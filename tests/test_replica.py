"""Control: la réplica de INDEC tiene que seguir siendo exacta cada vez que se actualizan los datos.

Si INDEC cambia la metodología (por ejemplo, la canasta de la ENGHo 2017/18), este test falla y avisa.
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ipc_nowcast import DATA, REGIONES, replica  # noqa: E402


def _piv():
    return replica.pivotear(pd.read_parquet(DATA / "processed" / "indec_divisiones.parquet"))


def test_nacional_desde_72_celdas_es_exacto():
    piv = _piv()
    pesos = replica.calibrar(piv)
    rep = replica.nacional_desde_celdas(piv, pesos)
    pub = piv["Nacional"]["00"]
    assert ((rep / pub - 1).abs() * 100).max() < 0.01
    vm_r, vm_p = rep.pct_change() * 100, pub.pct_change() * 100
    assert (vm_r.round(1) != vm_p.round(1)).iloc[1:].sum() == 0


def test_pesos_suman_100():
    pesos = replica.calibrar(_piv())
    assert abs(pesos["region_en_nacional"].sum() - 1) < 1e-3
    for r in REGIONES:
        assert abs(pesos["division_en_region"][r].sum() - 1) < 1e-3


def test_pesos_efectivos_suman_100_cada_mes():
    piv = _piv()
    ef = replica.pesos_efectivos(piv, replica.calibrar(piv))
    tot = ef.groupby("periodo")["peso_en_nacional_%"].sum()
    assert (tot - 100).abs().max() < 0.05
