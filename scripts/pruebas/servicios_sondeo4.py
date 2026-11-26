"""Cuarta vuelta: hosts y rutas que usan los bundles de tucan.la (menús de restaurantes) y de Burger King para cargar
el menú con precios. Salida: reports/prueba_servicios4.md"""
import re
import subprocess
from pathlib import Path
from urllib.parse import urljoin

OUT = Path(__file__).resolve().parents[2] / "reports" / "prueba_servicios4.md"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"


def get(url, t=30):
    r = subprocess.run(["curl", "-sSL", "--compressed", "--max-time", str(t), "-A", UA, "-w", "\n__HTTP__%{http_code}", url], capture_output=True)
    out = r.stdout
    i = out.rfind(b"\n__HTTP__")
    return (out[:i] if i >= 0 else out).decode("utf-8", "ignore"), (out[i + 9:].decode() if i >= 0 else "000")


L = ["# Sondeo 4", ""]
for pagina in ("https://pedir.tucan.la/menu/almacen-de-pizzas", "https://www.burgerking.com.ar/"):
    html, c = get(pagina)
    scripts = [urljoin(pagina, s) for s in re.findall(r'<script[^>]+src="([^"]+)"', html)]
    hosts, rutas = set(), set()
    for s in scripts[:25]:
        js, _ = get(s)
        hosts |= set(re.findall(r"https://[a-zA-Z0-9.\-]+\.[a-z]{2,}(?:/[a-zA-Z0-9_\-/.]{0,60})?", js))
        for m in re.finditer(r"(?:fetch|get|post|axios)\s*\(\s*[`'\"]([^`'\"]{3,120})", js):
            rutas.add(m.group(1))
        for m in re.finditer(r"[`'\"](/[a-zA-Z0-9_\-]+/[a-zA-Z0-9_\-/${}.]{2,100})[`'\"]", js):
            if any(k in m.group(1).lower() for k in ("menu", "product", "store", "shop", "item", "categor", "catalog", "price")):
                rutas.add(m.group(1))
    L += [f"## {pagina}", f"- {len(scripts)} scripts",
          "- hosts: " + " · ".join(sorted(h for h in hosts if not any(x in h for x in ("google", "facebook", "sentry", "w3.org", "schema.org", "reactjs", "github", "mozilla")))[:60]),
          "- rutas: " + " · ".join(sorted(rutas)[:60]), ""]
OUT.write_text("\n".join(L), encoding="utf-8")
print("\n".join(L)[:5000])
