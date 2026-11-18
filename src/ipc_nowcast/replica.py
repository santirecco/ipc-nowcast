"""Réplica exacta de la agregación del IPC de INDEC y pesos efectivos mes a mes.

Cómo agrega INDEC (verificado contra la serie publicada desde dic-2016):

* IPC regional = Laspeyres sobre las 12 divisiones de la región:
      I(gral,r,t) = sum_d w(d,r) * I(d,r,t)            (índices base dic-16 = 100)
  Lo mismo vale para las particiones Bienes/Servicios y Estacional/Núcleo/Regulados.
* IPC nacional = Laspeyres sobre los 6 niveles generales regionales:
      I(nac,t) = sum_r s(r) * I(gral,r,t)
* Cada división nacional = Laspeyres sobre esa misma división en las 6 regiones,
  con pesos regionales propios de la división: I(d,nac,t) = sum_r a(d,r) * I(d,r,t)

Los pesos publicados en el informe vienen redondeados a un decimal; acá se calibran
por mínimos cuadrados no negativos sobre los niveles, lo que reproduce la serie oficial
con error prácticamente nulo.

Peso efectivo (el que realmente pondera la variación del mes t):
      w_ef(i,t) = w(i) * I(i,t-1) / I(total,t-1)
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.optimize import nnls

from . import REGIONES

DIVISIONES = [f"{i:02d}" for i in range(1, 13)]
CATEGORIAS = ["Estacional", "Núcleo", "Regulados"]
BIENES_SERVICIOS = ["B", "S"]


def pivotear(df: pd.DataFrame) -> pd.DataFrame:
    """Formato ancho: filas = periodo, columnas = (region, codigo)."""
    return df.pivot_table(index="periodo", columns=["region", "codigo"], values="indice").sort_index()


def _calibrar(X: pd.DataFrame, y: pd.Series) -> pd.Series:
    ok = X.notna().all(axis=1) & y.notna()
    w, _ = nnls(X[ok].values, y[ok].values)
    return pd.Series(w, index=X.columns)


def calibrar(piv: pd.DataFrame) -> dict[str, pd.DataFrame | pd.Series]:
    """Pesos exactos (fracciones que suman ~1) para cada agregación de INDEC."""
    out = {
        "division_en_region": pd.DataFrame({r: _calibrar(piv[r][DIVISIONES], piv[r]["00"]) for r in REGIONES}),
        "categoria_en_region": pd.DataFrame({r: _calibrar(piv[r][CATEGORIAS], piv[r]["00"]) for r in REGIONES}),
        "bys_en_region": pd.DataFrame({r: _calibrar(piv[r][BIENES_SERVICIOS], piv[r]["00"]) for r in REGIONES}),
        "region_en_nacional": _calibrar(pd.DataFrame({r: piv[r]["00"] for r in REGIONES}), piv["Nacional"]["00"]),
    }
    out["region_en_division_nacional"] = pd.DataFrame(
        {d: _calibrar(pd.DataFrame({r: piv[r][d] for r in REGIONES}), piv["Nacional"][d]) for d in DIVISIONES}
    ).T
    return out


def _metricas(replica: pd.Series, publicado: pd.Series, nombre: str) -> dict:
    vm_r, vm_p = replica.pct_change() * 100, publicado.pct_change() * 100
    e = (vm_r - vm_p).dropna()
    return {
        "serie": nombre,
        "error_nivel_max_%": float(((replica / publicado - 1) * 100).abs().max()),
        "error_var_mensual_promedio_pp": float(e.abs().mean()),
        "error_var_mensual_max_pp": float(e.abs().max()),
        "meses_con_otra_decima": int((vm_r.round(1) != vm_p.round(1)).iloc[1:].sum()),
        "meses": int(e.size),
    }


def validar(piv: pd.DataFrame, pesos: dict) -> pd.DataFrame:
    filas = []
    for r in REGIONES:
        filas.append(_metricas((piv[r][DIVISIONES] * pesos["division_en_region"][r]).sum(axis=1), piv[r]["00"], f"{r}: general desde divisiones"))
        filas.append(_metricas((piv[r][CATEGORIAS] * pesos["categoria_en_region"][r]).sum(axis=1), piv[r]["00"], f"{r}: general desde categorías"))
    niv = pd.DataFrame({r: piv[r]["00"] for r in REGIONES})
    filas.append(_metricas((niv * pesos["region_en_nacional"]).sum(axis=1), piv["Nacional"]["00"], "Nacional: general desde regiones"))
    for d in DIVISIONES:
        X = pd.DataFrame({r: piv[r][d] for r in REGIONES})
        filas.append(_metricas((X * pesos["region_en_division_nacional"].loc[d]).sum(axis=1), piv["Nacional"][d], f"Nacional: división {d} desde regiones"))
    # Prueba de punta a punta: nacional reconstruido desde las 72 celdas región x división
    filas.append(_metricas(nacional_desde_celdas(piv, pesos), piv["Nacional"]["00"], "Nacional: general desde 72 celdas región x división"))
    return pd.DataFrame(filas)


def nacional_desde_celdas(piv: pd.DataFrame, pesos: dict) -> pd.Series:
    s = pesos["region_en_nacional"]
    w = pesos["division_en_region"]
    return sum(s[r] * (piv[r][DIVISIONES] * w[r]).sum(axis=1) for r in REGIONES)


def pesos_efectivos(piv: pd.DataFrame, pesos: dict) -> pd.DataFrame:
    """Peso efectivo de cada celda región x división en el mes t, dentro de su región y en el nacional.

    Columnas: periodo, region, division, peso_en_region_%, peso_region_en_nacional_%, peso_en_nacional_%
    """
    s = pesos["region_en_nacional"]
    w = pesos["division_en_region"]
    niv_nac = sum(s[r] * piv[r]["00"] for r in REGIONES)
    filas = []
    for r in REGIONES:
        ant_div = piv[r][DIVISIONES].shift(1)
        ant_gral = piv[r]["00"].shift(1)
        en_region = ant_div.mul(w[r], axis=1).div(ant_gral, axis=0) * 100
        region_en_nac = s[r] * ant_gral / niv_nac.shift(1) * 100
        larga = en_region.stack().rename("peso_en_region_%").reset_index()
        larga.columns = ["periodo", "division", "peso_en_region_%"]
        larga["region"] = r
        larga["peso_region_en_nacional_%"] = larga["periodo"].map(region_en_nac)
        filas.append(larga)
    out = pd.concat(filas, ignore_index=True).dropna()
    out["peso_en_nacional_%"] = out["peso_en_region_%"] * out["peso_region_en_nacional_%"] / 100
    return out[["periodo", "region", "division", "peso_en_region_%", "peso_region_en_nacional_%", "peso_en_nacional_%"]]


def descomponer_variacion(piv: pd.DataFrame, efectivos: pd.DataFrame) -> pd.DataFrame:
    """Incidencia (pp) de cada celda región x división en la variación mensual del nacional."""
    var = []
    for r in REGIONES:
        v = (piv[r][DIVISIONES].pct_change() * 100).stack().rename("var_%").reset_index()
        v.columns = ["periodo", "division", "var_%"]
        v["region"] = r
        var.append(v)
    out = efectivos.merge(pd.concat(var), on=["periodo", "region", "division"])
    out["incidencia_pp"] = out["peso_en_nacional_%"] * out["var_%"] / 100
    return out
