"""Baja los reportes mensuales de Tarifas y Subsidios del IIEP (UBA-CONICET) y guarda su texto.

Cada reporte trae la canasta de servicios públicos del AMBA (electricidad, gas, agua, transporte) armada con los
cuadros tarifarios vigentes en el mes. Sirve para reconstruir la historia de tarifas reguladas de GBA (2024-2026)
con información que ya era pública en ese mes.
Salida: data/precios/regulados/iiep/<archivo>.txt y reports/prueba_iiep.md (qué se encontró).
"""
import io
import json
import re
import subprocess
from pathlib import Path

import pdfplumber

RAIZ = Path(__file__).resolve().parents[2]
DIR = RAIZ / "data" / "precios" / "regulados" / "iiep"
MESES = ["ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO", "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE",
         "NOVIEMBRE", "DICIEMBRE"]


def get(url, t=120):
    r = subprocess.run(["curl", "-sSL", "--retry", "1", "--connect-timeout", "10", "--max-time", str(t), "-A", "Mozilla/5.0 (ipc-nowcast)", url],
                       capture_output=True)
    return r.stdout


def main():
    DIR.mkdir(parents=True, exist_ok=True)
    log = ["# Reportes de tarifas del IIEP", ""]
    urls = set()
    for pag in ("https://iiep.economicas.uba.ar/publicaciones/informes-reportes/",
                "https://iiep.economicas.uba.ar/publicaciones/informes-reportes/page/2/",
                "https://iiep.economicas.uba.ar/publicaciones/informes-reportes/page/3/"):
        html = get(pag).decode("utf-8", "ignore")
        urls |= {u for u in re.findall(r'https?://[^"\'\s]+\.pdf', html) if re.search(r"tarif", u, re.I)}
        log.append(f"- {pag}: {len(html)} bytes")
    # archivo web y patrón conocido de nombres
    body = get("https://web.archive.org/cdx/search/cdx?url=economicas.uba.ar/iiep/wp-content/uploads/*&from=2024"
               "&fl=original&output=json&collapse=urlkey&limit=20000", 300)
    try:
        urls |= {f[0].split("?")[0].replace("http://", "https://") for f in json.loads(body or b"[]")[1:]
                 if re.search(r"tarif", f[0], re.I) and f[0].lower().endswith(".pdf")}
    except Exception:  # noqa: BLE001
        pass
    # si la página no dio links, probar el patrón conocido (un solo nombre por mes, subcarpeta del mes y la siguiente)
    if len(urls) < 10:
        for anio in (2024, 2025, 2026):
            for i, m in enumerate(MESES):
                for sub in (f"{anio}/{i + 1:02d}", f"{anio}/{min(i + 2, 12):02d}"):
                    urls.add(f"https://economicas.uba.ar/iiep/wp-content/uploads/{sub}/INFORME-TARIFAS-Y-SUBSIDIOS-{m}-{anio}.pdf")
    log.append(f"- candidatos: {len(urls)}")
    hechos = {p.stem for p in DIR.glob("*.txt")}
    ok = 0
    for u in sorted(urls):
        nombre = u.rsplit("/", 1)[-1][:-4]
        if nombre in hechos:
            continue
        b = get(u, 20)
        if b[:4] != b"%PDF":
            continue
        try:
            with pdfplumber.open(io.BytesIO(b)) as pdf:
                txt = "\n\f\n".join((pg.extract_text(layout=True) or "") for pg in pdf.pages)
        except Exception as e:  # noqa: BLE001
            log.append(f"  - {u}: no se pudo leer ({e})")
            continue
        (DIR / f"{nombre}.txt").write_text(f"# {u}\n{txt}", encoding="utf-8")
        hechos.add(nombre)
        ok += 1
        log.append(f"  - {u}: {len(txt)} caracteres")
    log.append(f"- bajados: {ok}; total guardados: {len(hechos)}")
    (RAIZ / "reports" / "prueba_iiep.md").write_text("\n".join(log) + "\n", encoding="utf-8")
    print("\n".join(log))


if __name__ == "__main__":
    main()
