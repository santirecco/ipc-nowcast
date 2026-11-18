"""Backtest: simula el modelo mes a mes con la información que había en cada momento y mide el error.

Salidas: data/nowcast/backtest.csv y reports/backtest.md
"""
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pandas as pd  # noqa: E402

from ipc_nowcast import DATA, REPORTS, fuentes, modelo  # noqa: E402


def _n(v, d=2):
    return f"{v:.{d}f}".replace(".", ",")


def main():
    d = pd.read_parquet(DATA / "processed" / "indec_divisiones.parquet")
    a = pd.read_parquet(DATA / "processed" / "indec_aperturas.parquet")
    nc = modelo.Nowcast(d, a, fuentes.leer_ipcba())
    bt = modelo.backtest(nc, desde="2024-07-01")
    (DATA / "nowcast").mkdir(parents=True, exist_ok=True)
    bt.to_csv(DATA / "nowcast" / "backtest.csv", float_format="%.4f")

    filas = []
    for desde, etiqueta in [("2024-07-01", "jul-24 en adelante"), ("2025-01-01", "2025-2026"), ("2025-07-01", "últimos 16 meses")]:
        x = bt[bt.index >= desde].dropna(subset=["caba"])
        for col, nombre in [("inicio_de_mes", "Inicio de mes (solo estadística)"), ("mitad_de_mes", "Mitad de mes (+ precios hasta el día 15)"),
                            ("fin_de_mes", "Fin de mes (+ precios del mes completo)"), ("caba", "IPC CABA solo"),
                            ("vispera_con_caba", "Víspera (modelo + IPC CABA)")]:
            e = (x[col] - x.real).abs()
            filas.append({"Período": etiqueta, "Momento": nombre, "Error promedio (pp)": e.mean(),
                          "Error p80 (pp)": e.quantile(0.8), "Error máximo (pp)": e.max(), "Meses": len(x)})
    t = pd.DataFrame(filas)
    lineas = ["| Período | Momento | Error promedio (pp) | 80% de los meses dentro de (pp) | Error máximo (pp) | Meses |", "|---|---|---|---|---|---|"]
    for _, f in t.iterrows():
        lineas.append(f"| {f['Período']} | {f['Momento']} | {_n(f['Error promedio (pp)'])} | ±{_n(f['Error p80 (pp)'])} | {_n(f['Error máximo (pp)'])} | {f['Meses']} |")
    det = ["| Mes | INDEC | Inicio de mes | Mitad de mes | Fin de mes | IPC CABA | Víspera | Clases con datos propios |",
           "|---|---|---|---|---|---|---|---|"]
    for m, f in bt.iloc[::-1].iterrows():
        det.append(f"| {m:%m/%Y} | {_n(f.real, 1)} | {_n(f.inicio_de_mes)} | {_n(f.mitad_de_mes)} | {_n(f.fin_de_mes)} | "
                   f"{_n(f.caba) if pd.notna(f.caba) else '—'} | {_n(f.vispera_con_caba)} | {int(f.clases_con_datos)} |")
    md = f"""# Backtest del modelo

*Generado el {date.today():%d/%m/%Y}.*

Se simula el pronóstico de cada mes usando solo la información disponible en ese momento:
- **Inicio de mes:** solo la proyección estadística por región y división.
- **Mitad de mes:** además, los alimentos con los precios hasta el día 15: góndolas de todo el país (SEPA, desde
  septiembre de 2024), verduras y frutas mayoristas (Mercado Central, desde 2026) y hacienda (desde 2017). Cada clase
  usa solo las fuentes que la mejoraron fuera de muestra (ver reports/adelantados.md).
- **Fin de mes:** lo mismo con el mes completo.
- **Víspera:** además, el IPC de la Ciudad de Buenos Aires del mismo mes, que se publica unos días antes que INDEC
  (peso {int(modelo.PESO_CABA * 100)}% IPC CABA / {int((1 - modelo.PESO_CABA) * 100)}% modelo). En los meses en que la Ciudad
  se desvió de INDEC con el mismo signo todos los años (enero y julio) se corrige el IPC CABA por ese desvío típico.

El calendario de regulados y los supermercados online no tienen historia: su aporte se mide en la prueba en
paralelo de los próximos meses. Los meses sin datos de SEPA (abril a junio de 2026) solo usan la hacienda.

## Error contra el dato de INDEC (nacional, variación mensual)

{chr(10).join(lineas)}

## Detalle mes a mes

{chr(10).join(det)}
"""
    (REPORTS / "backtest.md").write_text(md, encoding="utf-8")
    print(t.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
