"""Otros indicadores adelantados: precio de los combustibles y tipo de cambio.

- Combustibles: tabla mensual de precios de YPF en la Ciudad de Buenos Aires que publica surtidores.com.ar
  (nafta súper, premium y gasoil; historia desde 2018). El valor de cada mes es el precio vigente en ese mes
  (para el mes en curso, el de hoy). Además se guarda una foto diaria para ver cambios dentro del mes.
  El dataset oficial de precios en surtidor (Secretaría de Energía) está caído desde hace meses.
- Tipo de cambio: dólar mayorista de referencia (Comunicación A 3500) de la API pública del BCRA, diario.
"""
from __future__ import annotations

import json
import re
import subprocess
import urllib.request
from datetime import date

import numpy as np
import pandas as pd

from . import DATA

DIR_COMB = DATA / "precios" / "combustibles"
DIR_FX = DATA / "precios" / "cambio"
URL_SURTIDORES = "https://surtidores.com.ar/precios/"
URL_BCRA = "https://api.bcra.gob.ar/estadisticas/v4.0/monetarias/5?desde={a}&hasta={b}&limit=3000"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"
PRODUCTOS = ("Super", "Premium", "Gasoil", "Euro")
DESDE_NAFTA = "2024-01-01"  # antes hay huecos en la tabla y un régimen de inflación muy distinto


# ------------------------------------------------------------------ combustibles
def parsear_tabla_surtidores(html: str) -> pd.DataFrame:
    t = re.sub(r"\s+", " ", re.sub("<[^>]+>", "|", re.sub(r"<script.*?</script>|<style.*?</style>", "", html, flags=re.S)))
    c = re.sub(r"(\|\s*)+", "|", t).split("|")
    filas, i = [], 0
    while i < len(c):
        if re.fullmatch(r"20\d\d", c[i]) and i + 13 < len(c) and c[i + 1] == "Enero":
            anio, j = int(c[i]), i + 13
            while j < len(c) and c[j] in PRODUCTOS:
                prod, vals, k = c[j], [], j + 1
                while k < len(c) and re.fullmatch(r"[\d\.,]+", c[k]) and len(vals) < 12 and not (k + 1 < len(c) and c[k + 1] == "Enero"):
                    vals.append(float(c[k].replace(".", "").replace(",", ".")))
                    k += 1
                filas += [{"anio": anio, "mes": m + 1, "producto": prod, "precio": v} for m, v in enumerate(vals)]
                j = k
            i = j
        else:
            i += 1
    return pd.DataFrame(filas)


def actualizar_combustibles() -> pd.DataFrame:
    html = subprocess.run(["curl", "-sSL", "--retry", "3", "--max-time", "60", "-A", UA, URL_SURTIDORES],
                          capture_output=True, check=True).stdout.decode("utf-8", "ignore")
    t = parsear_tabla_surtidores(html)
    if t.empty:
        raise RuntimeError("no se encontró la tabla de precios")
    DIR_COMB.mkdir(parents=True, exist_ok=True)
    t.sort_values(["anio", "mes", "producto"]).to_csv(DIR_COMB / "ypf_caba_mensual.csv", index=False)
    # foto del día (precio vigente del mes en curso)
    hoy = date.today()
    foto = t[(t.anio == hoy.year) & (t.mes == hoy.month)].assign(fecha=str(hoy))[["fecha", "producto", "precio"]]
    ruta = DIR_COMB / "ypf_caba_diario.csv"
    prev = pd.read_csv(ruta) if ruta.exists() else pd.DataFrame(columns=["fecha", "producto", "precio"])
    pd.concat([prev[prev.fecha != str(hoy)], foto]).to_csv(ruta, index=False)
    return t


def serie_nafta() -> pd.Series:
    """Variación % mensual del precio de los combustibles (media geométrica de súper, premium y gasoil)."""
    ruta = DIR_COMB / "ypf_caba_mensual.csv"
    if not ruta.exists():
        return pd.Series(dtype=float)
    t = pd.read_csv(ruta)
    t = t[t.producto.isin(["Super", "Premium", "Gasoil"]) & (t.precio > 0)]
    t["f"] = pd.to_datetime(dict(year=t.anio, month=t.mes, day=1))
    p = t.groupby("f").precio.apply(lambda x: float(np.exp(np.log(x).mean()))).sort_index()
    v = (p.pct_change() * 100).rename("nafta")
    v = v[v.index >= pd.Timestamp(DESDE_NAFTA)]
    return v[(v > -50) & (v < 100)]


# ------------------------------------------------------------------ tipo de cambio
def actualizar_dolar(desde: str = "2016-12-01") -> pd.DataFrame:
    ruta = DIR_FX / "a3500.csv"
    prev = pd.read_csv(ruta) if ruta.exists() else pd.DataFrame(columns=["fecha", "valor"])
    ini = (pd.Timestamp(prev.fecha.max()) - pd.Timedelta(days=10)).strftime("%Y-%m-%d") if len(prev) else desde
    filas = []
    for a, b in [(p.start_time, p.end_time) for p in pd.period_range(ini, date.today(), freq="Y")]:
        a = max(a, pd.Timestamp(ini))
        req = urllib.request.Request(URL_BCRA.format(a=a.strftime("%Y-%m-%d"), b=b.strftime("%Y-%m-%d")), headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=60) as r:
            d = json.load(r)
        for res in d.get("results", []):
            filas += res.get("detalle", [])
    nuevo = pd.DataFrame(filas)
    todo = pd.concat([prev, nuevo]).drop_duplicates("fecha", keep="last").sort_values("fecha") if len(nuevo) else prev
    DIR_FX.mkdir(parents=True, exist_ok=True)
    todo.to_csv(ruta, index=False)
    return todo


def serie_dolar(corte: int | None = None) -> pd.Series:
    """Variación % del promedio mensual del dólar mayorista (el mes, hasta el día `corte`, contra el mes anterior completo)."""
    ruta = DIR_FX / "a3500.csv"
    if not ruta.exists():
        return pd.Series(dtype=float)
    d = pd.read_csv(ruta, parse_dates=["fecha"])
    d["mes"] = d.fecha.dt.to_period("M").dt.to_timestamp()
    completo = d.groupby("mes").valor.mean()
    actual = d[d.fecha.dt.day <= corte].groupby("mes").valor.mean() if corte else completo
    return ((actual / completo.shift(1).reindex(actual.index) - 1) * 100).dropna().rename("fx")
