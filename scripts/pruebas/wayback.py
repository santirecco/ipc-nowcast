"""¿Sirve el archivo web (Wayback Machine) para reconstruir la historia de precios de ropa, calzado y electro?

Cuenta, por tienda y mes, cuántas páginas de producto tienen copia archivada y prueba si una copia trae el precio.
Precios publicados en su momento: usarlos para el pasado es honesto. Salida: reports/prueba_wayback.md
"""
import json
import re
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path

# mismas tiendas que src/ipc_nowcast/scrapers/vtex.py (copiadas: este script corre sin dependencias)
TIENDAS = {"equus": "https://www.equus.com.ar", "portsaid": "https://www.portsaid.com.ar",
           "tascani": "https://www.tascani.com.ar", "levis": "https://www.levi.com.ar",
           "legacy": "https://www.legacy.com.ar", "mimo": "https://www.mimo.com.ar",
           "topper": "https://www.topper.com.ar", "naldo": "https://www.naldo.com.ar",
           "cetrogar": "https://www.cetrogar.com.ar", "coppel": "https://www.coppel.com.ar",
           "pardo": "https://www.pardo.com.ar", "easy": "https://www.easy.com.ar", "blaisten": "https://www.blaisten.com.ar",
           "dafiti": "https://www.dafiti.com.ar", "fravega": "https://www.fravega.com", "garbarino": "https://www.garbarino.com"}
RUBRO_TIENDA = {"equus": "ropa", "portsaid": "ropa", "tascani": "ropa", "levis": "ropa", "legacy": "ropa", "mimo": "ropa",
                "dafiti": "ropa", "topper": "calzado", "naldo": "electro", "cetrogar": "electro", "coppel": "electro",
                "pardo": "electro", "fravega": "electro", "garbarino": "electro", "easy": "hogar", "blaisten": "hogar"}

UA = "Mozilla/5.0 (ipc-nowcast; investigación)"


def get(url, timeout=90):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def main():
    lineas = ["# Prueba del archivo web (Wayback Machine)", "",
              "| Tienda | Rubro | Páginas de producto archivadas (2023+) | Meses con 30+ copias | Copia con precio |", "|---|---|---|---|---|"]
    detalle = []
    for nombre, url in TIENDAS.items():
        if nombre not in RUBRO_TIENDA:
            continue
        dominio = urllib.parse.urlparse(url).netloc
        q = (f"https://web.archive.org/cdx/search/cdx?url={dominio}/*&from=2023&filter=statuscode:200"
             f"&filter=original:.*/p$&fl=timestamp,original&limit=50000&output=json")
        try:
            filas = json.loads(get(q, 180) or "[]")[1:]
        except Exception as e:  # noqa: BLE001
            lineas.append(f"| {nombre} | {RUBRO_TIENDA[nombre]} | error: {type(e).__name__} | | |")
            continue
        meses = Counter(ts[:6] for ts, _ in filas)
        con_precio = "—"
        if filas:
            ts, orig = filas[len(filas) // 2]
            try:
                html = get(f"https://web.archive.org/web/{ts}id_/{orig}")
                m = re.search(r'"(?:price|Price|bestPrice|lowPrice)"\s*:\s*"?([0-9][0-9.,]*)', html)
                con_precio = f"sí ({m.group(1)})" if m else "no"
            except Exception as e:  # noqa: BLE001
                con_precio = f"error {type(e).__name__}"
        lineas.append(f"| {nombre} | {RUBRO_TIENDA[nombre]} | {len(filas)} | {sum(1 for v in meses.values() if v >= 30)} | {con_precio} |")
        detalle.append(f"- {nombre}: " + ", ".join(f"{k}: {v}" for k, v in sorted(meses.items())))
    texto = "\n".join(lineas + ["", "Copias por mes:", ""] + detalle) + "\n"
    Path("reports/prueba_wayback.md").write_text(texto, encoding="utf-8")
    print(texto)


if __name__ == "__main__":
    main()
