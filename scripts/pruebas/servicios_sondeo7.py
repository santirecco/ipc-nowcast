"""Séptima vuelta: directorio de comercios de Tucán (POST /api/menu/near) y hashes/menú de un comercio.
Salida: reports/prueba_servicios7/"""
import json
import subprocess
from pathlib import Path

DIR = Path(__file__).resolve().parents[2] / "reports" / "prueba_servicios7"
DIR.mkdir(parents=True, exist_ok=True)
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"
B = "https://app.loveat.la"


def req(path, data=None, t=30):
    cmd = ["curl", "-sSL", "--compressed", "--max-time", str(t), "-A", UA, "-H", "Accept: application/json",
           "-H", "Origin: https://pedir.tucan.la", "-H", "Referer: https://pedir.tucan.la/"]
    if data is not None:
        cmd += ["-H", "Content-Type: application/json", "--data-raw", json.dumps(data)]
    r = subprocess.run(cmd + ["-w", "\n__HTTP__%{http_code}", B + path], capture_output=True)
    out = r.stdout
    i = out.rfind(b"\n__HTTP__")
    return (out[:i] if i >= 0 else out).decode("utf-8", "ignore"), (out[i + 9:].decode() if i >= 0 else "000")


log = []
near = {"lat": -34.6037, "lng": -58.3816, "filters": [{"key": "country", "value": "Argentina"}, {"key": "branch_contact", "value": "true"}],
        "pagingOption": {"pageSize": 50, "offset": 0}}
b, c = req("/api/menu/near", near)
log.append(f"near: HTTP {c}, {len(b):,} bytes: {b[:300]!r}")
(DIR / "near.json").write_text(b[:500000], encoding="utf-8")
for path in ("/api/diner/menu/11928/hash?", "/api/diner/menu/11928/hash?orderModeId=1&", "/api/diner/menu/11928/hash?orderModeId=2&",
             "/api/diner/menu/11928/hash?orderModeId=3&", "/api/ordermodes/11928", "/api/diner/menu/11928?orderModeId=1"):
    b, c = req(path)
    log.append(f"{path}: HTTP {c}, {len(b):,} bytes: {b[:300]!r}")
    if c == "200":
        (DIR / ("m" + path.replace("/", "_").replace("?", "_").replace("&", "_").replace("=", "") + ".json")).write_text(b[:500000], encoding="utf-8")
(DIR / "log.md").write_text("\n".join(log), encoding="utf-8")
print("\n".join(log))
