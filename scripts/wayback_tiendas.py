"""Reconstruye historia de precios de tiendas de ropa y electro con el archivo web (Wayback Machine).

Por tienda: lista las páginas de producto archivadas desde 2024, elige una copia por producto y por mes (solo
productos con copias en 2 meses o más, para poder comparar el mismo producto) y extrae el precio publicado.
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
TOPE = 2500          # copias por tienda y corrida
LIMITE_SEG = 5 * 3600 - 600  # cortar antes del límite del job


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


def main():
    DIR.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    for nombre, (dominio, rubro) in TIENDAS.items():
        ruta = DIR / f"{nombre}.csv"
        hechas = set()
        if ruta.exists():
            hechas = {ln.split(",")[2] for ln in ruta.read_text().splitlines()[1:] if ln}
        else:
            ruta.write_text("url,mes,timestamp,precio\n")
        try:
            q = (f"https://web.archive.org/cdx/search/cdx?url={dominio}/*&from=2024&filter=statuscode:200"
                 f"&filter=original:.*/p$&fl=timestamp,original&output=json&limit=200000")
            filas = json.loads(get(q, 300) or "[]")[1:]
        except Exception as e:  # noqa: BLE001
            print(nombre, "cdx error", e, flush=True)
            continue
        por = defaultdict(dict)  # url -> mes -> timestamp (la copia del medio del mes)
        for ts, url in filas:
            url = url.split("?")[0].replace("http://", "https://")
            m = ts[:6]
            if m not in por[url] or abs(int(ts[6:8]) - 15) < abs(int(por[url][m][6:8]) - 15):
                por[url][m] = ts
        tareas = [(u, m, ts) for u, ms in por.items() if len(ms) >= 2 for m, ts in ms.items() if ts not in hechas]
        print(nombre, rubro, f"{len(por)} productos, {len(tareas)} copias pendientes", flush=True)
        n = 0
        with open(ruta, "a") as f:
            for u, m, ts in sorted(tareas, key=lambda x: (x[1], x[0]))[:TOPE]:
                if time.time() - t0 > LIMITE_SEG:
                    print("tiempo agotado: sigue en la próxima corrida", flush=True)
                    return
                try:
                    p = precio(get(f"https://web.archive.org/web/{ts}id_/{u}"))
                except Exception:  # noqa: BLE001
                    p = None
                f.write(f"{u},{m},{ts},{'' if p is None else p}\n")
                f.flush()
                n += 1
                if n % 200 == 0:
                    print(nombre, n, flush=True)
                time.sleep(0.8)


if __name__ == "__main__":
    main()
