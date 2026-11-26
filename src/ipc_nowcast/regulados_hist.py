"""Historia de precios regulados o de lista (tarifas, transporte, cigarrillos...) a partir de anuncios con fecha.

`data/precios/regulados/eventos.csv`: un aumento por fila (fecha de vigencia, ítem, componente INDEC, parte del
componente que representa, regiones, % de aumento, confianza, fuente). Son anuncios públicos anteriores o del mismo
día de la vigencia.

INDEC compara promedios de mes: un aumento del día 29 pega casi entero en el mes siguiente. Por eso cada ítem se
convierte en un precio diario y se toma la variación del promedio mensual. Con un `corte` (día del mes), del mes en
curso solo cuentan los aumentos vigentes hasta ese día (lo que se sabía), y el resto del mes se completa con el último
precio conocido.
"""
from __future__ import annotations

import functools

import numpy as np
import pandas as pd

from . import DATA

RUTA = DATA / "precios" / "regulados" / "eventos.csv"
REGIONES = ["GBA", "Pampeana", "Noreste", "Noroeste", "Cuyo", "Patagonia"]
DESDE = pd.Timestamp("2024-07-01")  # desde cuándo está reconstruida la historia (antes: sin dato, no "sin aumento")


@functools.lru_cache(maxsize=1)
def eventos() -> pd.DataFrame:
    if not RUTA.exists():
        return pd.DataFrame()
    e = pd.read_csv(RUTA, parse_dates=["fecha"], dtype={"componente": str})
    e["clave"] = e.item.str.split("(").str[0].str.strip()
    return e


def _variacion_item(g: pd.DataFrame, corte: int | None) -> pd.Series:
    # el ítem existe desde el comienzo del calendario: sin eventos, su precio no cambió
    inicio = min(g.fecha.min() - pd.offsets.MonthBegin(2), DESDE - pd.offsets.MonthBegin(1))
    dias = pd.date_range(inicio, pd.Timestamp.today().normalize() + pd.offsets.MonthEnd(1))
    p = pd.Series(1.0, index=dias)
    for f in g.itertuples():
        p[p.index >= f.fecha] *= 1 + f.aumento / 100
    meses = p.index.to_period("M")
    prom = p.groupby(meses).mean()
    out = (prom / prom.shift(1) - 1) * 100
    if corte:  # mes en curso: precio de cada día = el vigente al corte (aumentos posteriores no se conocen)
        parcial = {}
        for m in prom.index[1:]:
            d = p[meses == m]
            corte_d = min(corte, len(d))
            conocido = d.iloc[:corte_d]
            relleno = pd.Series(conocido.iloc[-1], index=d.index[corte_d:])
            parcial[m] = (pd.concat([conocido, relleno]).mean() / prom[m - 1] - 1) * 100
        out = pd.Series(parcial)
    out.index = out.index.to_timestamp()
    return out[out.index >= DESDE]


@functools.lru_cache(maxsize=8)
def variaciones(corte: int | None = None) -> pd.DataFrame:
    """Variación % mensual de la parte cubierta de cada componente, por región. Columnas: (región, componente);
    además `parte` total cubierta en `partes` (dict)."""
    e = eventos()
    if e.empty:
        return pd.DataFrame()
    cols = {}
    for (comp, clave), g in e.groupby(["componente", "clave"]):
        v = _variacion_item(g, corte)
        parte = float(g.parte.iloc[0])
        regs = REGIONES if str(g.regiones.iloc[0]).strip() == "todas" else [r.strip() for r in str(g.regiones.iloc[0]).split(";")]
        for r in regs:
            cols.setdefault((r, comp), []).append((parte, v))
    out = {}
    for k, items in cols.items():
        tot = sum(p for p, _ in items)
        out[k] = sum(p * v for p, v in items) / tot
        out[k].attrs["parte"] = tot
    return pd.DataFrame(out)


def partes() -> dict:
    """Parte de cada (región, componente) que cubren los ítems con historia."""
    e = eventos()
    res = {}
    for (comp, clave), g in e.groupby(["componente", "clave"]):
        regs = REGIONES if str(g.regiones.iloc[0]).strip() == "todas" else [r.strip() for r in str(g.regiones.iloc[0]).split(";")]
        for r in regs:
            res[(r, comp)] = res.get((r, comp), 0.0) + float(g.parte.iloc[0])
    return res
