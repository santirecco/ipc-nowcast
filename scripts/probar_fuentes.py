"""Prueba de acceso: ¿qué fuentes de precios responden desde donde corre este script?

Escribe reports/prueba_fuentes.md con el código HTTP, el tamaño y una muestra de cada fuente.
Se corre en GitHub Actions para saber qué sitios bloquean a los servidores de GitHub.
"""
import json
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"


def sepa_urls():
    with urllib.request.urlopen(urllib.request.Request(
            "https://datos.gob.ar/api/3/action/package_show?id=precios-claros-base-sepa",
            headers={"User-Agent": UA}), timeout=60) as r:
        res = json.load(r)["result"]["resources"]
    return [(f"SEPA {x['name']}", x["url"]) for x in res if x["url"].endswith(".zip")][:2]


FUENTES = [
    ("INDEC series", "https://www.indec.gob.ar/ftp/cuadros/economia/serie_ipc_divisiones.csv"),
    ("Carrefour VTEX", "https://www.carrefour.com.ar/api/catalog_system/pub/products/search?ft=leche&_from=0&_to=2"),
    ("Jumbo VTEX", "https://www.jumbo.com.ar/api/catalog_system/pub/products/search?ft=leche&_from=0&_to=2"),
    ("Disco VTEX", "https://www.disco.com.ar/api/catalog_system/pub/products/search?ft=leche&_from=0&_to=2"),
    ("Vea VTEX", "https://www.vea.com.ar/api/catalog_system/pub/products/search?ft=leche&_from=0&_to=2"),
    ("Día VTEX", "https://diaonline.supermercadosdia.com.ar/api/catalog_system/pub/products/search?ft=leche&_from=0&_to=2"),
    ("Coto", "https://www.cotodigital.com.ar/sitios/cdigi/nuevositio"),
    ("Coto (viejo)", "https://www.cotodigital3.com.ar/sitios/cdigi/browse?Ntt=leche"),
    ("Mercado Central", "https://mercadocentral.gob.ar/"),
    ("IPCVA", "https://www.ipcva.com.ar/"),
    ("Precios surtidor (datos.energia)", "http://datos.energia.gob.ar/dataset/1c181390-5045-475e-94dc-410429be4b17"),
    ("BCRA", "https://www.bcra.gob.ar/"),
    ("Estadística CABA", "https://www.estadisticaciudad.gob.ar/"),
    ("Boletín Oficial", "https://www.boletinoficial.gob.ar/"),
]


def probar(nombre, url, max_bytes=2_000_000):
    t0 = time.time()
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
        with urllib.request.urlopen(req, timeout=90) as r:
            cuerpo = r.read(max_bytes)
            return {"fuente": nombre, "codigo": r.status, "bytes_leidos": len(cuerpo),
                    "largo_total": r.headers.get("Content-Length"), "tipo": r.headers.get("Content-Type"),
                    "ultima_modif": r.headers.get("Last-Modified"), "seg": round(time.time() - t0, 1),
                    "muestra": cuerpo[:120].decode("utf-8", "replace").replace("\n", " ").replace("|", "/")}
    except Exception as e:  # noqa: BLE001
        codigo = getattr(e, "code", None)
        return {"fuente": nombre, "codigo": codigo or "error", "bytes_leidos": 0, "seg": round(time.time() - t0, 1),
                "muestra": str(e)[:120].replace("|", "/")}


def main():
    fuentes = list(FUENTES)
    try:
        fuentes = sepa_urls() + fuentes
    except Exception as e:  # noqa: BLE001
        fuentes = [("SEPA (API CKAN)", "https://datos.gob.ar/api/3/action/package_show?id=precios-claros-base-sepa")] + fuentes
        print("No se pudo leer la API de datos.gob.ar:", e, file=sys.stderr)
    res = [probar(n, u) for n, u in fuentes]
    lineas = [f"# Prueba de fuentes ({datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC)", "",
              "| Fuente | Código | Bytes leídos | Largo total | Últ. modif. | Seg | Muestra |", "|---|---|---|---|---|---|---|"]
    for r in res:
        lineas.append(f"| {r['fuente']} | {r['codigo']} | {r['bytes_leidos']} | {r.get('largo_total')} | {r.get('ultima_modif')} | {r['seg']} | `{r['muestra'][:80]}` |")
    salida = RAIZ / "reports" / "prueba_fuentes.md"
    salida.write_text("\n".join(lineas) + "\n", encoding="utf-8")
    print("\n".join(lineas))


if __name__ == "__main__":
    main()
