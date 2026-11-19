"""Reconstruye el precio DIARIO de los combustibles (YPF, Ciudad de Buenos Aires) con las copias archivadas de
surtidores.com.ar/precios en el archivo web (Wayback Machine). Cada copia muestra el precio vigente ese día en la
celda del mes en curso: con eso se arma el promedio de cada mes, que es lo que compara INDEC.
Precios publicados en su momento: usarlos para el pasado es honesto. Corre en GitHub (el archivo no responde desde
otros lados). Salida: data/precios/combustibles/ypf_caba_wayback.csv (fecha, producto, precio).
"""
import json
import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import pandas as pd  # noqa: E402

from ipc_nowcast.indicadores import parsear_tabla_surtidores  # noqa: E402

SALIDA = Path(__file__).resolve().parents[1] / "data" / "precios" / "combustibles" / "ypf_caba_wayback.csv"
UA = "Mozilla/5.0 (ipc-nowcast; investigación)"


def get(url, timeout=90, intentos=4):
    for i in range(intentos):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read().decode("utf-8", "replace")
        except Exception:  # noqa: BLE001
            if i == intentos - 1:
                raise
            time.sleep(5 * (i + 1))


def main():
    prev = pd.read_csv(SALIDA, dtype={"fecha": str}) if SALIDA.exists() else pd.DataFrame(columns=["fecha", "producto", "precio", "timestamp"])
    hechas = set(prev.get("timestamp", pd.Series(dtype=str)).astype(str))
    snaps = []
    for u in ("surtidores.com.ar/precios/", "www.surtidores.com.ar/precios/", "surtidores.com.ar/precios"):
        q = (f"https://web.archive.org/cdx/search/cdx?url={u}&from=2023&filter=statuscode:200"
             f"&collapse=timestamp:8&fl=timestamp,original&output=json")
        try:
            snaps += [tuple(x) for x in json.loads(get(q, 180) or "[]")[1:]]
        except Exception as e:  # noqa: BLE001
            print("cdx", u, e)
    por_dia = {}
    for ts, orig in sorted(snaps):
        por_dia.setdefault(ts[:8], (ts, orig))
    print(f"{len(por_dia)} días con copia", flush=True)
    filas = []
    for dia, (ts, orig) in sorted(por_dia.items()):
        if ts in hechas:
            continue
        try:
            html = get(f"https://web.archive.org/web/{ts}id_/{orig}")
        except Exception as e:  # noqa: BLE001
            print(dia, "error", type(e).__name__, flush=True)
            continue
        t = parsear_tabla_surtidores(html)
        f = pd.Timestamp(dia)
        t = t[(t.anio == f.year) & (t.mes == f.month)]
        for _, r in t.iterrows():
            filas.append({"fecha": f.strftime("%Y-%m-%d"), "producto": r.producto, "precio": r.precio, "timestamp": ts})
        if len(filas) and len(filas) % 200 == 0:
            print(dia, len(filas), flush=True)
        time.sleep(1.0)
    todo = pd.concat([prev, pd.DataFrame(filas)]).drop_duplicates(["fecha", "producto"], keep="last").sort_values(["fecha", "producto"])
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    todo.to_csv(SALIDA, index=False)
    print(f"listo: {todo.fecha.nunique()} días, de {todo.fecha.min()} a {todo.fecha.max()}")


if __name__ == "__main__":
    main()
