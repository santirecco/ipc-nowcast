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
    assert len([x for x in apl if x["componente"] == "10"]) == 1
    assert abs(ajust[("GBA", "10")] - (0.5 * 9.0 + 0.5 * base[("GBA", "10")])) < 1e-9


def test_tabla_surtidores():
    from ipc_nowcast import indicadores
    html = "<table><tr><td>2026</td><td>Enero</td>" + "".join(f"<td>{m}</td>" for m in ["Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]) + \
           "</tr><tr><td>Super</td><td>1566</td><td>1609</td></tr><tr><td>2025</td><td>Enero</td>" + "".join(f"<td>{m}</td>" for m in ["Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]) + \
           "</tr><tr><td>Super</td><td>1128</td></tr></table>"
    t = indicadores.parsear_tabla_surtidores(html)
    assert t[t.anio == 2026].precio.tolist() == [1566.0, 1609.0]
    assert t[t.anio == 2025].precio.tolist() == [1128.0]


def test_carne_fresca():
    from ipc_nowcast.clasificador_sepa import es_carne_fresca
    assert es_carne_fresca("BIFE ANCHO X KG") and es_carne_fresca("CUADRADA OFERTA")
    assert not es_carne_fresca("LOMO DE CERDO") and not es_carne_fresca("PALETA DE MAQUILLAJES") and not es_carne_fresca("HAMBURGUESA DE CARNE")


def test_regla_prepagas():
    d = pd.read_parquet(DATA / "processed" / "indec_divisiones.parquet")
    a = pd.read_parquet(DATA / "processed" / "indec_aperturas.parquet")
    nc = modelo.Nowcast(d, a, None)
    mes = d.periodo.max()  # un mes ya publicado: la regla usa el IPC de dos meses antes
    info = nc.informacion_del_mes(mes, usar_regulados=False, usar_super=False)
    prep = [it for it in info if it["componente"] == "06.4.1"]
    ipc = nc.V["Nacional"]["00"].loc[mes - pd.offsets.MonthBegin(2)]
    assert len(prep) == 6 and all(abs(it["valor"] - ipc) < 1e-9 for it in prep)


def test_k_caba_por_rubro():
    import numpy as np
    import pandas as pd
    from ipc_nowcast import modelo
    meses = pd.date_range("2025-01-01", periods=14, freq="MS")
    rng = np.random.default_rng(0)
    filas = []
    for m in meses:
        real = 2 + rng.normal(0, 0.5)
        # división 01: la Ciudad acierta; división 09: la Ciudad es ruido
        filas.append({"mes": m, "div": "01", "var": real + 0.8, "real_div": real, "caba": real})
        filas.append({"mes": m, "div": "09", "var": real, "real_div": real, "caba": real + rng.normal(0, 2)})
    k = modelo.estimar_k_caba(pd.DataFrame(filas))
    assert k["01"] == 1.0 and k["09"] == 0.0
    assert modelo.estimar_k_caba(pd.DataFrame(filas[:10])) is None  # menos de 12 meses


def test_calendario_y_senal_no_se_cuentan_dos_veces(monkeypatch):
    """Si el calendario anuncia el 70% de combustibles, el precio de surtidor cubre solo el 30% restante."""
    nc = object.__new__(modelo.Nowcast)
    nc.V = {"Nacional": {"00": pd.Series({pd.Timestamp("2026-09-01"): 2.0})}}
    mes = pd.Timestamp("2026-11-01")
    cal = [{"nombre": "nafta", "componente": "07.2.2", "parte": 0.7, "regiones": ["GBA"], "variacion": 3.0,
            "vigencia": "2026-11-01"}]
    monkeypatch.setattr(modelo, "leer_regulados", lambda m, previo=False: [] if previo else cal)
    extra = [{"region": "GBA", "componente": "07.2.2", "fuente": "surtidor", "valor": 2.0, "parte": 1.0}]
    info = nc.informacion_del_mes(mes, usar_super=False, extra=extra, usar_reglas=False)
    partes = {it["fuente"]: it["parte"] for it in info if it["componente"] == "07.2.2"}
    assert abs(partes["calendario de regulados"] - 0.7) < 1e-9
    assert abs(partes["surtidor"] - 0.3) < 1e-9
