"""Octava vuelta: todas las rutas /api/ que arma el front de Tucán (con .concat) y prueba de las candidatas para bajar
el menú con precios a partir del hash. Salida: reports/prueba_servicios8/"""
import json
import re
import subprocess
from pathlib import Path
from urllib.parse import urljoin

DIR = Path(__file__).resolve().parents[2] / "reports" / "prueba_servicios8"
DIR.mkdir(parents=True, exist_ok=True)
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"


def get(url, t=30):
    r = subprocess.run(["curl", "-sSL", "--compressed", "--max-time", str(t), "-A", UA, "-H", "Accept: application/json",
                        "-H", "Origin: https://pedir.tucan.la", "-H", "Referer: https://pedir.tucan.la/",
                        "-w", "\n__HTTP__%{http_code}", url], capture_output=True)
    out = r.stdout
    i = out.rfind(b"\n__HTTP__")
    return (out[:i] if i >= 0 else out).decode("utf-8", "ignore"), (out[i + 9:].decode() if i >= 0 else "000")


L = []
pagina = "https://pedir.tucan.la/menu/almacen-de-pizzas"
html, _ = get(pagina)
scripts = [urljoin(pagina, s) for s in re.findall(r'<script[^>]+src="([^"]+)"', html)]
bm = [s for s in scripts if "_buildManifest" in s]
if bm:
    js, _ = get(bm[0])
    scripts += [urljoin(pagina, "/_next/" + s) for s in set(re.findall(r'"(static/chunks/[^"]+\.js)"', js))]
rutas = set()
for s in scripts:
    js, _ = get(s)
    for m in re.finditer(r'"(/api/[a-zA-Z0-9_\-/]*)"(\.concat\([^)]{0,60}\)(?:\.concat\([^)]{0,60}\)|,"[^"]{0,30}"){0,4})?', js):
        rutas.add(m.group(0)[:200])
    for m in re.finditer(r"hash", js):
        ctx = js[max(0, m.start() - 120):m.end() + 120]
        if "concat" in ctx and ("menu" in ctx.lower()):
            rutas.add("CTX: " + ctx)
L += ["## rutas"] + sorted(rutas)[:200]

# candidatas para el menú
mid, menu_id, h = 11928, 2, None
b, c = get(f"https://app.loveat.la/api/diner/menu/{mid}/hash?orderModeId=2&")
try:
    h = json.loads(b)["menuHashes"][0]["hash"]
except Exception:  # noqa: BLE001
    pass
L.append(f"## hash {h}")
for u in (f"https://app.loveat.la/api/diner/menu/{mid}/{menu_id}/{h}", f"https://app.loveat.la/api/diner/menu/{mid}/{menu_id}?hash={h}",
          f"https://app.loveat.la/api/diner/menu/{mid}?menuId={menu_id}&orderModeId=2", f"https://app.loveat.la/api/diner/menu/{mid}/{menu_id}",
          f"https://app.loveat.la/api/diner/menu/{mid}/2/full", f"https://app.loveat.la/api/diner/menu/{h}",
          f"https://images.loveat.la/menus/{h}.json", f"https://app.loveat.la/api/diner/menu/{mid}/orderMode/2"):
    b, c = get(u)
    L.append(f"- {u}: HTTP {c}, {len(b):,} bytes, price x{b.lower().count('price')}: {b[:200]!r}")
    if c == "200" and len(b) > 300:
        (DIR / (re.sub(r'[^a-zA-Z0-9]+', '_', u[8:])[:80] + ".json")).write_text(b[:500000], encoding="utf-8")
(DIR / "log.md").write_text("\n".join(L), encoding="utf-8")
print("\n".join(L)[-3000:])
