"""Pesos por debajo de la división: grupos y clases que INDEC publica por región.

INDEC no publica las ponderaciones de grupos y clases, pero sí sus índices. Como el IPC es un Laspeyres,
el índice de una división es el promedio ponderado de sus componentes; los pesos se recuperan por
mínimos cuadrados no negativos sobre los niveles. Donde los grupos publicados no cubren toda la división,
se usa la cobertura del cuadro 26 y el resto se trata como un componente "no publicado" que se mueve
como la división.
"""
from __future__ import annotations

import pandas as pd
import yaml
from scipy.optimize import nnls

from . import CONFIG, REGIONES

# Hijos de cada nodo (división -> grupos; grupo -> clases). 06 y 07.2 incluyen clases publicadas sueltas.
HIJOS_DIVISION = {
    "01": ["01.1", "01.2"], "02": ["02.1", "02.2"], "03": ["03.1", "03.2"], "04": ["04.1", "04.5"],
    "05": ["05.6"], "06": ["06.1", "06.4.1"], "07": ["07.1", "07.2", "07.3"], "08": ["08.3"],
    "09": ["09.4", "09.5"], "10": [], "11": ["11.1"], "12": ["12.1"],
}
HIJOS_GRUPO = {
    "01.1": ["01.1.1", "01.1.2", "01.1.4", "01.1.5", "01.1.6", "01.1.7", "01.1.8"],
    "01.2": ["01.2.1", "01.2.2"],
    "04.1": ["04.1.1"],
    "07.2": ["07.2.2"],
}


def _nnls(X: pd.DataFrame, y: pd.Series):
    ok = X.notna().all(axis=1) & y.notna()
    w, _ = nnls(X[ok].values, y[ok].values)
    return pd.Series(w, index=X.columns)


def calibrar(aperturas: pd.DataFrame) -> pd.DataFrame:
    """Peso base (dic-16) de cada grupo/clase dentro de su padre, por región (fracciones)."""
    cob = yaml.safe_load((CONFIG / "cobertura_grupos.yaml").read_text(encoding="utf-8"))
    piv = aperturas.pivot_table(index="periodo", columns=["region", "codigo"], values="indice").sort_index()
    filas = []
    for r in REGIONES:
        I = piv[r]
        for d, hijos in HIJOS_DIVISION.items():
            hijos = [h for h in hijos if h in I.columns]
            if not hijos:
                continue
            c = cob[d][r] / 100
            w = _nnls(I[hijos], I[d] * c)
            if w.sum() > 0:
                w = w / w.sum() * c
            filas += [{"region": r, "padre": d, "codigo": h, "peso": float(w[h])} for h in hijos]
            if c < 0.999:
                filas.append({"region": r, "padre": d, "codigo": f"{d}.resto", "peso": 1 - c})
        for g, hijos in HIJOS_GRUPO.items():
            hijos = [h for h in hijos if h in I.columns]
            w = _nnls(I[hijos], I[g])
            s = w.sum()
            if s > 1:
                w, s = w / s, 1.0
            filas += [{"region": r, "padre": g, "codigo": h, "peso": float(w[h])} for h in hijos]
            if s < 0.999:
                filas.append({"region": r, "padre": g, "codigo": f"{g}.resto", "peso": 1 - s})
    return pd.DataFrame(filas)


def peso_efectivo_en_division(aperturas: pd.DataFrame, base: pd.DataFrame, periodo: pd.Timestamp,
                               piv: pd.DataFrame | None = None) -> pd.DataFrame:
    """Peso efectivo de cada grupo/clase dentro de su DIVISIÓN para el mes `periodo` (fracción)."""
    if piv is None:
        piv = aperturas.pivot_table(index="periodo", columns=["region", "codigo"], values="indice").sort_index()
    ant = piv.index[piv.index < periodo].max()
    filas = []
    for _, f in base.iterrows():
        r, padre, cod = f.region, f.padre, f.codigo
        division = padre[:2]
        if cod.endswith(".resto"):
            rel = 1.0
        else:
            rel = piv[r][cod].loc[ant] / piv[r][padre].loc[ant]
        filas.append({**f.to_dict(), "division": division, "peso_en_padre_ef": f.peso * rel})
    df = pd.DataFrame(filas)
    # normalizar dentro de cada padre y encadenar hasta la división
    df["peso_en_padre_ef"] = df["peso_en_padre_ef"] / df.groupby(["region", "padre"])["peso_en_padre_ef"].transform("sum")
    padres = df.set_index(["region", "codigo"])["peso_en_padre_ef"]
    def en_div(f):
        if len(f.padre) == 2:
            return f.peso_en_padre_ef
        return f.peso_en_padre_ef * padres.get((f.region, f.padre), float("nan"))
    df["peso_en_division_ef"] = df.apply(en_div, axis=1)
    return df
