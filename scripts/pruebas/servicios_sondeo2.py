"""Segunda vuelta del sondeo: para las páginas de menú y de pasajes que son aplicaciones (SPA), busca en el HTML y en
sus bundles de JavaScript las direcciones de las API que cargan los precios, y prueba las más probables.
Salida: reports/prueba_servicios2.md"""
import re
import subprocess
from pathlib import Path
from urllib.parse import urljoin

OUT = Path(__file__).resolve().parents[2] / "reports" / "prueba_servicios2.md"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"
PRECIO = re.compile(r"\$\s?\d{1,3}(?:\.\d{3})+(?:,\d{2})?|\$\s?\d{4,}")
API = re.compile(r"""["'`](https?://[a-zA-Z0-9.\-]*(?:api|graphql|backend|gateway|services?)[a-zA-Z0-9.\-]*[^"'`\s]{0,80})["'`]""")
RUTA = re.compile(r"""["'`](/(?:api|v\d|graphql)[^"'`\s]{0,80})["'`]""")

PAGINAS = [
    "https://pedir.tucan.la/menu/almacen-de-pizzas",
    "https://www.wendys.com.ar/",
    "https://www.migusto.com.ar/cartadigital",
    "https://www.plataforma10.com.ar/pasajes-en-micro/bahia-blanca",
    "https://www.centraldepasajes.com.ar/cdp/pasajes-micro/retiro-buenos-aires/cordoba/?DIda=1&CntPas=1",
    "https://www.burgerking.com.ar/",
    "https://mostaza.com.ar/productos/",
    "https://www.aerolineas.com.ar/",
]


def get(url, t=25, extra=()):
    r = subprocess.run(["curl", "-sSL", "--compressed", "--max-time", str(t), "--connect-timeout", "10", "-A", UA,
                        "-H", "Accept-Language: es-AR,es;q=0.9", *extra, "-w", "\n__HTTP__%{http_code}", url], capture_output=True)
    out = r.stdout
    i = out.rfind(b"\n__HTTP__")
    return (out[:i] if i >= 0 else out).decode("utf-8", "ignore"), (out[i + 9:].decode() if i >= 0 else "000")


L = ["# Sondeo 2: API detrás de menús y pasajes", ""]
for url in PAGINAS:
    html, code = get(url)
    L += [f"## {url}", f"- HTTP {code}, {len(html):,} bytes, {len(PRECIO.findall(html))} precios en el HTML",
          f"- título: {(re.findall(r'<title>([^<]{0,120})', html) or [''])[0]}"]
    scripts = [urljoin(url, s) for s in re.findall(r'<script[^>]+src="([^"]+)"', html)][:12]
    apis, rutas = set(API.findall(html)), set(RUTA.findall(html))
    for s in scripts:
        js, c = get(s, 25)
        apis |= set(API.findall(js))
        rutas |= set(RUTA.findall(js))
    L.append(f"- scripts: {len(scripts)}")
    L.append("- API absolutas: " + " · ".join(sorted(apis)[:25]))
    L.append("- rutas relativas: " + " · ".join(sorted(rutas)[:25]))
    # JSON embebido con precios (Next/Nuxt)
    for k in ("__NEXT_DATA__", "__NUXT__", "window.__INITIAL_STATE__", "apolloState"):
        if k in html:
            i = html.find(k)
            L.append(f"- {k} embebido: …{html[i:i + 400]!r}")
    L.append("")
OUT.write_text("\n".join(L), encoding="utf-8")
print("\n".join(L)[:4000])
