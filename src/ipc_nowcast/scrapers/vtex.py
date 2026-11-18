"""Scraper de supermercados que usan la plataforma VTEX (catálogo público).

Recorre el árbol de categorías de cada cadena y baja todos los productos con su precio del día.
API usada (pública, sin login):
    /api/catalog_system/pub/category/tree/3                       árbol de categorías
    /api/io/_v/api/intelligent-search/product_search/<facetas>    productos (solo con stock)
VTEX limita la paginación a 2.500 resultados por consulta: si una categoría tiene más,
se baja nivel por nivel en el árbol.
"""
from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import date

import pandas as pd

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"

CADENAS = {
    "carrefour": "https://www.carrefour.com.ar",
    "jumbo": "https://www.jumbo.com.ar",
    "disco": "https://www.disco.com.ar",
    "vea": "https://www.vea.com.ar",
    "dia": "https://diaonline.supermercadosdia.com.ar",
}

# Tiendas de ropa, calzado y electrónica (mismo sistema VTEX). Se relevan desde nov-2026 para tener historia y
# poder probar, cuando alcance, si anticipan ropa (03) y equipamiento/electrónica (05, 09.1).
TIENDAS = {
    "equus": "https://www.equus.com.ar",
    "portsaid": "https://www.portsaid.com.ar",
    "tascani": "https://www.tascani.com.ar",
    "levis": "https://www.levi.com.ar",
    "legacy": "https://www.legacy.com.ar",
    "mimo": "https://www.mimo.com.ar",
    "topper": "https://www.topper.com.ar",
    "naldo": "https://www.naldo.com.ar",
    "cetrogar": "https://www.cetrogar.com.ar",
    "coppel": "https://www.coppel.com.ar",
}
RUBRO_TIENDA = {"equus": "ropa", "portsaid": "ropa", "tascani": "ropa", "levis": "ropa", "legacy": "ropa", "mimo": "ropa",
                "topper": "calzado", "naldo": "electro", "cetrogar": "electro", "coppel": "electro"}

# Departamentos que no aportan al IPC (o duplican otros) y se saltean
EXCLUIR = {"test category", "gift cards", "garantía extendida", "sin categoría", "combos", "felices fiestas",
           "luces c/toma", "huevos de pascua"}

PAGINA = 50
TOPE_VTEX = 2500  # 50 páginas x 50


def _get(url: str, intentos: int = 4) -> tuple[list | dict, dict]:
    for i in range(intentos):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read()), dict(r.headers)
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and i < intentos - 1:
                time.sleep(2 * (i + 1))
                continue
            raise
        except (urllib.error.URLError, TimeoutError):
            if i < intentos - 1:
                time.sleep(2 * (i + 1))
                continue
            raise
    raise RuntimeError(url)


def _ruta_facetas(url: str) -> str:
    """'https://www.jumbo.com.ar/almacen/aceites-y-vinagres' -> 'category-1/almacen/category-2/aceites-y-vinagres'"""
    partes = [x for x in urllib.parse.urlparse(url).path.split("/") if x]
    return "/".join(f"category-{i + 1}/{p}" for i, p in enumerate(partes))


def _buscar(base: str, facetas: str, pagina: int, cantidad: int = PAGINA) -> tuple[list, int]:
    """Intelligent Search de VTEX: solo productos con stock (hideUnavailableItems)."""
    url = (f"{base}/api/io/_v/api/intelligent-search/product_search/{facetas}"
           f"?count={cantidad}&page={pagina}&hideUnavailableItems=true")
    datos, _ = _get(url)
    return datos.get("products", []), int(datos.get("recordsFiltered") or 0)


def _consultas(base: str) -> list[tuple[str, int]]:
    """Rutas de categoría con su total, de modo que cada una tenga <= 2.500 productos con stock."""
    arbol, _ = _get(f"{base}/api/catalog_system/pub/category/tree/3")
    rutas = []

    def bajar(nodo):
        facetas = _ruta_facetas(nodo.get("url", ""))
        if not facetas:
            return
        _, total = _buscar(base, facetas, 1, 1)
        if total <= TOPE_VTEX or not nodo.get("children"):
            if total:
                rutas.append((facetas, total))
        else:
            for h in nodo["children"]:
                bajar(h)

    for dep in arbol:
        if dep["name"].strip().lower() in EXCLUIR:
            continue
        bajar(dep)
    return rutas


def _filas(productos: list, cadena: str) -> list[dict]:
    filas = []
    for p in productos:
        cats = p.get("categories") or [""]
        for it in p.get("items", []):
            sellers = it.get("sellers") or []
            if not sellers:
                continue
            o = sellers[0].get("commertialOffer", {})
            if not o or (o.get("AvailableQuantity") or 0) <= 0:
                continue
            teasers = [t.get("<Name>k__BackingField") or t.get("name") or t.get("Name")
                       for t in (o.get("Teasers") or o.get("teasers") or [])]
            filas.append({
                "cadena": cadena,
                "producto_id": str(p.get("productId")),
                "item_id": str(it.get("itemId")),
                "ean": it.get("ean") or None,
                "nombre": it.get("nameComplete") or p.get("productName"),
                "marca": p.get("brand"),
                "categoria": cats[0],
                "unidad": it.get("measurementUnit"),
                "multiplicador": it.get("unitMultiplier"),
                "precio": o.get("Price"),
                "precio_lista": o.get("ListPrice"),
                "precio_sin_desc": o.get("PriceWithoutDiscount"),
                "promos": "; ".join(t for t in teasers if t)[:200] or None,
            })
    return filas


def scrapear(cadena: str, hilos: int = 6, log=print) -> pd.DataFrame:
    base = CADENAS.get(cadena) or TIENDAS[cadena]
    t0 = time.time()
    rutas = _consultas(base)
    tareas = [(ruta, pag) for ruta, total in rutas for pag in range(1, min(total, TOPE_VTEX) // PAGINA + 2)
              if (pag - 1) * PAGINA < min(total, TOPE_VTEX)]

    def bajar(t):
        try:
            return _filas(_buscar(base, t[0], t[1])[0], cadena)
        except Exception as e:  # noqa: BLE001
            log(f"  ! {cadena} {t}: {e}")
            return []

    with ThreadPoolExecutor(hilos) as ex:
        filas = [f for lote in ex.map(bajar, tareas) for f in lote]
    df = pd.DataFrame(filas)
    if not df.empty:
        df = df.drop_duplicates(["item_id"]).reset_index(drop=True)
        df.insert(0, "fecha", pd.Timestamp(date.today()))
    log(f"{cadena}: {len(rutas)} categorías, {len(tareas)} páginas, {len(df):,} productos, {time.time() - t0:.0f}s")
    return df
