"""Índices de precios propios a partir de los supermercados online.

1. Clasifica cada producto en una clase/grupo de INDEC según su categoría en la web y su nombre.
2. Arma un índice diario por clase (encadenado, media geométrica de relativos del mismo producto día a día,
   como hace INDEC a nivel elemental), primero por cadena y luego promediando cadenas.
3. Resume por mes: promedio mensual del índice (INDEC compara promedios), variación en lo que va del mes
   y arrastre hacia el mes siguiente.
"""
from __future__ import annotations

import re
import unicodedata

import numpy as np
import pandas as pd

from . import DATA

DIR = DATA / "precios" / "supermercados"

NOMBRES = {
    "01.1.1": "Pan y cereales", "01.1.2": "Carnes y derivados", "01.1.4": "Leche, lácteos y huevos",
    "01.1.5": "Aceites, grasas y manteca", "01.1.6": "Frutas", "01.1.7": "Verduras, tubérculos y legumbres",
    "01.1.8": "Azúcar, dulces, chocolate, golosinas", "01.1.resto": "Otros alimentos (pescados, condimentos, etc.)",
    "01.2.1": "Café, té, yerba y cacao", "01.2.2": "Aguas, gaseosas y jugos", "02.1": "Bebidas alcohólicas",
    "05.6": "Limpieza y conservación del hogar", "06.1": "Productos medicinales", "12.1": "Cuidado personal",
}

# Reglas en orden: la primera que coincide gana. Se aplican sobre texto sin acentos y en minúscula.
REGLAS_ALIMENTOS = [
    ("02.1", r"vino|cerveza|bodega|espumante|sidra|fernet|aperitivo|bebidas blancas|destilado|whisk|licor|vodka|\bgin\b"),
    ("01.1.1", r"galletit|bizcoch|tostada|budin|magdalena"),
    ("01.1.8", r"helado"),
    ("01.1.resto", r"snack|papas fritas|palitos|\bmani\b|mayonesa|mostaza|ketchup|aderezo|encurtido|aceituna|pickle"),
    ("01.2.1", r"yerba|\bcafe|infusion|\bte\b|mate cocido|cacao"),
    ("01.2.2", r"\baguas?\b|gaseosa|jugo|isotonic|energizante|soda|a base de hierbas"),
    ("01.1.4", r"dulce de leche|leche|lacteo|yogur|queso|crema|huevo|postre"),
    ("01.1.5", r"aceite|manteca|margarina|grasa"),
    ("01.1.2", r"carne|pollo|cerdo|embutido|fiambre|salchicha|achura|hamburgues|milanesa|medallon|menudencia|granja|\baves\b"),
    ("01.1.6", r"\bfruta|frutos secos"),
    ("01.1.7", r"verdura|legumbre|\bpapas?\b|hortaliza|vegetal"),
    ("01.1.8", r"golosina|chocolate|alfajor|mermelada|dulce|azucar|endulzante|helado|caramelo|untable"),
    ("01.1.1", r"\bpan\b|panader|panific|harina|arroz|pasta|fideo|galletit|cereal|bizcoch|budin|magdalena|tostada|reposteria|tapas|pizza|masas"),
    ("01.1.resto", r"aderezo|\bsal\b|especia|conserva|enlatad|caldo|sopa|snack|comida|rotiseria|listos|encurtido|pescad|marisco|salsa|para preparar|congelad|picada|vinagre|pure"),
]
DEP_LIMPIEZA = r"^/?limpieza"
DEP_PERFUMERIA = r"^/?(perfumeria|mundo bebe|bebes y ninos)"
DEP_EXCLUIDOS = r"^/?(electro|hogar|tiempo libre|jugueteria|indumentaria|aire libre|automotor|mascotas|tecnologia|garantia|gift)"


def _norm(s) -> str:
    return unicodedata.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode().lower()


def clasificar(categoria: str, nombre: str) -> str | None:
    cat, nom = _norm(categoria), _norm(nombre)
    if re.search(DEP_EXCLUIDOS, cat):
        return None
    if re.search(DEP_LIMPIEZA, cat):
        return "05.6"
    partes = [p for p in cat.split("/") if p]
    if re.search(DEP_PERFUMERIA, cat) and not re.search(r"aliment|leche|lactancia|papilla|cereal", cat):
        return "06.1" if re.search(r"farmacia|botiquin", "/".join(partes[1:])) else "12.1"
    for texto in [partes[-1] if partes else "", "/".join(partes[-2:]), cat, nom]:
        for clase, patron in REGLAS_ALIMENTOS:
            if re.search(patron, texto):
                return clase
    return None


def cargar_panel() -> pd.DataFrame:
    """Todos los precios diarios con la clase INDEC de cada producto."""
    archivos = sorted((DIR / "diario").glob("*/*.parquet"))
    if not archivos:
        return pd.DataFrame()
    partes = []
    for a in archivos:
        fecha, cadena = a.stem.split("_", 1)
        df = pd.read_parquet(a, columns=["item_id", "precio"])
        df["fecha"], df["cadena"] = pd.Timestamp(fecha), cadena
        partes.append(df)
    panel = pd.concat(partes, ignore_index=True)
    cats = []
    for cadena in panel.cadena.unique():
        c = pd.read_parquet(DIR / f"catalogo_{cadena}.parquet", columns=["item_id", "categoria", "nombre"])
        c["clase"] = [clasificar(x, y) for x, y in zip(c.categoria, c.nombre)]
        c["cadena"] = cadena
        cats.append(c[["cadena", "item_id", "clase"]])
    panel = panel.merge(pd.concat(cats), on=["cadena", "item_id"], how="left")
    return panel[panel.clase.notna() & (panel.precio > 0)]


def indices_diarios(panel: pd.DataFrame, recorte=(0.6, 1.67)) -> pd.DataFrame:
    """Índice diario encadenado por clase (base: primer día = 100). Columnas = clases."""
    if panel.empty or panel.fecha.nunique() < 2:
        return pd.DataFrame()
    p = panel.pivot_table(index=["cadena", "clase", "item_id"], columns="fecha", values="precio")
    fechas = list(p.columns)
    rel = np.log(p[fechas[1:]].values / p[fechas[:-1]].values)
    rel = pd.DataFrame(rel, index=p.index, columns=fechas[1:])
    rel = rel.where((rel > np.log(recorte[0])) & (rel < np.log(recorte[1])))
    # Jevons por cadena y clase, luego promedio simple entre cadenas
    por_cadena = rel.groupby(level=["cadena", "clase"]).mean()
    por_clase = por_cadena.groupby(level="clase").mean().T.fillna(0)
    idx = np.exp(por_clase.cumsum()) * 100
    inicio = pd.DataFrame(100.0, index=[fechas[0]], columns=idx.columns)
    return pd.concat([inicio, idx]).sort_index()


def resumen_mensual(idx: pd.DataFrame, min_dias: int = 8) -> pd.DataFrame:
    """Por clase y mes: promedio del índice, variación vs. mes anterior (si hay datos), en lo que va del mes y arrastre."""
    if idx.empty:
        return pd.DataFrame()
    filas = []
    meses = sorted({pd.Timestamp(f.year, f.month, 1) for f in idx.index})
    for m in meses:
        dentro = idx[(idx.index.year == m.year) & (idx.index.month == m.month)]
        for clase in idx.columns:
            s = dentro[clase].dropna()
            if s.empty:
                continue
            filas.append({"mes": m, "clase": clase, "dias": len(s), "promedio": s.mean(),
                          "en_el_mes_%": (s.iloc[-1] / s.iloc[0] - 1) * 100,
                          "arrastre_%": (s.iloc[-1] / s.mean() - 1) * 100, "ultimo": s.iloc[-1]})
    r = pd.DataFrame(filas).sort_values(["clase", "mes"])
    r["var_mensual_%"] = np.where(
        (r.groupby("clase").dias.shift(1) >= min_dias) & (r.dias >= min_dias),
        (r.promedio / r.groupby("clase").promedio.shift(1) - 1) * 100, np.nan)
    return r
