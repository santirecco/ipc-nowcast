"""Prepara los archivos que lee el tablero (data/tablero/*.csv), con nombres de columna simples."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pandas as pd  # noqa: E402

from ipc_nowcast import DATA  # noqa: E402

NC = DATA / "nowcast"
OUT = DATA / "tablero"
COMPONENTES = {"04.5": "Electricidad, gas y otros combustibles", "06.4.1": "Prepagas", "07.3": "Transporte público",
               "07.2.2": "Combustibles", "02.2": "Tabaco", "08.3": "Telefonía e internet"}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    h = pd.read_csv(NC / "historial.csv")
    if "ajuste_caba" not in h.columns:
        h["ajuste_caba"] = 0.0
    h.rename(columns={"solo_modelo_estadistico": "solo_modelo"})[
        ["fecha_calculo", "mes", "estimacion", "rango_bajo", "rango_alto", "solo_modelo", "ipc_caba", "ajuste_caba", "rem", "dias_supermercados"]
    ].round(3).to_csv(OUT / "pronostico.csv", index=False)

    d = pd.read_csv(NC / "ultimo_divisiones.csv", dtype={"division": str})
    d.rename(columns={"variacion_%": "variacion", "peso_%": "peso", "incidencia_pp": "incidencia"})[
        ["division", "nombre", "variacion", "peso", "incidencia"]].round(3).to_csv(OUT / "divisiones.csv", index=False)

    r = pd.read_csv(NC / "ultimo_regiones.csv")
    r.rename(columns={"variacion_%": "variacion", "peso_%": "peso", "incidencia_pp": "incidencia"})[
        ["region", "variacion", "peso", "incidencia"]].round(3).to_csv(OUT / "regiones.csv", index=False)

    ruta = NC / "ultimo_informacion.csv"
    if ruta.exists():
        i = pd.read_csv(ruta, dtype={"componente": str})
        i["nombre_componente"] = i.componente.map(COMPONENTES).fillna(i.componente)
        i["clave"] = i.region + " · " + i.nombre_componente
        i.rename(columns={"valor": "dato", "proyeccion_estadistica": "proyeccion", "efecto_en_division_pp": "efecto_pp"})[
            ["clave", "region", "nombre_componente", "fuente", "detalle", "dato", "proyeccion", "efecto_pp"]
        ].round(3).to_csv(OUT / "informacion.csv", index=False)

    b = pd.read_csv(NC / "backtest.csv", parse_dates=["mes"])
    b["mes"] = b.mes.dt.strftime("%Y-%m")
    b.rename(columns={"real": "indec", "caba": "ipc_caba", "vispera_con_caba": "vispera"}).round(3).to_csv(OUT / "backtest.csv", index=False)

    s = pd.read_csv(DATA / "precios" / "supermercados" / "resumen.csv")
    s[["fecha", "cadena", "productos"]].to_csv(OUT / "recoleccion.csv", index=False)
    print("Tablero:", sorted(p.name for p in OUT.glob("*.csv")))


if __name__ == "__main__":
    main()
