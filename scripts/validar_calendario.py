"""Valida hacia adelante el calendario de tarifas: para cada mes ya publicado por INDEC compara, componente por
componente, el pronóstico con el calendario (aumentos anunciados) contra el de la regla estadística sola.

Usa data/nowcast/registro_calendario.csv (lo escribe scripts/nowcast.py cada día; se toma el último registro de
cada mes) y escribe reports/validacion_calendario.md. Cuando haya suficientes meses, este resultado decide si el
calendario sigue reemplazando a la regla.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import pandas as pd  # noqa: E402

from ipc_nowcast import DATA, modelo  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]


def main():
    ruta = DATA / "nowcast" / "registro_calendario.csv"
    if not ruta.exists():
        print("Todavía no hay registro del calendario.")
        return
    r = pd.read_csv(ruta)
    r = r[r.fecha == r.groupby("mes").fecha.transform("max")]
    d = pd.read_parquet(DATA / "processed" / "indec_divisiones.parquet")
    a = pd.read_parquet(DATA / "processed" / "indec_aperturas.parquet")
    nc = modelo.Nowcast(d, a, None)
    filas = []
    for (mes, reg, comp), g in r.groupby(["mes", "region", "componente"]):
        m = pd.Timestamp(mes + "-01")
        if (reg, comp) not in nc.Vap.columns or m not in nc.Vap.index or pd.isna(nc.Vap[reg][comp].get(m)):
            continue
        real = float(nc.Vap[reg][comp][m])
        proy = float(g.proyeccion_estadistica.iloc[0])
        cal = g[g.fuente.str.contains("calendario|arrastre")]
        otra = g[~g.fuente.str.contains("calendario|arrastre")]
        parte_cal = min(1.0, cal[~cal.fuente.str.contains("arrastre")].parte.sum())
        con_cal = (cal.parte * cal.valor).sum() + (otra.parte * otra.valor).sum() + max(0.0, 1 - parte_cal - otra.parte.sum()) * proy
        sin_cal = float(otra.valor.iloc[0]) if len(otra) else proy
        filas.append({"mes": mes, "region": reg, "componente": comp, "real": real, "con_calendario": con_cal,
                      "sin_calendario": sin_cal, "err_con": abs(con_cal - real), "err_sin": abs(sin_cal - real)})
    t = pd.DataFrame(filas)
    out = ["# Validación del calendario de tarifas (hacia adelante)", ""]
    if t.empty:
        out.append("Todavía no hay meses publicados por INDEC con registro del calendario.")
    else:
        res = t.groupby("componente")[["err_con", "err_sin"]].mean().round(2)
        res["meses"] = t.groupby("componente").mes.nunique()
        out += ["Error medio por componente (puntos porcentuales): con calendario vs sin calendario (regla o proyección).", "",
                "| Componente | Con calendario | Sin calendario | Meses |", "|---|---|---|---|"]
        out += [f"| {c} | {f.err_con:.2f} | {f.err_sin:.2f} | {int(f.meses)} |" for c, f in res.iterrows()]
        t.round(3).to_csv(DATA / "nowcast" / "validacion_calendario.csv", index=False)
    (RAIZ / "reports" / "validacion_calendario.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print("\n".join(out))


if __name__ == "__main__":
    main()
