"""Controles de las fuentes nuevas: clasificación de SEPA, índices por producto, mayoristas y calibración."""
import struct
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ipc_nowcast import DATA, adelantados, mayoristas, modelo, sepa  # noqa: E402
from ipc_nowcast.clasificador_sepa import clasificar  # noqa: E402


def test_clasificador_sepa():
    casos = {
        "LECHE ENTERA ULT PASTEUR RAMOLAC SACHET X 1 LT": "01.1.4",
        "SANCOR LECHE ENTERA": "01.1.4",
        "DULCE DE LECHE LA SERENISIMA 400G": "01.1.4",
        "TAPA DE NALGA NOVILLITO X KG": "01.1.2",
        "VACIO SC": "01.1.2",
        "FIDEOS TALLARIN LUCCHETTI 500G": "01.1.1",
        "PAN DE HAMBURGUESA X4": "01.1.1",
        "PAPA BLANCA X KG": "01.1.7",
        "PAPAS FRITAS LAYS 85G": "01.1.resto",
        "NARANJA DE OMBLIGO X KG": "01.1.6",
        "JUGO CEPITA NARANJA 1L": "01.2.2",
        "YERBA MATE TARAGUI 1KG": "01.2.1",
        "ACEITE GIRASOL NATURA 1.5L": "01.1.5",
        "VINO MALBEC 750 ML": "02.1",
        "CREMA F.NIVEA X100ML": None,
        "DET.MAGISTRAL X750ML LIMON": None,
        "SHAMPOO SEDAL 340ML": None,
    }
    for desc, esperado in casos.items():
        assert clasificar(desc) == esperado, desc


def test_variacion_sepa_un_producto():
    # dos cadenas, 25 productos cada una, todos suben 2% (cadena 1) y 4% (cadena 2): promedio simple entre cadenas
    filas_a, filas_b = [], []
    for c, sube in (("1", 1.02), ("2", 1.04)):
        for i in range(25):
            filas_a.append({"id_comercio": c, "region": "GBA", "id_producto": f"p{i}", "clase": "01.1.1", "p": 100.0 + i, "dias": 30})
            filas_b.append({"id_comercio": c, "region": "GBA", "id_producto": f"p{i}", "clase": "01.1.1", "p": (100.0 + i) * sube, "dias": 10})
    v = sepa.variacion(pd.DataFrame(filas_a), pd.DataFrame(filas_b))
    esperado = (np.exp((np.log(1.02) + np.log(1.04)) / 2) - 1) * 100
    assert len(v) == 1 and abs(v["var_%"].iloc[0] - esperado) < 1e-9 and v.cadenas.iloc[0] == 2


def test_variacion_descarta_saltos_y_pocos_productos():
    a = pd.DataFrame({"id_comercio": "1", "region": "GBA", "id_producto": [f"p{i}" for i in range(25)], "clase": "01.1.4",
                      "p": 100.0, "dias": 30})
    b = a.assign(p=[101.0] * 24 + [300.0], dias=10)  # un producto triplica (error de carga): se descarta
    v = sepa.variacion(a, b)
    assert abs(v["var_%"].iloc[0] - 1.0) < 1e-9
    assert sepa.variacion(a.iloc[:10], b.iloc[:10]).empty  # menos de 20 productos: la cadena no cuenta


def test_biff2():
    def rec(rid, data):
        return struct.pack("<HH", rid, len(data)) + data
    label = lambda r, c, s: rec(0x0004, struct.pack("<HH", r, c) + b"\x00\x00\x00" + bytes([len(s)]) + s.encode("latin-1"))
    num = lambda r, c, v: rec(0x0003, struct.pack("<HH", r, c) + b"\x00\x00\x00" + struct.pack("<d", v))
    datos = rec(0x0009, b"\x02\x00\x10\x00") + label(0, 0, "ESP") + label(1, 0, "PAPA") + num(1, 1, 450.5) + rec(0x000A, b"")
    assert mayoristas.leer_biff2(datos) == [["ESP", None], ["PAPA", 450.5]]


def test_ajuste_recupera_coeficiente():
    rng = np.random.default_rng(0)
    n = 200
    t = pd.DataFrame({"clase": "01.1.1", "proy": rng.normal(2, 0.5, n), "sepa": rng.normal(2, 1, n)})
    t["real"] = t.proy + 0.6 * (t.sepa - t.proy) + rng.normal(0, 0.05, n)
    b = adelantados._ajustar(t, ["sepa"])
    assert abs(b[0] - 0.6) < 0.05


def test_item_de_division_entera():
    d = pd.read_parquet(DATA / "processed" / "indec_divisiones.parquet")
    a = pd.read_parquet(DATA / "processed" / "indec_aperturas.parquet")
    nc = modelo.Nowcast(d, a, None)
    mes = d.periodo.max() + pd.offsets.MonthBegin(1)
    base, _ = nc.celdas(mes, usar_regulados=False, usar_super=False)
    extra = [{"region": "GBA", "componente": "10", "fuente": "prueba", "valor": 9.0, "parte": 0.5}]
    ajust, apl = nc.celdas(mes, usar_regulados=False, usar_super=False, extra=extra)
    assert len(apl) == 1
    assert abs(ajust[("GBA", "10")] - (0.5 * 9.0 + 0.5 * base[("GBA", "10")])) < 1e-9
