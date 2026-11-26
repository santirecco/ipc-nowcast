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
for bid, mid in ((11928, 2), (9118, None)):
    if mid is None:
        b, c = get(f"/api/diner/menu/{bid}/hash?orderModeId=1&orderModeId=2&orderModeId=3&")
        log.append(f"hash {bid}: {c} {b[:200]}")
        try:
            mid = json.loads(b)["menuHashes"][0]["menuId"]
        except Exception:  # noqa: BLE001
            continue
    b, c = get(f"/api/diner/{bid}/menu/{mid}?lazyPlates=true")
    log.append(f"menu {bid}/{mid}: HTTP {c}, {len(b):,} bytes, price x{b.count('price')}: {b[:300]!r}")
    (DIR / f"menu_{bid}_{mid}.json").write_text(b[:600000], encoding="utf-8")
    try:
        cats = json.loads(b).get("categories") or []
    except Exception:  # noqa: BLE001
        cats = []
    for cat in cats[:2]:
        cid = cat.get("id")
        b2, c2 = get(f"/api/diner/{bid}/menu/{mid}/category/{cid}?page=0&size=50")
        log.append(f"  cat {cid}: HTTP {c2}, {len(b2):,} bytes, price x{b2.count('price')}: {b2[:300]!r}")
        (DIR / f"cat_{bid}_{mid}_{cid}.json").write_text(b2[:300000], encoding="utf-8")
(DIR / "log.md").write_text("\n".join(log), encoding="utf-8")
print("\n".join(log))
