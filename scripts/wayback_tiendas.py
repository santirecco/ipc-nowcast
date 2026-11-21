"""Reconstruye historia de precios de tiendas de ropa y electro con el archivo web (Wayback Machine).

Por tienda: lista las páginas de producto archivadas desde 2023 y arma un panel: por mes, hasta POR_MES productos con
copias en 2 meses o más, priorizando los que más meses duran (para comparar el mismo producto) y extrae el precio publicado.
Precios publicados en su momento: usarlos para el pasado es honesto. Se puede cortar y retomar.
Salida: data/precios/wayback/<tienda>.csv (url, mes, timestamp, precio).
"""
import json
import re
import sys
import time
import urllib.request
from collections import defaultdict
from pathlib import Path

DIR = Path(__file__).resolve().parents[1] / "data" / "precios" / "wayback"
UA = "Mozilla/5.0 (ipc-nowcast; investigación)"
TIENDAS = {"tascani": ("www.tascani.com.ar", "ropa"), "levis": ("www.levi.com.ar", "ropa"),
           "portsaid": ("www.portsaid.com.ar", "ropa"), "equus": ("www.equus.com.ar", "ropa"),
           "coppel": ("www.coppel.com.ar", "electro"), "naldo": ("www.naldo.com.ar", "electro"),
           "pardo": ("www.pardo.com.ar", "electro"), "cetrogar": ("www.cetrogar.com.ar", "electro")}
LIMITE_SEG = 4 * 3600 + 1800  # cortar antes del límite del job (300 min)


def get(url, timeout=60, intentos=3):
    for i in range(intentos):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read().decode("utf-8", "replace")
        except Exception:  # noqa: BLE001
            if i == intentos - 1:
                raise
            time.sleep(4 * (i + 1))


def precio(html: str):
    """Precio del producto: JSON-LD de tipo Product (precio u oferta más baja); si no, primer "price" de la página."""
    for m in re.finditer(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>', html, re.S):
        try:
            d = json.loads(m.group(1).strip())
        except Exception:  # noqa: BLE001
            continue
        for o in (d if isinstance(d, list) else [d]):
            if isinstance(o, dict) and str(o.get("@type", "")).lower() == "product":
                of = o.get("offers") or {}
                of = of[0] if isinstance(of, list) and of else of
                for k in ("lowPrice", "price"):
                    v = of.get(k) if isinstance(of, dict) else None
                    if v not in (None, "", 0, "0"):
                        try:
                            return float(str(v).replace(",", "."))
                        except ValueError:
                            pass
    m = re.search(r'"(?:bestPrice|Price|price)"\s*:\s*"?([0-9]+(?:\.[0-9]+)?)', html)
    return float(m.group(1)) if m else None


POR_MES = 40         # productos por tienda y mes (panel: los que más meses duran, para comparar el mismo producto)
HILOS = 2


def tareas_tienda(nombre, dominio, ruta):
    """Copias pendientes de una tienda: por mes, hasta POR_MES productos, priorizando los de vida más larga."""
    hechas, por_mes_hecho = set(), defaultdict(int)
    if ruta.exists():
        for ln in ruta.read_text().splitlines()[1:]:
            if ln:
                c = ln.split(",")
                hechas.add(c[2])
                por_mes_hecho[c[1]] += 1
    else:
        ruta.write_text("url,mes,timestamp,precio\n")
    q = (f"https://web.archive.org/cdx/search/cdx?url={dominio}/*&from=2023&filter=statuscode:200"
         f"&filter=original:.*/p$&fl=timestamp,original&output=json&limit=300000")
    filas = json.loads(get(q, 300) or "[]")[1:]
    por = defaultdict(dict)  # url -> mes -> timestamp (la copia más cercana al día 15)
    for ts, url in filas:
        url = url.split("?")[0].replace("http://", "https://")
        m = ts[:6]
        if m not in por[url] or abs(int(ts[6:8]) - 15) < abs(int(por[url][m][6:8]) - 15):
            por[url][m] = ts
    vida = {u: len(ms) for u, ms in por.items() if len(ms) >= 2}
    meses = sorted({m for u in vida for m in por[u]})
    out = []
    for m in meses:
        cand = sorted((u for u in vida if m in por[u]), key=lambda u: (-vida[u], u))
        libres = max(0, POR_MES - por_mes_hecho[m])
        pend = [u for u in cand if por[u][m] not in hechas]
        # los de vida más larga primero: así el mismo producto aparece en meses seguidos
        out += [(u, m, por[u][m]) for u in pend[:libres]]
    print(nombre, f"{len(vida)} productos con 2+ meses, {len(meses)} meses, {len(out)} copias pendientes", flush=True)
    return out


def main():
    from concurrent.futures import ThreadPoolExecutor
    DIR.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    colas, archivos = {}, {}
    for nombre, (dominio, rubro) in TIENDAS.items():
        ruta = DIR / f"{nombre}.csv"
        try:
            colas[nombre] = tareas_tienda(nombre, dominio, ruta)
        except Exception as e:  # noqa: BLE001
            print(nombre, "cdx error", e, flush=True)
            continue
        archivos[nombre] = open(ruta, "a")
    # todas las tiendas a la vez (una copia de cada una por turno), en orden de mes
    orden = []
    k = 0
    while any(k < len(c) for c in colas.values()):
        orden += [(n, *c[k]) for n, c in colas.items() if k < len(c)]
        k += 1

    def bajar(t):
        n, u, m, ts = t
        try:
            return t, precio(get(f"https://web.archive.org/web/{ts}id_/{u}"))
        except Exception:  # noqa: BLE001
            return t, None

    hechas = 0
    with ThreadPoolExecutor(HILOS) as ex:
        for i in range(0, len(orden), 20):
            if time.time() - t0 > LIMITE_SEG:
                print("tiempo agotado: sigue en la próxima corrida", flush=True)
                break
            for (n, u, m, ts), p in ex.map(bajar, orden[i:i + 20]):
                # sin precio (página sin precio legible o copia caída): se anota vacío para no reintentarla siempre
                archivos[n].write(f"{u},{m},{ts},{'' if p is None else p}\n")
                archivos[n].flush()
                hechas += 1
            print(f"{min(i + 20, len(orden))}/{len(orden)} copias ({hechas} con precio)", flush=True)
            time.sleep(1)
    for f in archivos.values():
        f.close()


if __name__ == "__main__":
    main()
