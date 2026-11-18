"""Calibra los indicadores adelantados de alimentos (SEPA, Mercado Central, hacienda) contra INDEC.

Correr después de cada dato nuevo de INDEC (lo hace el workflow mensual).
Salidas: config/calibracion_adelantados.yaml, data/precios/adelantados_backtest.csv, reports/adelantados.md
"""
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pandas as pd  # noqa: E402

from ipc_nowcast import DATA, REPORTS, adelantados, fuentes, modelo  # noqa: E402


def _n(v, d=2):
    return "—" if v is None or pd.isna(v) else f"{v:.{d}f}".replace(".", ",")


def main():
    d = pd.read_parquet(DATA / "processed" / "indec_divisiones.parquet")
    a = pd.read_parquet(DATA / "processed" / "indec_aperturas.parquet")
    nc = modelo.Nowcast(d, a, fuentes.leer_ipcba())
    calib, res, bt = adelantados.calibrar(nc)
    nombres_f = {"sepa": "SEPA", "may": "mayorista", "sepa+may": "SEPA + mayorista"}
    lineas = []
    for corte, etiqueta in [("15", "Mitad de mes (datos hasta el día 15)"), ("completo", "Mes completo")]:
        lineas += [f"### {etiqueta}", "",
                   "| Clase | Fuentes | Meses evaluados | Error solo estadística (pp) | Error con la fuente (pp) | ¿Se usa? |",
                   "|---|---|---|---|---|---|"]
        r = res[res.corte == corte].sort_values(["clase", "fuentes"]) if not res.empty else res
        for _, f in r.iterrows():
            ops = [o["fuentes"] for o in calib.get(corte, {}).get(f.clase, [])]
            pos = ops.index(f.fuentes.split("+")) if f.fuentes.split("+") in ops else None
            usa = "no" if pos is None else ("**sí**" if pos == 0 else "sí, si falta la anterior")
            lineas.append(f"| {adelantados.NOMBRES.get(f.clase, f.clase)} | {nombres_f.get(f.fuentes, f.fuentes)} | {f.meses} | "
                          f"{_n(f.error_proyeccion)} | {_n(f.error_con_fuente)} | {usa} |")
        lineas.append("")
    md = f"""# Indicadores adelantados de alimentos

*Generado el {date.today():%d/%m/%Y}.*

Para cada clase de alimentos se mide si los precios de góndola de todo el país (SEPA), los precios mayoristas
de verduras y frutas (Mercado Central) y el precio de la hacienda (carne) anticipan el dato de INDEC mejor que la
proyección estadística sola. La prueba es **fuera de muestra**: cada mes se predice con coeficientes estimados
solo con los meses anteriores. El error es el promedio, en puntos porcentuales, de la variación mensual de la
clase en las seis regiones. Una fuente se usa en una clase solo si baja el error al menos {_n(adelantados.MEJORA_MINIMA)} pp.
Si hay varias que sirven, se usa la mejor (comparadas en los mismos meses) y las otras quedan de respaldo para los
meses en que falta algún dato (por ejemplo, SEPA no tiene abril a junio de 2026).

{chr(10).join(lineas)}
"""
    (REPORTS / "adelantados.md").write_text(md, encoding="utf-8")
    print(md)


if __name__ == "__main__":
    main()
