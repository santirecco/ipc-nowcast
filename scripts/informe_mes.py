"""Informe automático cuando INDEC publica un dato: cómo le fue al predictor ese mes y dónde falló.

- Pronóstico en cada momento del mes (los cálculos diarios guardados y la simulación del backtest) contra el dato.
- Error a fin de mes descompuesto por rubro y por región (puntos del nivel general que explica cada uno).
- Señales del mes: en qué rubros los precios relevados acercaron el pronóstico al dato y en cuáles lo alejaron.

Salidas: reports/informe_AAAA-MM.md y data/nowcast/informe_ultimo.json (lo lee el tablero).
Uso: python scripts/informe_mes.py [AAAA-MM]   (sin argumento: el último mes publicado)
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from ipc_nowcast import DATA, REPORTS, adelantados, fuentes, indec, modelo  # noqa: E402

MOMENTOS = [("inicio_de_mes", "Inicio de mes"), ("mitad_de_mes", "Mitad de mes"), ("dia_22", "Día 22"),
            ("fin_de_mes", "Fin de mes"), ("vispera_con_caba", "Víspera")]
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]


def n(v, d=2, signo=False):
    if v is None or (isinstance(v, float) and not np.isfinite(v)):
        return "—"
    t = f"{abs(v):.{d}f}".replace(".", ",")
    return (("+" if v > 0 else "−" if v < 0 else "") if signo else ("−" if v < 0 else "")) + t


def main():
    d = pd.read_parquet(DATA / "processed" / "indec_divisiones.parquet")
    a = pd.read_parquet(DATA / "processed" / "indec_aperturas.parquet")
    nc = modelo.Nowcast(d, a, fuentes.leer_ipcba())
    real = nc.V["Nacional"]["00"].dropna()
    mes = pd.Timestamp(sys.argv[1] + "-01") if len(sys.argv) > 1 else real.index.max()
    dato = float(real.loc[mes])
    nombre_mes = f"{MESES[mes.month - 1]} {mes.year}"

    # 1. pronóstico en cada momento: simulación (backtest) y cálculos en vivo guardados
    bt = pd.read_csv(DATA / "nowcast" / "backtest.csv", index_col=0, parse_dates=True)
    sim = []
    if mes in bt.index:
        for col, nom in MOMENTOS:
            if col in bt and pd.notna(bt.loc[mes, col]):
                sim.append({"momento": nom, "pronostico": round(float(bt.loc[mes, col]), 3), "error": round(float(bt.loc[mes, col]) - dato, 3)})
    vivo = []
    h = pd.read_csv(DATA / "nowcast" / "historial.csv")
    hm = h[h.mes == f"{mes:%Y-%m}"]
    if not hm.empty:
        for etiqueta, fila in [("Primer cálculo", hm.iloc[0]), ("Último cálculo", hm.iloc[-1])]:
            vivo.append({"momento": f"{etiqueta} ({fila.fecha_calculo})", "pronostico": round(float(fila.estimacion), 3),
                         "error": round(float(fila.estimacion) - dato, 3)})

    # 2. error a fin de mes por rubro y por región
    ex = adelantados.informacion_historica(mes, "completo")
    r = nc.calcular(mes, usar_regulados=False, usar_caba=False, extra=ex)
    c = r["celdas"].copy()
    c.index = pd.MultiIndex.from_tuples(c.index, names=["region", "division"])
    c["real"] = [nc.V[rg][dv].get(mes, np.nan) for rg, dv in c.index]
    c["aporte_error"] = c["peso_%"] / 100 * (c.variacion - c.real)
    _, _, nombres = indec.ponderaciones_base()
    por_div = c.groupby("division").apply(lambda g: pd.Series({
        "pronostico": (g.variacion * g["peso_%"]).sum() / g["peso_%"].sum(), "real": (g.real * g["peso_%"]).sum() / g["peso_%"].sum(),
        "aporte_error": g.aporte_error.sum()})).reset_index()
    por_div["nombre"] = por_div.division.map(nombres)
    por_reg = c.groupby("region").apply(lambda g: pd.Series({
        "pronostico": (g.variacion * g["peso_%"]).sum() / g["peso_%"].sum(), "real": (g.real * g["peso_%"]).sum() / g["peso_%"].sum(),
        "aporte_error": g.aporte_error.sum()})).reset_index()

    # 3. señales del mes: ¿acercaron o alejaron?
    sen = []
    ab = adelantados.RUTA_BT
    if ab.exists():
        b = pd.read_csv(ab, dtype={"clase": str, "corte": str}, parse_dates=["mes"])
        b = b[(b.mes == mes) & (b.corte == "completo") & (~b.solo_inicio.astype(bool))]
        for (clase, fuente), g in b.groupby(["clase", "fuentes"]):
            e_sin = float((g.proy - g.real).abs().mean())
            e_con = float((g.pred - g.real).abs().mean())
            sen.append({"rubro": adelantados.NOMBRES.get(clase, clase), "fuente": " + ".join(adelantados.ETIQUETA.get(f, f) for f in fuente.split("+")),
                        "real": round(float(g.real.mean()), 2), "con_senal": round(float(g.pred.mean()), 2), "sin_senal": round(float(g.proy.mean()), 2),
                        "mejora": round(e_sin - e_con, 2)})
    sen = sorted(sen, key=lambda x: x["mejora"])

    fin = next((x for x in sim if x["momento"] == "Fin de mes"), None)
    peor_div = por_div.reindex(por_div.aporte_error.abs().sort_values(ascending=False).index).head(3)
    resumen = (f"INDEC publicó {n(dato)}% para {nombre_mes}."
               + (f" A fin de mes el predictor daba {n(fin['pronostico'])}% (error {n(fin['error'], 2, True)} pp)." if fin else "")
               + " Los rubros que más explicaron el error: "
               + ", ".join(f"{row.nombre} ({n(row.aporte_error, 2, True)} pp)" for row in peor_div.itertuples()) + ".")
    ayudaron = [x for x in sen if x["mejora"] > 0.05]
    fallaron = [x for x in sen if x["mejora"] < -0.05]

    out = {"mes": f"{mes:%Y-%m}", "dato": round(dato, 3), "resumen": resumen, "simulacion": sim, "en_vivo": vivo,
           "por_division": por_div.round(3).replace({np.nan: None}).to_dict("records"),
           "por_region": por_reg.round(3).replace({np.nan: None}).to_dict("records"),
           "senales": sen, "ayudaron": len(ayudaron), "fallaron": len(fallaron)}
    (DATA / "nowcast" / "informe_ultimo.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")

    L = [f"# Informe del predictor · {nombre_mes}", "", resumen, "", "## Pronóstico en cada momento del mes", "",
         "| Momento | Pronóstico | Error (pp) |", "|---|---|---|"]
    L += [f"| {x['momento']} | {n(x['pronostico'])}% | {n(x['error'], 2, True)} |" for x in vivo + sim]
    L += ["", "Error = pronóstico − dato. Las filas de «cálculo» son los pronósticos que se publicaron en vivo; el resto, la "
          "simulación con lo que se sabía en cada momento.", "", "## Dónde estuvo el error (fin de mes)", "",
          "| Rubro | Pronóstico | INDEC | Aporte al error (pp) |", "|---|---|---|---|"]
    for row in por_div.reindex(por_div.aporte_error.abs().sort_values(ascending=False).index).itertuples():
        L.append(f"| {row.nombre} | {n(row.pronostico)}% | {n(row.real)}% | {n(row.aporte_error, 3, True)} |")
    L += ["", "| Región | Pronóstico | INDEC | Aporte al error (pp) |", "|---|---|---|---|"]
    for row in por_reg.itertuples():
        L.append(f"| {row.region} | {n(row.pronostico)}% | {n(row.real)}% | {n(row.aporte_error, 3, True)} |")
    L += ["", "## Señales del mes", "", "Mejora = cuánto bajó el error del rubro la señal frente a la proyección con la historia "
          "(promedio de las 6 regiones, en pp). Negativo: la señal alejó el pronóstico del dato.", "",
          "| Rubro | Fuente | INDEC | Con la señal | Sin la señal | Mejora (pp) |", "|---|---|---|---|---|---|"]
    for x in sen:
        L.append(f"| {x['rubro']} | {x['fuente']} | {n(x['real'])}% | {n(x['con_senal'])}% | {n(x['sin_senal'])}% | {n(x['mejora'], 2, True)} |")
    L += ["", f"Señales que ayudaron: {len(ayudaron)} · que alejaron el pronóstico: {len(fallaron)}. Un rubro que falla varios "
          "meses seguidos es candidato a revisar."]
    (REPORTS / f"informe_{mes:%Y-%m}.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print(resumen)


if __name__ == "__main__":
    main()
