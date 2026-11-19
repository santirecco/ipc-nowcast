"""Backtest largo: error del modelo mes a mes desde 2018, por período, con lo que se sabía en cada momento.

Antes de jul-2024 no hay precios relevados con historia (SEPA arranca en sep-2024): en esos años trabaja solo la
parte estadística (y el calendario de tarifas, en los meses que lo tienen). Sirve para que una mejora no "gane"
solo en un tramo. Salidas: data/nowcast/backtest_largo.csv y reports/backtest_largo.md
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from ipc_nowcast import DATA, REPORTS, adelantados, fuentes, modelo  # noqa: E402

PERIODOS = [("2018-01-01", "2019-12-01", "2018-2019"), ("2020-01-01", "2022-12-01", "2020-2022"),
            ("2023-01-01", "2024-06-01", "2023 a jun-2024"), ("2024-07-01", "2099-01-01", "jul-2024 en adelante"),
            ("2025-07-01", "2099-01-01", "últimos 16 meses")]
CON_PRECIOS = pd.Timestamp(__import__("os").environ.get("IPC_CON_PRECIOS", "2024-07-01"))


def correr(nc, usar_regulados=True, desde="2018-01-01"):
    real = nc.V["Nacional"]["00"]
    filas = []
    for mes in real.index[real.index >= pd.Timestamp(desde)]:
        if mes >= CON_PRECIOS:
            e0 = adelantados.informacion_historica(mes, "15", solo_estadistica=True)
            ec = adelantados.informacion_historica(mes, "completo")
        else:
            e0 = ec = []
        r0 = nc.calcular(mes, usar_regulados=usar_regulados, usar_caba=False, extra=e0)
        rc = nc.calcular(mes, usar_regulados=usar_regulados, usar_caba=False, extra=ec)
        filas.append({"mes": mes, "real": real.loc[mes], "inicio_de_mes": r0["estimacion"], "fin_de_mes": rc["estimacion"]})
    return pd.DataFrame(filas).set_index("mes")


def tabla(bt):
    filas = []
    for a, b, nombre in PERIODOS:
        x = bt[(bt.index >= a) & (bt.index <= b)]
        for col in ["inicio_de_mes", "fin_de_mes"]:
            e = (x[col] - x.real)
            filas.append({"periodo": nombre, "momento": col, "error": e.abs().mean(), "sesgo": e.mean(),
                          "maximo": e.abs().max(), "meses": len(x)})
    return pd.DataFrame(filas)


def main():
    d = pd.read_parquet(DATA / "processed" / "indec_divisiones.parquet")
    a = pd.read_parquet(DATA / "processed" / "indec_aperturas.parquet")
    nc = modelo.Nowcast(d, a, fuentes.leer_ipcba())
    bt = correr(nc)
    bt.to_csv(DATA / "nowcast" / "backtest_largo.csv", float_format="%.4f")
    t = tabla(bt)
    n = lambda v: f"{v:.2f}".replace(".", ",")  # noqa: E731
    lin = ["# Backtest largo (desde 2018)", "",
           "Cada mes se predice solo con lo que se sabía antes. Antes de jul-2024 no hay precios relevados con historia:",
           "en esos años el modelo es solo estadístico (más el calendario de tarifas donde está cargado).", "",
           "| Período | Momento | Error promedio (pp) | Sesgo (pp) | Error máximo (pp) | Meses |", "|---|---|---|---|---|---|"]
    for _, f in t.iterrows():
        lin.append(f"| {f.periodo} | {'Inicio de mes' if f.momento == 'inicio_de_mes' else 'Fin de mes'} | {n(f.error)} | "
                   f"{n(f.sesgo)} | {n(f.maximo)} | {f.meses} |")
    (REPORTS / "backtest_largo.md").write_text("\n".join(lin) + "\n", encoding="utf-8")
    print(t.round(3).to_string())


if __name__ == "__main__":
    main()
