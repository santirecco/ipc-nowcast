"""Paso 2: replica la agregación de INDEC, calibra los pesos exactos y calcula los pesos efectivos.

Salidas:
  config/ponderaciones_calibradas.yaml         pesos exactos (los usa el resto del modelo)
  data/processed/pesos_efectivos.csv           peso de cada región x división, mes a mes
  data/processed/incidencias.csv               aporte de cada región x división a la variación nacional
  reports/replica_indec.md                     informe legible con los resultados
"""
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pandas as pd  # noqa: E402
import yaml  # noqa: E402

from ipc_nowcast import CONFIG, DATA, REGIONES, REPORTS, indec, replica  # noqa: E402


MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]


def _mes(t) -> str:
    return f"{MESES[t.month - 1]} {t.year}"


def _mes_corto(t) -> str:
    return f"{MESES[t.month - 1][:3]}-{t:%y}"


def _num(v, fmt: str = "{:.2f}") -> str:
    """Número con coma decimal (formato argentino)."""
    if isinstance(v, (int,)) or (isinstance(v, float) and float(v).is_integer() and fmt == "{:.0f}"):
        return str(int(v))
    if isinstance(v, float):
        return fmt.format(v).replace(".", ",")
    return str(v)


def _tabla_md(df: pd.DataFrame, fmt: str = "{:.2f}") -> str:
    cols = [str(c) for c in df.columns]
    lineas = ["| " + " | ".join([df.index.name or ""] + cols) + " |", "|" + "---|" * (len(cols) + 1)]
    for idx, fila in df.iterrows():
        celdas = [_num(v, fmt) for v in fila.values]
        lineas.append("| " + " | ".join([str(idx)] + celdas) + " |")
    return "\n".join(lineas)


def main():
    df = pd.read_parquet(DATA / "processed" / "indec_divisiones.parquet")
    piv = replica.pivotear(df)
    pesos = replica.calibrar(piv)
    _, w_pub, nombres = indec.ponderaciones_base()

    # 1) Pesos calibrados (en %)
    cal = {
        "_nota": "Generado por scripts/replicar_indec.py. Pesos base dic-2016 en %, calibrados contra la serie oficial.",
        "_actualizado": str(date.today()),
        "region_en_nacional": {r: round(float(v) * 100, 4) for r, v in pesos["region_en_nacional"].items()},
        "division_en_region": {d: {r: round(float(pesos["division_en_region"].loc[d, r]) * 100, 4) for r in REGIONES} for d in replica.DIVISIONES},
        "categoria_en_region": {c: {r: round(float(pesos["categoria_en_region"].loc[c, r]) * 100, 4) for r in REGIONES} for c in replica.CATEGORIAS},
        "bys_en_region": {c: {r: round(float(pesos["bys_en_region"].loc[c, r]) * 100, 4) for r in REGIONES} for c in replica.BIENES_SERVICIOS},
        "region_en_division_nacional": {d: {r: round(float(pesos["region_en_division_nacional"].loc[d, r]) * 100, 4) for r in REGIONES} for d in replica.DIVISIONES},
    }
    (CONFIG / "ponderaciones_calibradas.yaml").write_text(yaml.safe_dump(cal, allow_unicode=True, sort_keys=False), encoding="utf-8")

    # 2) Validación
    val = replica.validar(piv, pesos)

    # 3) Pesos efectivos e incidencias
    ef = replica.pesos_efectivos(piv, pesos)
    inc = replica.descomponer_variacion(piv, ef)
    ef.to_csv(DATA / "processed" / "pesos_efectivos.csv", index=False, float_format="%.4f")
    inc.to_csv(DATA / "processed" / "incidencias.csv", index=False, float_format="%.4f")

    # 4) Informe
    ult = ef.periodo.max()
    nac_div = ef[ef.periodo == ult].groupby("division")["peso_en_nacional_%"].sum()
    base_div = ef[ef.periodo == ef.periodo.min()].groupby("division")["peso_en_nacional_%"].sum()
    tabla_div = pd.DataFrame({"División": [nombres[d] for d in nac_div.index], "Peso dic-16 %": base_div.values, f"Peso {_mes_corto(ult)} %": nac_div.values})
    tabla_div["Cambio pp"] = tabla_div.iloc[:, 2] - tabla_div.iloc[:, 1]
    tabla_div = tabla_div.set_index("División").sort_values(f"Peso {_mes_corto(ult)} %", ascending=False)

    reg = ef[ef.periodo == ult].groupby("region")["peso_region_en_nacional_%"].first().reindex(REGIONES)
    tabla_reg = pd.DataFrame({"Base calibrada %": [cal["region_en_nacional"][r] for r in REGIONES], f"Efectivo {_mes_corto(ult)} %": reg.values}, index=pd.Index(REGIONES, name="Región"))

    celda = ef[ef.periodo == ult].pivot(index="division", columns="region", values="peso_en_region_%")[REGIONES]
    celda.index = [nombres[d] for d in celda.index]
    celda.index.name = "División"

    dif = (pesos["division_en_region"] * 100 - w_pub[REGIONES]).abs().max().max()
    v = val.set_index("serie")
    vtxt = v[["error_nivel_max_%", "error_var_mensual_max_pp", "meses_con_otra_decima"]].copy()
    vtxt["meses_con_otra_decima"] = vtxt["meses_con_otra_decima"].astype(int)
    vtxt.columns = ["Error máx. en nivel (%)", "Error máx. en variación mensual (pp)", "Meses con otra décima"]
    vtxt.index.name = "Réplica"

    ultimo_inc = inc[inc.periodo == ult]
    var_rep = ultimo_inc["incidencia_pp"].sum()
    var_pub = df[(df.region == "Nacional") & (df.codigo == "00") & (df.periodo == ult)]["var_m"].iloc[0]

    md = f"""# Réplica del IPC de INDEC

*Generado automáticamente el {date.today():%d/%m/%Y} con datos hasta {_mes(ult)}.*

## Resultado

Con los pesos calibrados, el modelo reproduce **toda la serie oficial desde dic-2016** con error prácticamente nulo:
el nacional reconstruido desde las 72 celdas región × división difiere del publicado en
**{_num(v.loc['Nacional: general desde 72 celdas región x división', 'error_nivel_max_%'], '{:.4f}')}%** como máximo en nivel, y en
**{int(v.loc['Nacional: general desde 72 celdas región x división', 'meses_con_otra_decima'])}** de
{int(v.loc['Nacional: general desde 72 celdas región x división', 'meses'])} meses la variación mensual redondeada daría una décima distinta.

Control del último mes: variación nacional reconstruida **{_num(var_rep)}%** vs publicada **{_num(float(var_pub), '{:.1f}')}%**.

Hallazgos sobre cómo agrega INDEC:
- El IPC de cada región es un Laspeyres de sus 12 divisiones (también de Bienes/Servicios y de Estacional/Núcleo/Regulados).
- El nacional es un Laspeyres de los 6 niveles regionales: los pesos regionales **se mueven con los precios relativos**
  (no son fijos sobre las variaciones mensuales).
- Cada división nacional tiene sus propios pesos regionales, distintos del producto peso región × peso división.
- Los pesos publicados (1 decimal) difieren de los exactos en hasta {_num(dif)} pp; por eso calibramos.

## Peso de cada división en el índice nacional

El peso efectivo es el que realmente pondera la variación del mes: el peso base ajustado por cuánto subió cada rubro
respecto del resto desde dic-2016.

{_tabla_md(tabla_div)}

## Peso de cada región en el índice nacional

{_tabla_md(tabla_reg)}

## Peso de cada división dentro de su región ({_mes_corto(ult)}, %)

{_tabla_md(celda)}

## Precisión de cada réplica

{_tabla_md(vtxt, "{:.4f}")}

## Archivos

- `config/ponderaciones_calibradas.yaml`: pesos exactos.
- `data/processed/pesos_efectivos.csv`: peso de cada región × división, mes a mes.
- `data/processed/incidencias.csv`: aporte de cada región × división a la variación nacional, mes a mes.
"""
    REPORTS.mkdir(exist_ok=True)
    (REPORTS / "replica_indec.md").write_text(md, encoding="utf-8")
    print(vtxt.to_string())
    print(f"\nÚltimo mes: reconstruido {var_rep:.3f}% vs publicado {var_pub}%")


if __name__ == "__main__":
    main()
