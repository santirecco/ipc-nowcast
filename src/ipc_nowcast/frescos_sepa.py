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
