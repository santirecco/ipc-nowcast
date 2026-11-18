"""Precios mayoristas que anticipan a los minoristas: verduras y frutas (Mercado Central de Buenos Aires)
y hacienda (Mercado Agroganadero de Cañuelas, ex Liniers).

- Mercado Central publica un archivo por día hábil con el precio de cada especie (mínimo, modal y máximo por kg).
  Se usa el precio modal promedio de cada especie ("Prom.Esp.") y se arma un índice ponderado de las especies que
  más pesan en el IPC. La historia diaria disponible arranca en enero de 2026.
- El Mercado Agroganadero publica precios por categoría para cualquier rango de fechas (historia desde 2017).
  Se usa el promedio de novillitos y vaquillonas (la hacienda de consumo), ponderado por kilos.
"""
from __future__ import annotations

import io
import re
import struct
import subprocess
import zipfile
from datetime import date

import numpy as np
import pandas as pd

from . import DATA

DIR = DATA / "precios" / "mayoristas"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"
MC_PAGINA = "https://mercadocentral.gob.ar/informacion/precios-mayoristas"
HACIENDA_URL = ("https://www.mercadoagroganadero.com.ar/dll/hacienda1.dll/haciinfo000002"
                "?txtFECHAINI={a}&txtFECHAFIN={b}&CP=&LISTADO=SI")

# Ponderaciones aproximadas dentro de cada grupo (participación en el gasto de los hogares; se ajustan solas
# en la calibración, que estima cuánto del movimiento mayorista pasa al precio minorista).
PESOS_VERDURAS = {"PAPA": .24, "TOMATE": .22, "CEBOLLA": .12, "LECHUGA": .10, "ZANAHORIA": .06, "ZAPALLO": .06,
                  "ACELGA": .04, "ZAPALLITO": .04, "PIMIENTO": .04, "BATATA": .03, "ESPINACA": .02, "CHOCLO": .02,
                  "BERENJENA": .01}
PESOS_FRUTAS = {"BANANA": .28, "MANZANA": .22, "NARANJA": .18, "MANDARINA": .10, "PERA": .06, "LIMON": .06,
                "FRUTILLA": .03, "DURAZNO": .03, "UVA": .02, "POMELO": .02}


def _get(url: str) -> bytes:
    return subprocess.run(["curl", "-sSL", "--retry", "3", "--max-time", "120", "-A", UA, url],
                          capture_output=True, check=True).stdout


# ------------------------------------------------------------------ Mercado Central
def leer_biff2(data: bytes) -> list[list]:
    """Lee planillas Excel muy viejas (formato BIFF2, como las que publica el Mercado Central)."""
    i, celdas = 0, {}
    while i + 4 <= len(data):
        rid, ln = struct.unpack_from("<HH", data, i)
        d = data[i + 4:i + 4 + ln]
        i += 4 + ln
        if rid == 0x0004 and ln >= 8:
            r, c = struct.unpack_from("<HH", d, 0)
            celdas[(r, c)] = d[8:8 + d[7]].decode("latin-1").strip()
        elif rid == 0x0003 and ln >= 15:
            r, c = struct.unpack_from("<HH", d, 0)
            celdas[(r, c)] = struct.unpack_from("<d", d, 7)[0]
        elif rid == 0x0002 and ln >= 9:
            r, c = struct.unpack_from("<HH", d, 0)
            celdas[(r, c)] = struct.unpack_from("<H", d, 7)[0]
        elif rid == 0x000A:
            break
    if not celdas:
        return []
    nr, nc = max(r for r, _ in celdas) + 1, max(c for _, c in celdas) + 1
    return [[celdas.get((r, c)) for c in range(nc)] for r in range(nr)]


def _parsear_dia(data: bytes, nombre: str, tipo: str) -> pd.DataFrame:
    m = re.search(r"(\d\d)(\d\d)(\d\d)\.XLS$", nombre.upper())
    filas = leer_biff2(data) if m else []
    if not filas:
        return pd.DataFrame()
    cab = [str(x) for x in filas[0]]
    df = pd.DataFrame(filas[1:], columns=cab)
    mo = [c for c in cab if c.startswith("MOPK")]
    if not mo or "VAR" not in df:
        return pd.DataFrame()
    p = df[df.VAR.astype(str).str.contains("Prom.Esp", na=False)][["ESP", mo[0]]]
    p.columns = ["especie", "precio_kg"]
    p["fecha"] = f"20{m[3]}-{m[2]}-{m[1]}"
    p["tipo"] = tipo
    return p[p.precio_kg > 0]


def actualizar_mercado_central(todos: bool = False) -> pd.DataFrame:
    """Baja los archivos mensuales publicados (por defecto, solo el mes en curso y el anterior)."""
    ruta = DIR / "mercado_central.csv"
    previo = pd.read_csv(ruta) if ruta.exists() else pd.DataFrame(columns=["fecha", "tipo", "especie", "precio_kg"])
    html = _get(MC_PAGINA).decode("utf-8", "ignore")
    links = sorted(set(re.findall(r'https?://[^"\']+/precios_mayoristas/[^"\']+\.zip', html)))
    hoy = pd.Timestamp(date.today())
    recientes = {f"{m:%m}" for m in [hoy, hoy - pd.offsets.MonthBegin(1)]}
    meses_txt = {"01": "ENERO", "02": "FEBRERO", "03": "MARZO", "04": "ABRIL", "05": "MAYO", "06": "JUNIO", "07": "JULIO",
                 "08": "AGOSTO", "09": "SEPTI|SETI|SEPTIEN", "10": "OCTUBRE", "11": "NOVIEMBRE", "12": "DICIEMBRE"}
    nuevos = []
    for u in links:
        nombre = u.rsplit("/", 1)[-1].upper()
        if not todos and not any(re.search(meses_txt[m], nombre) for m in recientes):
            continue
        tipo = "frutas" if "FRUT" in nombre else "hortalizas"
        try:
            z = zipfile.ZipFile(io.BytesIO(_get(u)))
        except Exception:
            continue
        for n in z.namelist():
            d = _parsear_dia(z.read(n), n, tipo)
            if not d.empty:
                nuevos.append(d)
    if not nuevos:
        return previo
    todo = pd.concat([previo] + nuevos, ignore_index=True)
    todo = todo.drop_duplicates(["fecha", "tipo", "especie"], keep="last").sort_values(["fecha", "tipo", "especie"])
    DIR.mkdir(parents=True, exist_ok=True)
    todo.to_csv(ruta, index=False, float_format="%.2f")
    return todo


def _indice(m: pd.DataFrame, pesos: dict) -> pd.Series:
    sub = m.loc[[k for k in pesos if k in m.index]]
    r = np.log(sub / sub.shift(axis=1))
    w = pd.Series(pesos).reindex(sub.index)
    return (np.exp(r.mul(w, axis=0).sum() / r.notna().mul(w, axis=0).sum()) - 1) * 100


def indices_mercado_central(corte: int | None = None) -> pd.DataFrame:
    """Variación % mensual mayorista de verduras y frutas (promedio del mes vs. promedio del mes anterior).
    Con `corte`, el último mes usa solo los días hasta ese día."""
    ruta = DIR / "mercado_central.csv"
    if not ruta.exists():
        return pd.DataFrame()
    d = pd.read_csv(ruta)
    d["mes"] = d.fecha.str[:7]
    if corte is not None:
        ult = d.mes.max()
        d = d[(d.mes != ult) | (d.fecha.str[8:10].astype(int) <= corte)]
    m = d.groupby(["tipo", "especie", "mes"]).precio_kg.mean().unstack("mes")
    out = pd.DataFrame({"01.1.7": _indice(m.xs("hortalizas"), PESOS_VERDURAS),
                        "01.1.6": _indice(m.xs("frutas"), PESOS_FRUTAS)})
    out.index = pd.to_datetime(out.index + "-01")
    out["dias"] = d.groupby("mes").fecha.nunique().set_axis(pd.to_datetime(d.groupby("mes").fecha.nunique().index + "-01"))
    return out.iloc[1:]


# ------------------------------------------------------------------ Hacienda
def _num(x: str) -> float:
    return float(x.replace(".", "").replace(",", ".").replace("$", ""))


def consultar_hacienda(desde: pd.Timestamp, hasta: pd.Timestamp) -> pd.DataFrame:
    s = _get(HACIENDA_URL.format(a=desde.strftime("%d/%m/%Y"), b=hasta.strftime("%d/%m/%Y"))).decode("latin-1")
    t = re.sub(r"\s+", " ", re.sub(r"<script.*?</script>|<style.*?</style>", "", s, flags=re.S))
    cel = [c.strip() for c in re.sub(r"(\|\s*)+", "|", re.sub("<[^>]+>", "|", t)).split("|")]
    filas = []
    for i, c in enumerate(cel):
        if re.match(r"^(NOVILLOS|NOVILLITOS|VAQUILLONAS|VACAS|TOROS|MEJ)\b", c) and i + 8 < len(cel):
            try:
                filas.append({"categoria": c, "promedio": _num(cel[i + 3]), "cabezas": _num(cel[i + 5]), "kgs": _num(cel[i + 7])})
            except ValueError:
                pass
    return pd.DataFrame(filas)


def actualizar_hacienda(desde: str | None = None) -> pd.DataFrame:
    """Promedios mensuales por categoría. Por defecto refresca el mes en curso y el anterior."""
    ruta = DIR / "hacienda.csv"
    previo = pd.read_csv(ruta) if ruta.exists() else pd.DataFrame()
    hoy = pd.Timestamp(date.today())
    ini = pd.Period(desde, "M") if desde else (pd.Period(hoy, "M") - 1)
    nuevos = []
    for per in pd.period_range(ini, pd.Period(hoy, "M"), freq="M"):
        fin = min(per.end_time.normalize(), hoy)
        d = consultar_hacienda(per.start_time, fin)
        if d.empty:
            continue
        d["mes"], d["hasta"] = str(per), f"{fin:%Y-%m-%d}"
        nuevos.append(d)
    if not nuevos:
        return previo
    nuevos = pd.concat(nuevos)
    todo = pd.concat([previo[~previo.mes.isin(nuevos.mes.unique())] if not previo.empty else previo, nuevos])
    DIR.mkdir(parents=True, exist_ok=True)
    todo.sort_values(["mes", "categoria"]).to_csv(ruta, index=False)
    # primera quincena del mes en curso (para calibrar el pronóstico de mitad de mes)
    if hoy.day >= 15:
        rq = DIR / "hacienda_quincena.csv"
        q = pd.read_csv(rq) if rq.exists() else pd.DataFrame()
        ini = hoy.replace(day=1)
        d = consultar_hacienda(ini, ini + pd.Timedelta(days=14))
        if not d.empty:
            d["mes"] = f"{hoy:%Y-%m}"
            q = pd.concat([q[q.mes != d.mes.iloc[0]] if not q.empty else q, d])
            q.sort_values(["mes", "categoria"]).to_csv(rq, index=False)
    return todo


def indice_hacienda() -> pd.Series:
    """Variación % mensual del precio de la hacienda de consumo (novillitos y vaquillonas, ponderado por kilos)."""
    ruta = DIR / "hacienda.csv"
    if not ruta.exists():
        return pd.Series(dtype=float)
    h = pd.read_csv(ruta)
    h = h[h.categoria.str.match(r"NOVILLITOS|VAQUILLONAS")]
    p = h.groupby("mes").apply(lambda g: np.average(g.promedio, weights=g.kgs), include_groups=False)
    p.index = pd.to_datetime(p.index + "-01")
    return (p.pct_change() * 100).dropna().rename("01.1.2")


# ------------------------------------------------------------------ series para la calibración
def serie_mercado_central(corte: int | None = None) -> pd.DataFrame:
    """Para cada mes: variación mayorista (verduras 01.1.7 y frutas 01.1.6) del promedio de los días del mes
    hasta `corte` contra el promedio del mes anterior completo."""
    ruta = DIR / "mercado_central.csv"
    if not ruta.exists():
        return pd.DataFrame()
    d = pd.read_csv(ruta)
    d["mes"] = d.fecha.str[:7]
    d["dia"] = d.fecha.str[8:10].astype(int)
    completo = d.groupby(["tipo", "especie", "mes"]).precio_kg.mean().unstack("mes")
    parcial = (d[d.dia <= corte] if corte else d).groupby(["tipo", "especie", "mes"]).precio_kg.mean().unstack("mes")
    filas = []
    meses = sorted(d.mes.unique())
    for ant, act in zip(meses[:-1], meses[1:]):
        if act not in parcial:
            continue
        fila = {"mes": pd.Timestamp(act + "-01"), "dias": int(d[(d.mes == act) & ((d.dia <= corte) if corte else True)].fecha.nunique())}
        for tipo, clase, pesos in [("hortalizas", "01.1.7", PESOS_VERDURAS), ("frutas", "01.1.6", PESOS_FRUTAS)]:
            m = pd.concat([completo[ant].xs(tipo), parcial[act].xs(tipo)], axis=1, keys=["a", "b"]).dropna()
            m = m.loc[[k for k in pesos if k in m.index]]
            if m.empty:
                continue
            w = pd.Series(pesos).reindex(m.index)
            fila[clase] = (np.exp((np.log(m.b / m.a) * w).sum() / w.sum()) - 1) * 100
        filas.append(fila)
    return pd.DataFrame(filas).set_index("mes")


def _precio_consumo(h: pd.DataFrame) -> pd.Series:
    h = h[h.categoria.str.match(r"NOVILLITOS|VAQUILLONAS")]
    p = h.groupby("mes").apply(lambda g: np.average(g.promedio, weights=g.kgs), include_groups=False)
    p.index = pd.to_datetime(p.index + "-01")
    return p


def serie_hacienda(corte: int | None = None) -> pd.Series:
    """Variación % del precio de la hacienda de consumo: mes (completo o primera quincena) vs. mes anterior completo."""
    ruta = DIR / "hacienda.csv"
    if not ruta.exists():
        return pd.Series(dtype=float)
    completo = _precio_consumo(pd.read_csv(ruta))
    if corte:
        rq = DIR / "hacienda_quincena.csv"
        if not rq.exists():
            return pd.Series(dtype=float)
        actual = _precio_consumo(pd.read_csv(rq))
    else:
        actual = completo
    ant = completo.shift(1, freq="MS")
    return ((actual / ant.reindex(actual.index) - 1) * 100).dropna().rename("01.1.2")
