"""Controles del modelo de pronóstico y de la clasificación de productos."""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ipc_nowcast import DATA, modelo, supermercados  # noqa: E402


def test_clasificacion_basica():
    casos = {
        ("/Frutas y verduras/Verduras/", "Pepino x kg."): "01.1.7",
        ("/Desayuno y merienda/Galletitas bizcochitos y tostadas/Galletitas de agua/", "Criollitas"): "01.1.1",
        ("/Lácteos y productos frescos/Leches/Leches descremadas/", "Leche"): "01.1.4",
        ("/Almacén/Desayuno y Merienda/Yerbas/", "Yerba"): "01.2.1",
        ("/Bebidas/Vinos/Vinos tintos/", "Malbec"): "02.1",
        ("/Limpieza/Lavandinas/", "Lavandina"): "05.6",
        ("/Electro y tecnología/TV y soportes/", "Smart TV"): None,
    }
    for (cat, nom), esperado in casos.items():
        assert supermercados.clasificar(cat, nom) == esperado, (cat, nom)


def test_arrastre():
    m = pd.Timestamp("2026-11-01")
    assert modelo.impacto_en_mes(3.0, pd.Timestamp("2026-11-01").date(), m) == 3.0
    assert abs(modelo.impacto_en_mes(3.0, pd.Timestamp("2026-11-16").date(), m) - 1.5) < 1e-9
    assert abs(modelo.impacto_en_mes(3.0, pd.Timestamp("2026-10-17").date(), m) - 3.0 * 16 / 31) < 1e-9


def test_nowcast_razonable():
    d = pd.read_parquet(DATA / "processed" / "indec_divisiones.parquet")
    a = pd.read_parquet(DATA / "processed" / "indec_aperturas.parquet")
    nc = modelo.Nowcast(d, a, None)
    mes = d.periodo.max() + pd.offsets.MonthBegin(1)
    r = nc.calcular(mes)
    assert -2 < r["estimacion"] < 15
    assert abs(r["celdas"]["peso_%"].sum() - 100) < 1e-6
