"""Quinta vuelta: API de Tucán (plataforma de pedidos propia de restaurantes argentinos). Salida: reports/prueba_servicios5/"""
import subprocess
from pathlib import Path

DIR = Path(__file__).resolve().parents[2] / "reports" / "prueba_servicios5"
DIR.mkdir(parents=True, exist_ok=True)
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"


def get(url, t=30):
    r = subprocess.run(["curl", "-sSL", "--compressed", "--max-time", str(t), "-A", UA, "-H", "Accept: application/json",
                        "-H", "Origin: https://pedir.tucan.la", "-H", "Referer: https://pedir.tucan.la/",
                        "-w", "\n__HTTP__%{http_code}", url], capture_output=True)
    out = r.stdout
    i = out.rfind(b"\n__HTTP__")
    return (out[:i] if i >= 0 else out).decode("utf-8", "ignore"), (out[i + 9:].decode() if i >= 0 else "000")


B = "https://pedir.tucan.la"
log = []
for n, path in enumerate([
        "/api/diner/branches/11928", "/api/diner/branches/?menu=11928", "/api/diner/branches/?alias=almacen-de-pizzas",
        "/api/diner/menu/11928", "/api/diner/menu/?id=11928", "/api/diner/menu/almacen-de-pizzas",
        "/api/menu/near?lat=-34.6037&lng=-58.3816", "/api/menu/near?latitude=-34.6037&longitude=-58.3816",
        "/api/categories", "/api/country/", "/api/ordermodes/?menu=11928", "/api/diner/menu/?menuId=11928", "/api/diner/menu/?alias=almacen-de-pizzas", "/api/diner/branches/?menuId=11928"]):
    b, c = get(B + path)
    log.append(f"{path}: HTTP {c}, {len(b):,} bytes, price x{b.lower().count('price')}: {b[:160]!r}")
    if c == "200" and len(b) > 50:
        (DIR / f"r{n:02d}.json").write_text(b[:300000], encoding="utf-8")
(DIR / "log.md").write_text("\n".join(log), encoding="utf-8")
print("\n".join(log))
