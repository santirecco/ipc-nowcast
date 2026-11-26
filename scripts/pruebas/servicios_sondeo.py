"""Sondeo de fuentes de precios para rubros que hoy no se miden: restaurantes y comidas fuera del hogar (división 11)
y turismo (09, pasajes y paquetes). Para cada sitio candidato prueba la portada y las API públicas de las plataformas
de comercio más comunes (VTEX, Shopify, WooCommerce, Tiendanube), cuenta precios visibles y lista enlaces a menús o
pedidos. Salida: reports/prueba_servicios.md (no guarda datos)."""
import json
import re
import subprocess
from pathlib import Path

OUT = Path(__file__).resolve().parents[2] / "reports" / "prueba_servicios.md"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"

RESTAURANTES = [
    "www.mostaza.com.ar", "www.burgerking.com.ar", "www.mcdonalds.com.ar", "www.kfc.com.ar", "www.wendys.com.ar",
    "www.popeyes.com.ar", "www.subway.com/es-AR", "www.kentucky.com.ar", "www.grido.com.ar", "www.freddo.com.ar",
    "www.luccianos.com", "www.persicco.com", "www.cremolatti.com.ar", "www.havanna.com.ar", "www.cafemartinez.com",
    "www.starbucks.com.ar", "www.migusto.com.ar", "www.elnoble.com.ar", "www.guerrin.com", "www.almacendepizzas.com",
    "www.tostado.com.ar", "www.bonafide.com.ar", "www.lapaneterarosa.com", "www.romario.com.ar", "www.sushiclub.com.ar",
    "www.pedidosya.com.ar", "www.rappi.com.ar", "menu.fu.do", "pedix.app", "www.olaclick.com",
]
TURISMO = [
    "www.aerolineas.com.ar", "flybondi.com/ar", "jetsmart.com/ar/es", "www.plataforma10.com.ar",
    "www.centraldepasajes.com.ar", "www.despegar.com.ar", "www.turismocity.com.ar", "www.andesmar.com",
    "www.flechabus.com.ar", "www.viabariloche.com.ar", "www.almundo.com.ar", "www.avantrip.com",
]

PRECIO = re.compile(r"\$\s?\d{1,3}(?:\.\d{3})+(?:,\d{2})?|\$\s?\d{4,}")


def get(url, t=25):
    r = subprocess.run(["curl", "-sSL", "--compressed", "--max-time", str(t), "--connect-timeout", "10", "-A", UA,
                        "-H", "Accept-Language: es-AR,es;q=0.9", "-w", "\n__HTTP__%{http_code} %{url_effective}", url],
                       capture_output=True)
    out = r.stdout
    i = out.rfind(b"\n__HTTP__")
    body = out[:i] if i >= 0 else out
    meta = out[i + 9:].decode(errors="ignore") if i >= 0 else "000 -"
    code, _, final = meta.partition(" ")
    return body.decode("utf-8", "ignore"), code, final


def plataformas(html):
    h = html.lower()
    return [n for n, k in (("vtex", "vtex"), ("shopify", "cdn.shopify"), ("tiendanube", "tiendanube"),
                           ("tiendanube", "nuvemshop"), ("woocommerce", "woocommerce"), ("magento", "mage/"),
                           ("next.js", "__next_data__"), ("fudo", "fu.do"), ("olaclick", "olaclick"),
                           ("pedix", "pedix"), ("pedidosya", "pedidosya"), ("rappi", "rappi"),
                           ("cloudflare-desafio", "cf-chl"), ("captcha", "captcha")) if k in h]


def enlaces(html, base):
    hs = set(re.findall(r'href="([^"#]+)"', html))
    claves = ("menu", "carta", "pedid", "delivery", "tienda", "shop", "productos", "vuelos", "pasajes", "paquetes",
              "ofertas", "precios")
    out = [h for h in hs if any(c in h.lower() for c in claves)]
    return sorted(out)[:12]


def apis(dom):
    res = []
    base = "https://" + dom.split("/")[0]
    for nombre, path, check in (
            ("vtex", "/api/catalog_system/pub/products/search?_from=0&_to=9", lambda b: b.strip().startswith("[") and '"Price"' in b),
            ("shopify", "/products.json?limit=10", lambda b: '"variants"' in b and '"price"' in b),
            ("woo", "/wp-json/wc/store/products?per_page=10", lambda b: '"prices"' in b)):
        b, c, _ = get(base + path, 20)
        if c == "200" and check(b):
            try:
                n = len(json.loads(b)) if nombre != "shopify" else len(json.loads(b)["products"])
            except Exception:  # noqa: BLE001
                n = "?"
            ej = re.findall(r'"(?:productName|title|name)"\s*:\s*"([^"]{3,60})"', b)[:3]
            res.append(f"{nombre} OK ({n} productos; ej.: {', '.join(ej)})")
    return res


def sondear(dom):
    html, code, final = get("https://" + dom)
    precios = PRECIO.findall(html)
    fila = [f"### {dom}", f"- HTTP {code}, {len(html):,} bytes, final: {final}",
            f"- plataformas: {', '.join(plataformas(html)) or '—'}",
            f"- precios visibles en la portada: {len(precios)} (ej.: {', '.join(precios[:5])})"]
    a = apis(dom) if code == "200" else []
    if a:
        fila.append("- API: " + "; ".join(a))
    ls = enlaces(html, final)
    if ls:
        fila.append("- enlaces: " + " · ".join(ls))
        for l in ls[:4]:
            u = l if l.startswith("http") else final.rstrip("/") + "/" + l.lstrip("/")
            h2, c2, _ = get(u, 20)
            p2 = PRECIO.findall(h2)
            fila.append(f"  - {u} → HTTP {c2}, {len(h2):,} bytes, {len(p2)} precios (ej.: {', '.join(p2[:4])})")
    return fila + [""]


L = ["# Sondeo de fuentes: restaurantes y turismo", ""]
for titulo, lista in (("Restaurantes y comidas fuera del hogar", RESTAURANTES), ("Turismo", TURISMO)):
    L += [f"## {titulo}", ""]
    for d in lista:
        try:
            L += sondear(d)
        except Exception as e:  # noqa: BLE001
            L += [f"### {d}", f"- error: {e}", ""]
OUT.write_text("\n".join(L), encoding="utf-8")
print("\n".join(L)[:3000])
