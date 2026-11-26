"""Tercera vuelta: guarda muestras crudas de las fuentes que respondieron con precios, para armar los parsers.
Salida: reports/prueba_servicios3/ (archivos chicos de muestra)."""
import json
import re
import subprocess
from pathlib import Path

DIR = Path(__file__).resolve().parents[2] / "reports" / "prueba_servicios3"
DIR.mkdir(parents=True, exist_ok=True)
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"


def get(url, t=30, extra=()):
    r = subprocess.run(["curl", "-sSL", "--compressed", "--max-time", str(t), "--connect-timeout", "10", "-A", UA,
                        "-H", "Accept-Language: es-AR,es;q=0.9", *extra, "-w", "\n__HTTP__%{http_code}", url], capture_output=True)
    out = r.stdout
    i = out.rfind(b"\n__HTTP__")
    return (out[:i] if i >= 0 else out).decode("utf-8", "ignore"), (out[i + 9:].decode() if i >= 0 else "000")


log = []

# 1. tucan.la: __NEXT_DATA__ del menú
for alias in ("almacen-de-pizzas",):
    html, c = get(f"https://pedir.tucan.la/menu/{alias}")
    m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html, re.S)
    if m:
        (DIR / f"tucan_{alias}.json").write_text(m.group(1)[:400000], encoding="utf-8")
        log.append(f"tucan {alias}: HTTP {c}, next_data {len(m.group(1)):,} bytes, 'price' x{m.group(1).count('price')}")
    # el menú puede venir de la API propia
    for path in (f"/api/menu/{alias}", f"/api/store/{alias}", "/api/manifest/" + alias):
        b, c2 = get("https://pedir.tucan.la" + path, 20)
        log.append(f"tucan {path}: HTTP {c2}, {len(b):,} bytes, 'price' x{b.count('price')}")
        if c2 == "200" and len(b) > 200:
            (DIR / ("tucan" + path.replace("/", "_") + ".txt")).write_text(b[:200000], encoding="utf-8")

# 2. Aerolíneas: ofertas publicadas
for path in ("/api/best_offers", "/api/best_offers?origin=BUE", "/api/home_page_container", "/api/main_slider"):
    b, c = get("https://www.aerolineas.com.ar" + path, 30, ("-H", "Accept: application/json"))
    log.append(f"aerolineas {path}: HTTP {c}, {len(b):,} bytes, '$'/price x{b.count('price') + b.count('$')}")
    if c == "200":
        (DIR / ("aerolineas" + path.replace("/", "_").replace("?", "_") + ".txt")).write_text(b[:200000], encoding="utf-8")

# 3. Central de Pasajes: resultado de búsqueda de micros (HTML)
for o, d in (("retiro-buenos-aires", "cordoba"), ("retiro-buenos-aires", "mar-del-plata"), ("retiro-buenos-aires", "rosario")):
    url = f"https://www.centraldepasajes.com.ar/cdp/pasajes-micro/{o}/{d}/?DIda=1&CntPas=1"
    html, c = get(url, 40)
    log.append(f"cdp {o}->{d}: HTTP {c}, {len(html):,} bytes")
    trozos = []
    for mm in re.finditer(r"\$\s?\d{1,3}(?:\.\d{3})+", html):
        trozos.append(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html[max(0, mm.start() - 600):mm.end() + 100])))
    (DIR / f"cdp_{d}.txt").write_text("\n-----\n".join(trozos[:20]), encoding="utf-8")

# 4. Plataforma10: API del front
for path in ("/api", "/api/v2/", "/api/v2/stops"):
    b, c = get("https://p10-backend-for-frontend.prd.plataforma10.com" + path, 20)
    log.append(f"p10 {path}: HTTP {c}, {len(b):,} bytes: {b[:200]!r}")

(DIR / "log.md").write_text("\n".join(log), encoding="utf-8")
print("\n".join(log))
