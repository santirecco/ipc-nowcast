"""Otros indicadores adelantados: precio de los combustibles y tipo de cambio.

- Combustibles: tabla mensual de precios de YPF en la Ciudad de Buenos Aires que publica surtidores.com.ar
  (nafta súper, premium y gasoil; historia desde 2018). El valor de cada mes es el precio vigente en ese mes
  (para el mes en curso, el de hoy). Además se guarda una foto diaria para ver cambios dentro del mes.
  El dataset oficial de precios en surtidor (Secretaría de Energía) está caído desde hace meses.
- Tipo de cambio: dólar mayorista de referencia (Comunicación A 3500) de la API pública del BCRA, diario.
"""
from __future__ import annotations

import functools
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


def serie_nafta_promedio(corte: int | None = None) -> pd.Series:
    """Variación % del precio PROMEDIO del mes (lo que compara INDEC): precio de cada día = el de la última foto
    disponible (copias del archivo web hacia atrás, foto diaria propia desde nov-2026); promedio de los días hasta
    `corte` del mes contra el promedio del mes anterior completo."""
    partes = []
    for nombre in ("ypf_caba_wayback.csv", "ypf_caba_diario.csv"):
        ruta = DIR_COMB / nombre
        if ruta.exists():
            partes.append(pd.read_csv(ruta, parse_dates=["fecha"])[["fecha", "producto", "precio"]])
    if not partes:
        return pd.Series(dtype=float)
    t = pd.concat(partes)
    t = t[t.producto.isin(["Super", "Premium", "Gasoil"]) & (t.precio > 0)]
    if t.empty:
        return pd.Series(dtype=float)
    foto = t.groupby("fecha").precio.apply(lambda x: float(np.exp(np.log(x).mean()))).sort_index()
    dias = pd.date_range(foto.index.min(), foto.index.max(), freq="D")
    gap = pd.Series(foto.index, index=foto.index).reindex(dias).ffill()
    dia = foto.reindex(dias).ffill()
    dia = dia[(dia.index - gap).dt.days <= 10]  # sin foto en más de 10 días: no se inventa
    mes = dia.index.to_period("M").to_timestamp()
    n = dia.groupby(mes).size()
    completo = dia.groupby(mes).mean()[n >= 25]
    sel = dia.index.day <= corte if corte else np.ones(len(dia), bool)
    actual = dia[sel].groupby(mes[sel]).mean()
    if corte:
        actual = actual[dia[sel].groupby(mes[sel]).size() >= corte - 3]
    else:
        actual = completo
    return ((actual / completo.shift(1, freq="MS").reindex(actual.index) - 1) * 100).dropna().rename("naftap")


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


# ------------------------------------------------------------------ alquileres: ICL del BCRA
URL_ICL = "https://api.bcra.gob.ar/estadisticas/v4.0/monetarias/40?desde={a}&hasta={b}&limit=3000"


def actualizar_icl() -> pd.DataFrame:
    """Índice para Contratos de Locación (BCRA, diario, se conoce por adelantado)."""
    ruta = DATA / "precios" / "alquileres" / "icl.csv"
    ruta.parent.mkdir(parents=True, exist_ok=True)
    filas = []
    hoy = pd.Timestamp.today().normalize()
    a = pd.Timestamp("2020-07-01")
    while a <= hoy + pd.Timedelta(days=40):
        b = min(a + pd.Timedelta(days=2500), hoy + pd.Timedelta(days=40))
        raw = subprocess.run(["curl", "-sS", "--retry", "3", "--max-time", "90", URL_ICL.format(a=a.date(), b=b.date())],
                             capture_output=True, check=True).stdout
        for r in json.loads(raw)["results"]:
            for x in r.get("detalle", []):
                filas.append({"fecha": x["fecha"], "icl": x["valor"]})
        a = b + pd.Timedelta(days=1)
    t = pd.DataFrame(filas).drop_duplicates("fecha").sort_values("fecha")
    t.to_csv(ruta, index=False)
    return t


def serie_icl() -> pd.DataFrame:
    """Por mes: aumento anual del ICL repartido en 12 (contratos que ajustan ese mes) y variación mensual, en %."""
    ruta = DATA / "precios" / "alquileres" / "icl.csv"
    if not ruta.exists():
        return pd.DataFrame(columns=["icl_a", "icl_m"])
    t = pd.read_csv(ruta, parse_dates=["fecha"]).set_index("fecha").icl
    ini = t.resample("MS").first()  # valor del primer día del mes (lo que usan los contratos que ajustan ese mes)
    prom = t.resample("MS").mean()
    return pd.DataFrame({"icl_a": (ini / ini.shift(12) - 1) * 100 / 12, "icl_m": (prom / prom.shift(1) - 1) * 100})


# ------------------------------------------------------------------ salarios (INDEC, empleo registrado)
SERIE_SALARIOS = {"salarios": "149.1_TL_REGIADO_OCTU_0_16", "ripte": "158.1_REPTE_0_0_5"}
REZAGO_SALARIOS = 4  # se publican con ~4 meses de atraso: en el mes m solo se usa hasta m-4


def actualizar_salarios() -> pd.DataFrame:
    from .fuentes import series
    t = series(SERIE_SALARIOS)
    ruta = DATA / "precios" / "salarios" / "salarios.csv"
    ruta.parent.mkdir(parents=True, exist_ok=True)
    t.to_csv(ruta)
    return t


def serie_salarios() -> pd.DataFrame:
    """Por mes m: suba mensual promedio de los salarios registrados en m-6..m-4 (lo publicado al empezar m), en %."""
    ruta = DATA / "precios" / "salarios" / "salarios.csv"
    if not ruta.exists():
        return pd.DataFrame(columns=["sal"])
    t = pd.read_csv(ruta, index_col=0, parse_dates=True)
    v = t["salarios"].pct_change() * 100
    sal = v.rolling(3).mean().shift(REZAGO_SALARIOS, freq="MS")
    return pd.DataFrame({"sal": sal})


DIR_WAYBACK = DATA / "precios" / "wayback"
RUBRO_TIENDA = {"tascani": "ropa", "levis": "ropa", "portsaid": "ropa", "equus": "ropa",
                "coppel": "electro", "naldo": "electro", "pardo": "electro", "cetrogar": "electro"}
MIN_PARES_TIENDA = 10   # productos comparables mínimos por tienda y mes


def _efectos_mes(y, prod, mes, iters=60):
    """Índice de ventas repetidas: log precio = efecto del producto + efecto del mes (mínimos cuadrados por
    proyecciones alternadas). Devuelve el efecto de cada mes (Series), o vacío."""
    d = pd.DataFrame({"y": y, "p": prod, "m": mes})
    for _ in range(2):  # segunda pasada sin los saltos de más del doble (cambio de variante o mala lectura)
        em = pd.Series(0.0, index=sorted(d.m.unique()))
        for _ in range(iters):
            ap = (d.y - d.m.map(em)).groupby(d.p).mean()
            em = (d.y - d.p.map(ap)).groupby(d.m).mean()
        res = d.y - d.p.map(ap) - d.m.map(em)
        d = d[res.abs() < np.log(2) / 2]
    return em


@functools.lru_cache(maxsize=8)
def serie_tiendas(corte: int | None = None) -> pd.DataFrame:
    """Variación % mensual de precios publicados en tiendas online (copias del archivo web), por rubro.

    En el archivo el mismo producto casi nunca aparece en meses seguidos: índice de ventas repetidas por tienda
    (efecto producto + efecto mes), promedio simple entre tiendas del rubro. Sin mirar el futuro: la variación del
    mes m se estima solo con copias hasta ese mes (y con `corte`, del mes m solo las de hasta ese día).
    Columnas: ropa, ropa_l1, electro, electro_l1 (l1 = variación del mes anterior, con meses completos)."""
    if not DIR_WAYBACK.exists():
        return pd.DataFrame()
    por_rubro = {}
    for ruta in sorted(DIR_WAYBACK.glob("*.csv")):
        rubro = RUBRO_TIENDA.get(ruta.stem)
        if rubro is None:
            continue
        t = pd.read_csv(ruta, dtype={"mes": str, "timestamp": str})
        t = t[pd.to_numeric(t.precio, errors="coerce") > 0].copy()
        if t.empty:
            continue
        t["y"] = np.log(t.precio.astype(float))
        t["dia"] = t.timestamp.str[6:8].astype(int)
        t["mes"] = pd.to_datetime(t.mes + "01")
        t = t.sort_values("timestamp").drop_duplicates(["url", "mes"], keep="last")
        meses = sorted(t.mes.unique())

        def var(m, dia_max):
            d = t[(t.mes < m) | ((t.mes == m) & (t.dia <= dia_max))]
            ant = m - pd.offsets.MonthBegin(1)
            vistos = set(d[d.mes < m].url)
            n_m = d[(d.mes == m) & d.url.isin(vistos)].shape[0]
            if ant not in set(d.mes) or n_m < MIN_PARES_TIENDA:
                return np.nan
            d = d[d.url.map(d.url.value_counts()) >= 2]
            em = _efectos_mes(d.y.values, d.url.values, d.mes.values)
            if m not in em.index or ant not in em.index:
                return np.nan
            return float(np.exp(em[m] - em[ant]) - 1) * 100

        cur = pd.Series({m: var(m, corte or 31) for m in meses}, dtype=float)
        full = cur if not corte else pd.Series({m: var(m, 31) for m in meses}, dtype=float)
        por_rubro.setdefault(rubro, []).append((cur, full))
    out = pd.DataFrame()
    for rubro, partes in por_rubro.items():
        cur = pd.concat([p[0] for p in partes], axis=1).mean(axis=1)
        full = pd.concat([p[1] for p in partes], axis=1).mean(axis=1)
        o = pd.DataFrame({rubro: cur, rubro + "_l1": full.shift(1, freq="MS")})
        out = o if out.empty else out.join(o, how="outer")
    return out.sort_index()
