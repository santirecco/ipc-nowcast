"""Variedades que INDEC publica con precio promedio (GBA) emparejadas con productos envasados de SEPA.

Sirve para (1) medir cuán bien sigue SEPA a INDEC producto por producto y (2) armar, por clase, una señal hecha solo
con los productos que INDEC efectivamente mide (en vez de todos los de la clase)."""
from __future__ import annotations

import re
import warnings

import numpy as np
import pandas as pd

from . import sepa
from .clasificador_sepa import normalizar

URL_PRECIOS = "https://www.indec.gob.ar/ftp/cuadros/economia/sh_ipc_precios_promedio.xls"
RUTA_INDEC = sepa.SALIDA.parent / "indec" / "precios_promedio_gba.csv"

# variedad INDEC: (clase, palabras que deben estar al principio, palabras que excluyen)
VARIEDADES = {
    "Pan de mesa": ("01.1.1", r"^pan (lactal|de mesa|blanco|molde)", r"integral|salvado|semilla|sin gluten|hamburgues|pancho|rallado|light|negro|centeno|keto"),
    "Galletitas dulces envasadas sin relleno": ("01.1.1", r"^galletit\w* (dulce|vainill|de vainill|maria|surtid|anillo|coco|limon|chocolat)", r"rellen|banad|banad|bano|oblea|sin gluten|chips"),
    "Galletitas de agua envasadas": ("01.1.1", r"^galletit\w* (de agua|agua|crackers?|criollit|salvado)", r"rellen|sin gluten"),
    "Harina de trigo común 000": ("01.1.1", r"^harina (de )?(trigo )?(comun )?0{3}\b", r"leudante|integral|0000|maiz|arroz|pizza|preme"),
    "Arroz blanco simple": ("01.1.1", r"^arroz (blanco|largo fino|doble carolina|grano largo|fino|carolina|elaborado)", r"integral|parboil|yamani|risotto|listo|bolsita|sin tacc|preparad"),
    "Fideos secos tipo guisero": ("01.1.1", r"^fideos? (secos? )?(guiser|codito|codo|tirabuz|mostachol|tallarin|spaghet|tallarines|moño|monito|dedal|rigatt|penne|mostacc)", r"huevo|espinaca|integral|sin gluten|rellen|frescos?\b|verdura"),
    "Hamburguesas congeladas": ("01.1.2", r"^hamburgues", r"pollo|vegetal|veggie|soja|pescado|cerdo|lenteja|garbanzo|quinoa|calabaza|espinaca"),
    "Salchicha tipo viena": ("01.1.2", r"^salchich\w* (tipo )?viena|^salchich\w*", r"parrill|alemana|pollo|vegana|de cerdo"),
    "Aceite de girasol": ("01.1.5", r"^aceite (de )?girasol", r"alto oleico|aerosol|spray|mezcla"),
    "Leche fresca entera en sachet": ("01.1.4", r"^leche (fluida |entera |uat |larga vida |fresca )*(entera)", r"polvo|descrem|parcial|chocolat|sin lactosa|condensad|cabra|vegetal|almendra|deslact|infantil|crecimiento|zero|0%"),
    "Leche en polvo entera": ("01.1.4", r"^leche (en )?polvo entera", r"infantil|nutri|crecimiento|descrem|deslact"),
    "Manteca": ("01.1.5", r"^manteca", r"mani|cacao|light|sin sal"),
    "Yogur firme": ("01.1.4", r"^yogh?(ur|urt) firme", r""),
    "Dulce de leche": ("01.1.8", r"^dulce (de|d) ?leche", r"cabra|light|sin azucar|alfajor|cafe|chocolat"),
    "Tomate entero en conserva": ("01.1.7", r"^tomates? (entero|perita)", r"triturad|pure|salsa|seco|cubitado|cherry"),
    "Arvejas secas remojadas": ("01.1.7", r"^arvejas", r"partid|congelad|seca(s)? partid"),
    "Azúcar": ("01.1.8", r"^azucar (comun |blanca |tipo a |refinad )*", r"impalpable|rubia|negra|mascabo|organica|light|edulcor|sticks?|sobre"),
    "Sal fina": ("01.1.9", r"^sal (fina|de mesa)", r"gruesa|parrill|marina|rosa|light|baja|condiment"),
    "Polvo para flan": ("01.1.8", r"^(postre|polvo).*(flan)|^flan", r"listo|vasito|pote"),
    "Gaseosa base cola": ("01.2.2", r"^(gaseosa|bebida) .*cola|^coca cola|^pepsi", r"zero|light|sin azucar|lata|cafe"),
    "Agua sin gas": ("01.2.2", r"^agua (mineral |de mesa |mineralizada )*(sin gas|natural)?", r"con gas|c gas|saboriz|\bsab\b|aquarius|levite|tonica|gasificad|sodas?\b|bidon|limon|pomelo|manzana|pera|durazno|naranja|uva"),
    "Café molido": ("01.2.1", r"^cafe (molido|torrado molido|tostado molido)", r"capsula|instantane|grano|descaf"),
    "Yerba mate": ("01.2.1", r"^yerba( mate)?", r"compuesta|hierbas|saborizad|naranja|limon|menta|boldo|mate cocido|saquito|cocido"),
}


def actualizar_precios_indec() -> pd.DataFrame:
    """Baja el cuadro de precios promedio del GBA (INDEC) y lo guarda largo: mes, variedad, precio."""
    import io, subprocess
    raw = subprocess.run(["curl", "-sSL", "--retry", "3", "--max-time", "120", URL_PRECIOS], capture_output=True, check=True).stdout
    g = pd.read_excel(io.BytesIO(raw), sheet_name="GBA", header=None)
    fila_mes = g.iloc[3]
    anio = g.iloc[2].ffill()
    meses_txt = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
    cols = {}
    for j in range(2, g.shape[1]):
        m, a = str(fila_mes[j]).strip().lower(), re.findall(r"\d{4}", str(anio[j]))
        if m in meses_txt and a:
            cols[j] = pd.Timestamp(int(a[0]), meses_txt.index(m) + 1, 1)
    filas = []
    for i in range(4, g.shape[0]):
        v = g.iloc[i, 0]
        if not isinstance(v, str) or not isinstance(g.iloc[i, 1], str):
            continue
        for j, mes in cols.items():
            p = pd.to_numeric(g.iloc[i, j], errors="coerce")
            if pd.notna(p):
                filas.append({"mes": mes.strftime("%Y-%m"), "variedad": v.strip(), "precio": float(p)})
    t = pd.DataFrame(filas)
    RUTA_INDEC.parent.mkdir(parents=True, exist_ok=True)
    t.to_csv(RUTA_INDEC, index=False)
    return t


def emparejar() -> pd.DataFrame:
    """EAN de SEPA -> variedad INDEC, según la descripción."""
    warnings.filterwarnings("ignore", "This pattern is interpreted as a regular expression")
    d = pd.read_csv(sepa.SALIDA / "descripciones.csv", dtype=str)
    d["n"] = d.desc.map(normalizar)
    out = []
    for var, (clase, inc, exc) in VARIEDADES.items():
        m = d[d.n.str.contains(inc, regex=True) & (~d.n.str.contains(exc, regex=True) if exc else True)]
        out.append(m.assign(variedad=var, clase_v=clase)[["id_producto", "variedad", "clase_v", "desc"]])
    return pd.concat(out).drop_duplicates("id_producto")


def variaciones_variedades(meses: list[str], corte=None) -> pd.DataFrame:
    """Variación % mensual de cada variedad según SEPA (Jevons de los EAN emparejados, por región)."""
    emp = emparejar()[["id_producto", "variedad", "clase_v"]]
    filas = []
    prev = None
    for m in sorted(set(meses) | {(pd.Period(min(meses)) - 1).strftime("%Y-%m")}):
        pm = sepa.promedios_mensuales([m], corte=None, origen=sepa.CACHE)
        if not pm.empty:
            pm = pm.merge(emp, on="id_producto")
        act = sepa.promedios_mensuales([m], corte=corte, origen=sepa.CACHE) if corte else pm
        if corte and not act.empty:
            act = act.merge(emp, on="id_producto")
        if prev is not None and not act.empty and m in meses:
            x = prev.merge(act, on=["id_comercio", "region", "id_producto", "variedad", "clase_v"], suffixes=("_0", "_1"))
            x = x[(x.dias_0 >= 8) & (x.dias_1 >= 3)]
            x["r"] = (x.p_1 / x.p_0).clip(0.6, 1.67)
            for (reg, var, cl), g in x.groupby(["region", "variedad", "clase_v"]):
                if len(g) >= 3:
                    filas.append({"mes": m, "region": reg, "variedad": var, "clase": cl,
                                  "var_%": (np.exp(np.log(g.r).mean()) - 1) * 100, "productos": len(g)})
        prev = pm if not pm.empty else None
    return pd.DataFrame(filas)
