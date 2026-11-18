"""Calcula el pronóstico del IPC del mes en curso con toda la información disponible hoy.

Uso:  python scripts/nowcast.py            (mes siguiente al último publicado por INDEC)
      python scripts/nowcast.py 2026-12    (un mes puntual)

Salidas (data/nowcast/): historial.csv, ultimo_*.csv, supermercados_*.csv; informe en reports/nowcast.md
"""
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pandas as pd  # noqa: E402
import yaml  # noqa: E402

from ipc_nowcast import CONFIG, DATA, REGIONES, REPORTS, adelantados, fuentes, indec, modelo, replica, supermercados  # noqa: E402

OUT = DATA / "nowcast"
MOMENTOS = {"inicio_de_mes": "solo modelo estadístico", "mitad_de_mes": "con precios de la primera quincena",
            "fin_de_mes": "con precios del mes completo", "vispera_con_caba": "con IPC de la Ciudad"}
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]


def n(v, d=2):
    return "—" if v is None or pd.isna(v) else f"{v:.{d}f}".replace(".", ",")


def banda(momento: str) -> float:
    ruta = OUT / "backtest.csv"
    if not ruta.exists():
        return 0.5
    bt = pd.read_csv(ruta, index_col=0, parse_dates=True).iloc[-16:]
    col = momento if momento in bt else "inicio_de_mes"
    return float((bt[col] - bt.real).abs().quantile(0.8))


def momento_del_mes(con_caba: bool, extra: list, hoy: pd.Timestamp, mes: pd.Timestamp) -> str:
    """Qué columna del backtest describe mejor la información disponible hoy."""
    if con_caba:
        return "vispera_con_caba"
    if not extra:
        return "inicio_de_mes"
    return "fin_de_mes" if (hoy >= mes + pd.offsets.MonthEnd(0) or hoy.day >= 21) else "mitad_de_mes"


def main():
    hoy = date.today()
    d = pd.read_parquet(DATA / "processed" / "indec_divisiones.parquet")
    a = pd.read_parquet(DATA / "processed" / "indec_aperturas.parquet")
    ultimo_publicado = d.periodo.max()
    mes = pd.Timestamp(sys.argv[1] + "-01") if len(sys.argv) > 1 else ultimo_publicado + pd.offsets.MonthBegin(1)

    # supermercados: índice diario por clase y resumen mensual
    panel = supermercados.cargar_panel()
    idx = supermercados.indices_diarios(panel)
    sm = supermercados.resumen_mensual(idx)
    OUT.mkdir(parents=True, exist_ok=True)
    if not idx.empty:
        larga = idx.rename_axis("fecha").reset_index().melt(id_vars="fecha", var_name="clase", value_name="indice")
        larga["nombre"] = larga.clase.map(supermercados.NOMBRES)
        larga.to_csv(OUT / "supermercados_diario.csv", index=False, float_format="%.3f")
        sm.assign(nombre=sm.clase.map(supermercados.NOMBRES)).to_csv(OUT / "supermercados_mensual.csv", index=False, float_format="%.3f")

    nc = modelo.Nowcast(d, a, fuentes.leer_ipcba())
    extra = adelantados.informacion(nc, mes, pd.Timestamp(hoy))
    r = nc.calcular(mes, super_mensual=sm, extra=extra)
    sin_info = nc.calcular(mes, usar_regulados=False, usar_super=False, usar_caba=False)["estimacion"]
    con_caba = r["caba"] is not None
    momento = momento_del_mes(con_caba, extra, pd.Timestamp(hoy), mes)
    b = banda(momento)
    externos = yaml.safe_load((CONFIG / "externos.yaml").read_text(encoding="utf-8"))
    rem = (externos.get("rem") or {}).get(f"{mes:%Y-%m}", {}).get("valor")

    # detalle por división nacional y por región
    c = r["celdas"].copy()
    c.index = pd.MultiIndex.from_tuples(c.index, names=["region", "division"])
    _, _, nombres = indec.ponderaciones_base()
    div = c.groupby("division").apply(lambda g: pd.Series({
        "variacion_%": (g["variacion"] * g["peso_%"]).sum() / g["peso_%"].sum(),
        "peso_%": g["peso_%"].sum(), "incidencia_pp": g["incidencia_pp"].sum()})).reset_index()
    div["nombre"] = div.division.map(nombres)
    reg = c.groupby("region").apply(lambda g: pd.Series({
        "variacion_%": (g["variacion"] * g["peso_%"]).sum() / g["peso_%"].sum(),
        "peso_%": g["peso_%"].sum(), "incidencia_pp": g["incidencia_pp"].sum()})).reindex(REGIONES).reset_index()
    div.to_csv(OUT / "ultimo_divisiones.csv", index=False, float_format="%.4f")
    reg.to_csv(OUT / "ultimo_regiones.csv", index=False, float_format="%.4f")
    info = r["informacion"]
    if not info.empty:
        # efecto de cada dato sobre el IPC nacional: efecto en la división de esa región x peso de la celda
        w = r["celdas"]["peso_%"]
        info["peso_celda_%"] = [float(w.get((rr, dd), 0.0)) for rr, dd in zip(info.region, info.division)]
        info["efecto_nacional_pp"] = info.efecto_en_division_pp * info["peso_celda_%"] / 100
        info.to_csv(OUT / "ultimo_informacion.csv", index=False, float_format="%.4f")

    # historial de pronósticos (uno por día y mes pronosticado)
    fila = {"fecha_calculo": str(hoy), "mes": f"{mes:%Y-%m}", "estimacion": round(r["estimacion"], 4),
            "rango_bajo": round(r["estimacion"] - b, 4), "rango_alto": round(r["estimacion"] + b, 4),
            "solo_modelo_estadistico": round(sin_info, 4), "abajo_arriba": round(r["abajo_arriba"], 4),
            "ipc_caba": None if r["caba"] is None else round(r["caba"], 4), "ajuste_caba": round(r["ajuste_caba"], 4), "rem": rem,
            "datos_incorporados": len(info), "dias_supermercados": int(panel.fecha.nunique()) if not panel.empty else 0,
            "momento": momento}
    ruta_h = OUT / "historial.csv"
    h = pd.read_csv(ruta_h, dtype=str) if ruta_h.exists() else pd.DataFrame(columns=list(fila))
    h = h[~((h.fecha_calculo == fila["fecha_calculo"]) & (h.mes == fila["mes"]))]
    h = pd.concat([h, pd.DataFrame([fila]).astype(str)], ignore_index=True)
    h.to_csv(ruta_h, index=False)
    (OUT / "ultimo.json").write_text(json.dumps(fila, ensure_ascii=False, indent=2), encoding="utf-8")

    # informe legible
    nombre_mes = f"{MESES[mes.month - 1]} {mes.year}"
    t_div = "\n".join(f"| {f.nombre} | {n(f['peso_%'], 1)} | {n(f['variacion_%'])} | {n(f.incidencia_pp)} |"
                      for _, f in div.sort_values("incidencia_pp", ascending=False).iterrows())
    t_reg = "\n".join(f"| {f.region} | {n(f['peso_%'], 1)} | {n(f['variacion_%'])} |" for _, f in reg.iterrows())
    t_info = "\n".join(f"| {f.region} | {f.componente} | {f.fuente} | {n(f.valor)} | {n(f.proyeccion_estadistica)} | {n(f.efecto_en_division_pp)} |"
                       for _, f in info.iterrows()) if not info.empty else "| — | — | — | — | — | — |"
    if not sm.empty:
        u = sm[sm.mes == sm.mes.max()]
        t_sm = "\n".join(f"| {supermercados.NOMBRES.get(f.clase, f.clase)} | {int(f.dias)} | {n(f['en_el_mes_%'])} | {n(f['var_mensual_%'])} |"
                         for _, f in u.sort_values("clase").iterrows())
    else:
        t_sm = "| (todavía no hay dos días de datos) | | | |"
    md = f"""# Pronóstico IPC {nombre_mes}

*Calculado el {hoy:%d/%m/%Y}. Último dato oficial de INDEC: {MESES[ultimo_publicado.month - 1]} {ultimo_publicado.year}.*

## {n(r['estimacion'], 1)}% mensual (rango probable {n(r['estimacion'] - b, 1)}% a {n(r['estimacion'] + b, 1)}%)

| | % mensual |
|---|---|
| **Pronóstico** | **{n(r['estimacion'])}** |
| Solo modelo estadístico | {n(sin_info)} |
| Modelo + información del mes (de abajo hacia arriba) | {n(r['abajo_arriba'])} |
| IPC Ciudad de Buenos Aires del mes | {n(r['caba'])} {'(todavía no publicado)' if not con_caba else ''} |
| Ajuste estacional al IPC Ciudad (pp) | {n(r['ajuste_caba'])} |
| REM del BCRA (referencia) | {n(rem, 1)} |

El rango cubre el 80% de los errores del backtest de los últimos 16 meses para este momento del mes
({MOMENTOS.get(momento, momento)}).

## Por división (nacional)

| División | Peso % | Variación % | Incidencia (pp) |
|---|---|---|---|
{t_div}

## Por región

| Región | Peso % | Variación % |
|---|---|---|
{t_reg}

## Información del mes incorporada

| Región | Componente | Fuente | Dato % | Proyección estadística % | Efecto en la división (pp) |
|---|---|---|---|---|---|
{t_info}

## Supermercados online (último mes con datos)

| Clase | Días | Variación en lo que va del mes % | Variación mensual (promedio vs. mes anterior) % |
|---|---|---|---|
{t_sm}
"""
    (REPORTS / "nowcast.md").write_text(md, encoding="utf-8")
    print(json.dumps(fila, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
