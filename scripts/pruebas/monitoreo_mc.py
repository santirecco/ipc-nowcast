"""Baja los informes mensuales "Monitoreo Federal" del Mercado Central (abr-2024 en adelante) y guarda su texto.

Cada informe trae, por especie, el precio mayorista ($/kg) al principio y al final del mes: con eso se reconstruye
la variación mayorista de verduras y frutas de 2024-2025 (las planillas diarias del sitio son solo del año en curso).
Son datos que el Mercado Central ya publicaba día a día en su momento.
Salida: data/precios/mayoristas/monitoreo/<archivo>.txt
"""
import io
import json
import subprocess
from pathlib import Path

import pdfplumber

DIR = Path(__file__).resolve().parents[2] / "data" / "precios" / "mayoristas" / "monitoreo"
BASE = "https://mercadocentral.gob.ar/sites/default/files/docs/"
MES = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
COR = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]


def get(url, t=120):
    r = subprocess.run(["curl", "-sSL", "--retry", "2", "--max-time", str(t), "-A", "Mozilla/5.0 (ipc-nowcast)", url],
                       capture_output=True)
    return r.stdout


def candidatos():
    """Nombres conocidos (archivo web) más variantes de los que faltan."""
    body = get("https://web.archive.org/cdx/search/cdx?url=mercadocentral.gob.ar/sites/default/files/docs/*"
               "&from=2023&fl=original&output=json&collapse=urlkey&limit=5000", 300)
    try:
        urls = {f[0].split("?")[0].rsplit("/", 1)[-1] for f in json.loads(body or b"[]")[1:]}
    except Exception:  # noqa: BLE001
        urls = set()
    nombres = {u for u in urls if "onitoreo" in u and u.lower().endswith(".pdf")}
    for a in (24, 25, 26):
        for i in range(12):
            for base in (f"MonitoreoFederal-{MES[i]}{a}", f"MonitoreoFederal-{COR[i]}{a}"):
                for suf in ("", "a", "b", "c", "_0", "a_0"):
                    nombres.add(f"{base}{suf}.pdf")
        for i in range(12):
            for suf in ("", "_0"):
                nombres.add(f"Informe_monitoreo-{i + 1:02d}-20{a}{suf}.pdf")
    return sorted(nombres)


def main():
    DIR.mkdir(parents=True, exist_ok=True)
    hechos = {p.stem for p in DIR.glob("*.txt")}
    bajados = 0
    for n in candidatos():
        if n[:-4] in hechos:
            continue
        b = get(BASE + n, 90)
        if b[:4] != b"%PDF":
            continue
        try:
            with pdfplumber.open(io.BytesIO(b)) as pdf:
                txt = "\n\f\n".join((pg.extract_text(layout=True) or "") for pg in pdf.pages)
        except Exception as e:  # noqa: BLE001
            print(n, "no se pudo leer", e)
            continue
        (DIR / (n[:-4] + ".txt")).write_text(txt, encoding="utf-8")
        bajados += 1
        print(n, len(txt), "caracteres", flush=True)
    print("bajados", bajados)


if __name__ == "__main__":
    main()
