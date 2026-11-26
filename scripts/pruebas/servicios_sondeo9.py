"""Novena vuelta: menú con precios de Tucán (/api/diner/{branch}/menu/{menu}). Salida: reports/prueba_servicios9/"""
import json
import subprocess
from pathlib import Path

DIR = Path(__file__).resolve().parents[2] / "reports" / "prueba_servicios9"
DIR.mkdir(parents=True, exist_ok=True)
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"


def get(path, t=30):
    r = subprocess.run(["curl", "-sSL", "--compressed", "--max-time", str(t), "-A", UA, "-H", "Accept: application/json",
                        "-H", "Origin: https://pedir.tucan.la", "-H", "Referer: https://pedir.tucan.la/",
                        "-w", "\n__HTTP__%{http_code}", "https://app.loveat.la" + path], capture_output=True)
    out = r.stdout
    i = out.rfind(b"\n__HTTP__")
    return (out[:i] if i >= 0 else out).decode("utf-8", "ignore"), (out[i + 9:].decode() if i >= 0 else "000")


log = []
for path in ["/api/diner/11928/menu/2?lazyPlates=true", "/api/diner/11928/menu/2", "/api/diner/almacen-de-pizzas/menu/2?lazyPlates=true",
             "/api/diner/11928/menu/81c463d0?lazyPlates=true", "/api/diner/11928/menu/d0fe19b7?lazyPlates=true",
             "/api/diner/11928/menu/1?lazyPlates=true", "/api/diner/11928/menu/3?lazyPlates=true", "/api/diner/11928",
             "/api/diner/almacen-de-pizzas", "/api/diner/branches/almacen-de-pizzas", "/api/diner/companies/almacen-de-pizzas",
             "/api/diner/9118/menu/2?lazyPlates=true&orderModeId=2", "/api/plates?branchId=11928"]:
    b, c = get(path)
    log.append(f"{path}: HTTP {c}, {len(b):,} bytes, price x{b.count('price')}: {b[:400]!r}")
    if c == "200" and len(b) > 100:
        (DIR / (path.replace("/", "_").replace("?", "_").replace("&", "_").replace("=", "")[:90] + ".json")).write_text(b[:600000], encoding="utf-8")
(DIR / "log.md").write_text("\n".join(log), encoding="utf-8")
print("\n".join(log))
