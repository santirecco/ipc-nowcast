"""Busca historia mayorista de verduras y frutas para 2022-2025 (el Mercado Central publica sus planillas diarias solo
del año en curso). Candidatas, todas con datos que ya eran públicos en su momento:
1. Dataset de datos.gob.ar "Frutas y hortalizas - Precios mayoristas" (Dirección de Mercados Agrícolas).
2. Informes mensuales del Mercado Central (Monitoreo Federal): precio por especie al principio y al final del mes.
3. Informes mensuales del Ministerio de Agricultura (precios_fyh_AAAA_MM.pdf): precio de la última semana del mes.
4. Precios históricos de surtidor (Energía) en el archivo web.
Salida: reports/prueba_historia.md
"""
import json
import re
import subprocess
from pathlib import Path

OUT = Path(__file__).resolve().parents[2] / "reports" / "prueba_historia.md"
L = ["# Prueba de historia mayorista (verduras y frutas) y surtidores", ""]


def get(url, max_time=120, rango=None):
    cmd = ["curl", "-sSL", "--retry", "2", "--max-time", str(max_time), "-A", "Mozilla/5.0 (ipc-nowcast)",
           "-w", "\n__HTTP__%{http_code} %{size_download}"]
    if rango:
        cmd += ["-r", rango]
    r = subprocess.run(cmd + [url], capture_output=True)
    out = r.stdout
    i = out.rfind(b"\n__HTTP__")
    return (out[:i] if i >= 0 else out), (out[i + 9:].decode() if i >= 0 else "000 0")


def cdx(patron, desde="2022"):
    body, meta = get("https://web.archive.org/cdx/search/cdx?url=" + patron + f"&from={desde}"
                     "&fl=timestamp,original,statuscode,length&output=json&collapse=urlkey&limit=5000", 300)
    try:
        return json.loads(body or b"[]")[1:], meta
    except Exception:  # noqa: BLE001
        return [], meta


# 1. datos.gob.ar ------------------------------------------------------------------------------------------------
L += ["## 1. datos.gob.ar: Frutas y hortalizas - Precios mayoristas", ""]
body, meta = get("https://datos.gob.ar/api/3/action/package_search?q=frutas%20hortalizas%20precios%20mayoristas&rows=10")
try:
    for p in json.loads(body)["result"]["results"]:
        L.append(f"- paquete `{p.get('name')}` ({p.get('metadata_modified')}): {p.get('title')}")
        for r in p.get("resources", [])[:12]:
            L.append(f"  - {r.get('name')} | {r.get('last_modified') or r.get('created')} | {r.get('url')}")
            if str(r.get("url", "")).lower().endswith(".csv"):
                b, m2 = get(r["url"], 120)
                lin = b.decode("utf-8", "ignore").splitlines()
                L.append(f"    - HTTP {m2}, {len(lin)} líneas; primeras: `{lin[:3]}`; últimas: `{lin[-2:]}`")
                if "mercado" in b[:3000].decode("utf-8", "ignore").lower():
                    mercados = sorted({x.split(",")[1] for x in lin[1:2000] if x.count(",") > 2})[:20]
                    L.append(f"    - valores de la 2da columna: {mercados}")
except Exception as e:  # noqa: BLE001
    L.append(f"- error {meta}: {str(e)[:100]} `{body[:200]!r}`")
L.append("")

# 2. Monitoreo Federal del Mercado Central -------------------------------------------------------------------------
L += ["## 2. Informes Monitoreo Federal (Mercado Central)", ""]
filas, meta = cdx("mercadocentral.gob.ar/sites/default/files/docs/*", "2023")
pdfs = sorted({f[1].split("?")[0] for f in filas if f[1].lower().endswith(".pdf") and re.search(r"monitoreo", f[1], re.I)})
L.append(f"Archivo web: HTTP {meta}, {len(filas)} URLs en docs/, {len(pdfs)} PDFs de monitoreo")
for u in pdfs:
    L.append(f"- {u}")
html, meta = get("https://mercadocentral.gob.ar/informacion/monitoreo-federal")
links = sorted(set(re.findall(r'https?://[^"\']+\.pdf', html.decode("utf-8", "ignore"))))
L.append(f"Página del sitio (HTTP {meta}): {len(links)} PDFs")
for u in links[:80]:
    L.append(f"- {u}")
for u in (pdfs + links)[:2]:
    b, m2 = get(u.replace("http://", "https://"), 120)
    L.append(f"- descarga de prueba `{u.rsplit('/', 1)[-1]}`: HTTP {m2}, pdf={b[:4] == b'%PDF'}")
L.append("")

# 3. Informes del Ministerio de Agricultura -----------------------------------------------------------------------
L += ["## 3. Informes precios_fyh (Ministerio de Agricultura)", ""]
filas, meta = cdx("argentina.gob.ar/sites/default/files/*precios_fyh*", "2021")
fyh = sorted({f[1].split("?")[0] for f in filas})
L.append(f"Archivo web: HTTP {meta}, {len(fyh)} URLs")
for u in fyh:
    L.append(f"- {u}")
for u in fyh[:1] + ["https://www.argentina.gob.ar/sites/default/files/precios_fyh_2024_05.pdf"]:
    b, m2 = get(u.replace("http://", "https://"), 120)
    L.append(f"- descarga de prueba `{u.rsplit('/', 1)[-1]}`: HTTP {m2}, pdf={b[:4] == b'%PDF'}")
L.append("")

# 4. Surtidores: precios históricos de Energía en el archivo web ----------------------------------------------
L += ["## 4. Precios históricos de surtidor (Energía) en el archivo web", ""]
for patron in ("datos.energia.gob.ar/dataset/1c181390-5045-475e-94dc-410429be4b17/resource/*",):
    filas, meta = cdx(patron, "2023")
    L.append(f"`{patron}`: HTTP {meta}, {len(filas)} URLs")
    for f in filas[:30]:
        L.append(f"- {f}")
L.append("")

OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
print("\n".join(L))
