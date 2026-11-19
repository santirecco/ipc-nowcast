"""Frutas y verduras FRESCAS de SEPA (las que se venden por kilo, unidad, atado o bandeja).

La clase SEPA de verduras (01.1.7) y frutas (01.1.6) mezcla envasados (latas, congelados, deshidratados, frutas en
almíbar, frutos secos) que casi no se mueven, mientras INDEC mide sobre todo frescos, que saltan ±10-30% por mes.
Estas clases "01.1.7f" y "01.1.6f" usan solo los frescos."""
import re

import numpy as np
import pandas as pd

from . import sepa
from .clasificador_sepa import normalizar
VERD=r"^(?:tomate|papa|cebolla|lechuga|zanahoria|zapallo|zapallito|batata|morron|pimiento|acelga|espinaca|brocoli|coliflor|repollo|berenjena|pepino|choclo|ajo|apio|puerro|remolacha|rucula|radicheta|chaucha|mandioca|verdeo|perejil|albahaca|calabaza|alcaucil|esparrago|rabanito|nabo)\b"
FRUT=r"^(?:manzana|banana|naranja|mandarina|limon|pera|uva|frutilla|durazno|ciruela|kiwi|anana|melon|sandia|pomelo|palta|mango|cereza|damasco|pelon|nectarina|higo|arandano|membrillo|kaki|granada|papaya|lima)\b"
NO=r"(?:dulcor|cong|refrig|fritas?|trit|mitades|trozos|cubos|lata|tetra|frasco|conserva|congelad|deshid|almibar|pure|salsa|jugo|mermelada|dulce|bebida|pulpa|chips|baston|noisette|seco|confit|banad|chocolat|yogur|helado|cereal|barra|galleta|torta|tarta|empanad|milanesa|rellen|snack|natural p|pote|polvo|lista|lavad|en granos?|perita en|pelad|smiles|rusticas|carrefour classic|bsa)"
POR_PESO=r"(?:\bkg\b|kgr|\bxkg|x ?kg|granel|x ?un\b|xun|x ?uni|cubeta|bandeja|atado|x at\b|\(t\)|\(pax\))"
def fresco(n, rx):
    if not re.search(rx, n) or re.search(NO, n): return False
    if re.search(POR_PESO, n): return True
    return not re.search(r"\d", n) and len(n.split()) <= 4
def catalogo():
    d=pd.read_csv(sepa.SALIDA / 'descripciones.csv',dtype=str); d['n']=d.desc.map(normalizar)
    out=[]
    for c,rx in [('01.1.7',VERD),('01.1.6',FRUT)]:
        m=d[[fresco(n,rx) for n in d.n]].assign(clase_f=c)
        out.append(m)
    return pd.concat(out)
def indices_frescos(mes: str, corte=None, origen=sepa.CACHE) -> pd.DataFrame:
    """Variación % mensual de frutas y verduras frescas por región (misma fórmula que el resto de SEPA)."""
    import polars as pl
    cat = catalogo()
    out = []
    previo = (pd.Timestamp(mes + "-01") - pd.offsets.MonthBegin(1)).strftime("%Y-%m")
    for clase in ("01.1.7", "01.1.6"):
        ids = pl.from_pandas(cat[cat.clase_f == clase][["id_producto"]].drop_duplicates())

        def prom(m, c):
            fs = [str(p) for p in sorted(origen.glob(f"{m}-??.parquet")) if c is None or int(p.stem[-2:]) <= c]
            if not fs:
                return pd.DataFrame()
            lf = (pl.scan_parquet(fs).filter(pl.col("clase") == clase)
                    .select("fecha", "id_comercio", "region", "id_producto", "precio").join(ids.lazy(), on="id_producto"))
            return (lf.group_by("id_comercio", "region", "id_producto").agg(p=pl.col("precio").mean(), dias=pl.col("fecha").n_unique())
                      .collect().to_pandas().assign(clase=clase + "f"))
        a, b = prom(previo, None), prom(mes, corte)
        if a.empty or b.empty:
            continue
        v = sepa.variacion(a.assign(mes=previo), b.assign(mes=mes), min_productos=8)
        if not v.empty:
            out.append(v.assign(mes=mes))
    return pd.concat(out) if out else pd.DataFrame()


# ---------------------------------------------------------------- canasta de variedades de INDEC
# INDEC publica el precio promedio de estas variedades (GBA) desde 2016. La variación de verduras y frutas de INDEC
# se explica muy bien con ellas (error medio ~2,3 pp en verduras, ~2 pp en frutas, pesos estimados con meses
# anteriores). Se arma la misma canasta con los precios de SEPA, variedad por variedad.
VARIEDADES_FRESCAS = {
    "01.1.7": {"Tomate redondo": r"^tomate\b(?!.*\b(?:cherry|perita|pera|hidrop))", "Papa": r"^papas?\b",
               "Cebolla": r"^cebollas?\b(?!.*\b(?:verdeo|morada))", "Lechuga": r"^lechugas?\b",
               "Zapallo anco": r"^(?:zapallo|calabaza)\b(?!.*zapallito)", "Batata": r"^batatas?\b"},
    "01.1.6": {"Banana": r"^bananas?\b", "Manzana deliciosa": r"^manzanas?\b(?!.*verde)", "Naranja": r"^naranjas?\b",
               "Limón": r"^limon(?:es)?\b"},
}


def indices_variedades_frescas(mes: str, corte=None, origen=sepa.CACHE, cat=None) -> pd.DataFrame:
    """Variación % mensual de cada variedad de la canasta de INDEC, por región (SEPA, solo frescos)."""
    import polars as pl
    cat = cat if cat is not None else catalogo()
    previo = (pd.Timestamp(mes + "-01") - pd.offsets.MonthBegin(1)).strftime("%Y-%m")
    out = []
    for clase, vs in VARIEDADES_FRESCAS.items():
        base = cat[cat.clase_f == clase]
        filas = []
        for v, rx in vs.items():
            ids = base[base.n.str.contains(rx, regex=True)].id_producto.drop_duplicates()
            filas += [(i, v) for i in ids]
        if not filas:
            continue
        mapa = pl.DataFrame(filas, schema=["id_producto", "variedad"], orient="row").unique("id_producto")

        def prom(m, c):
            fs = [str(p) for p in sorted(origen.glob(f"{m}-??.parquet")) if c is None or int(p.stem[-2:]) <= c]
            if not fs:
                return pd.DataFrame()
            lf = (pl.scan_parquet(fs).filter(pl.col("clase") == clase)
                    .select("fecha", "id_comercio", "region", "id_producto", "precio").join(mapa.lazy(), on="id_producto"))
            return (lf.group_by("id_comercio", "region", "id_producto", "variedad").agg(p=pl.col("precio").mean(), dias=pl.col("fecha").n_unique())
                      .collect().to_pandas().rename(columns={"variedad": "clase"}))
        a, b = prom(previo, None), prom(mes, corte)
        if a.empty or b.empty:
            continue
        v = sepa.variacion(a, b, min_productos=1)
        if not v.empty:
            out.append(v.assign(mes=mes, grupo=clase))
    return pd.concat(out) if out else pd.DataFrame()


def pesos_variedades(hasta: pd.Timestamp, clase: str) -> dict:
    """Pesos de cada variedad en la variación de INDEC de la clase (GBA), estimados con los meses anteriores a `hasta`."""
    from scipy.optimize import nnls
    from . import DATA
    pp = pd.read_csv(DATA / "precios" / "indec" / "precios_promedio_gba.csv")
    pp["mes"] = pd.to_datetime(pp.mes + "-01")
    vs = list(VARIEDADES_FRESCAS[clase])
    P = pp[pp.variedad.isin(vs)].pivot_table(index="mes", columns="variedad", values="precio")[vs]
    X = (P / P.shift(1) - 1) * 100
    y = pd.read_parquet(DATA / "processed" / "indec_aperturas.parquet")
    y = y[(y.region == "GBA") & (y.codigo == clase)].set_index("periodo").indice.sort_index()
    y = (y / y.shift(1) - 1) * 100
    df = X.join(y.rename("y"), how="inner").dropna()
    df = df[df.index < hasta]
    if len(df) < 24:
        return {}
    w, _ = nnls(df[vs].values, df.y.values)
    return dict(zip(vs, w))
