"""Busca historia para las dos clases que más error dejan a fin de mes (nov-2026):
1. Mercado Central 2022-2025 (verduras y frutas): archivos mensuales viejos en el servidor o en el archivo web.
2. Precios diarios de surtidor de la Secretaría de Energía (Res. 314/2016): con fecha de vigencia por estación,
   permitirían el promedio del mes (lo que mide INDEC) hacia atrás.
Salida: reports/prueba_historia.md
"""
import json
import re
import subprocess
from pathlib import Path

OUT = Path(__file__).resolve().parents[2] / "reports" / "prueba_historia.md"
lineas = ["# Prueba de historia: Mercado Central y surtidores (Energía)", ""]


def get(url, max_time=120, head=False):
    cmd = ["curl", "-sSL", "--retry", "2", "--max-time", str(max_time), "-A", "Mozilla/5.0 (ipc-nowcast)",
           "-w", "\n__HTTP__%{http_code} %{size_download}"]
    if head:
        cmd += ["-r", "0-2047"]
    r = subprocess.run(cmd + [url], capture_output=True)
    out = r.stdout
    i = out.rfind(b"\n__HTTP__")
    meta = out[i + 9:].decode() if i >= 0 else "000 0"
    return (out[:i] if i >= 0 else out), meta


# 1. Mercado Central -------------------------------------------------------------------------------------------
lineas += ["## Mercado Central", ""]
html, meta = get("https://mercadocentral.gob.ar/informacion/precios-mayoristas")
links = sorted(set(re.findall(r'https?://[^"\']+\.zip', html.decode("utf-8", "ignore"))))
lineas.append(f"Página actual: HTTP {meta}, {len(links)} links .zip")
for u in links[:40]:
    lineas.append(f"- {u}")
lineas.append("")

# lo que tiene el archivo web, por año
for patron in ("mercadocentral.gob.ar/sites/default/files/precios_mayoristas/*",
               "mercadocentral.gob.ar/*precios*mayoristas*"):
    body, meta = get("https://web.archive.org/cdx/search/cdx?url=" + patron +
                     "&from=2022&fl=timestamp,original,statuscode,length&output=json&collapse=urlkey&limit=5000", 300)
    try:
        filas = json.loads(body or b"[]")[1:]
    except Exception:  # noqa: BLE001
        filas = []
    lineas.append(f"Archivo web `{patron}` desde 2022: HTTP {meta}, {len(filas)} URLs distintas")
    zips = [f for f in filas if f[1].lower().endswith(".zip")]
    por_anio = {}
    for ts, url, st, ln in zips:
        m = re.search(r"(20\d\d)", url.rsplit("/", 1)[-1])
        por_anio.setdefault(m.group(1) if m else "?", []).append((ts, url, st, ln))
    for a in sorted(por_anio):
        lineas.append(f"- {a}: {len(por_anio[a])} zips")
        for ts, url, st, ln in por_anio[a][:30]:
            lineas.append(f"  - {ts} {st} {ln} {url}")
    lineas.append("")

# probar si el servidor todavía tiene los archivos de años anteriores con el mismo patrón que los actuales
prob = []
for u in links[:6]:
    for a in ("2025", "2024", "2023"):
        if "2026" in u:
            prob.append(u.replace("2026", a))
for u in prob[:18]:
    b, meta = get(u, 60, head=True)
    lineas.append(f"- servidor {meta} `{u.rsplit('/', 1)[-1]}` zip={b[:2] == b'PK'}")
lineas.append("")

# 2. Energía: precios en surtidor ------------------------------------------------------------------------------
lineas += ["## Surtidores (Secretaría de Energía)", ""]
for api in ("http://datos.energia.gob.ar/api/3/action/package_show?id=precios-en-surtidor-resolucin-3142016",
            "https://datos.energia.gob.ar/api/3/action/package_search?q=surtidor",
            "https://datos.gob.ar/api/3/action/package_search?q=precios%20en%20surtidor"):
    body, meta = get(api, 120)
    lineas.append(f"- `{api}`: HTTP {meta}")
    try:
        d = json.loads(body)
        res = d["result"]
        pkgs = res["results"] if isinstance(res, dict) and "results" in res else [res]
        for p in pkgs[:5]:
            lineas.append(f"  - paquete {p.get('name')} ({p.get('metadata_modified')})")
            for r in p.get("resources", [])[:10]:
                lineas.append(f"    - {r.get('name')} | {r.get('last_modified') or r.get('created')} | {r.get('url')}")
                if r.get("url", "").endswith(".csv"):
                    b, m2 = get(r["url"], 60, head=True)
                    lineas.append(f"      primeros bytes ({m2}): `{b[:300].decode('utf-8', 'ignore').splitlines()[:2]}`")
    except Exception as e:  # noqa: BLE001
        lineas.append(f"  - sin JSON: {str(e)[:80]} `{body[:120]!r}`")
lineas.append("")

OUT.write_text("\n".join(lineas) + "\n", encoding="utf-8")
print("\n".join(lineas))
