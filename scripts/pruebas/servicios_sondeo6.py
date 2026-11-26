"""Sexta vuelta: contexto de las llamadas /api/diner/menu/ y /api/diner/branches/ en los bundles de Tucán, y prueba
de las URL que arman. Salida: reports/prueba_servicios6.md"""
import re
import subprocess
from pathlib import Path
from urllib.parse import urljoin

OUT = Path(__file__).resolve().parents[2] / "reports" / "prueba_servicios6.md"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"


def get(url, t=30):
    r = subprocess.run(["curl", "-sSL", "--compressed", "--max-time", str(t), "-A", UA, "-H", "Accept: application/json",
                        "-H", "Origin: https://pedir.tucan.la", "-w", "\n__HTTP__%{http_code}", url], capture_output=True)
    out = r.stdout
    i = out.rfind(b"\n__HTTP__")
    return (out[:i] if i >= 0 else out).decode("utf-8", "ignore"), (out[i + 9:].decode() if i >= 0 else "000")


L = ["# Sondeo 6", ""]
pagina = "https://pedir.tucan.la/menu/almacen-de-pizzas"
html, _ = get(pagina)
scripts = [urljoin(pagina, s) for s in re.findall(r'<script[^>]+src="([^"]+)"', html)]
# también los chunks que carga el build (_buildManifest)
bm = [s for s in scripts if "_buildManifest" in s]
if bm:
    js, _ = get(bm[0])
    scripts += [urljoin(pagina, "/_next/" + s) for s in set(re.findall(r'"(static/chunks/[^"]+\.js)"', js))]
for s in scripts:
    js, _ = get(s)
    for k in ("api/diner/menu", "api/diner/branches", "api/menu/near", "products", "getMenu"):
        for m in list(re.finditer(re.escape(k), js))[:3]:
            L.append(f"- `{s.rsplit('/', 1)[-1]}` [{k}]: {js[max(0, m.start() - 250):m.end() + 250]!r}")
OUT.write_text("\n".join(L), encoding="utf-8")
print(len(L))
