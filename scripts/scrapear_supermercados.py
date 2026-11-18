"""Recolección diaria de precios de supermercados online (Carrefour, Jumbo, Disco, Vea, Día).

Guarda:
  data/precios/supermercados/diario/AAAA-MM/AAAA-MM-DD_<cadena>.parquet   precio del día de cada producto con stock
  data/precios/supermercados/catalogo_<cadena>.parquet                    datos fijos de cada producto (nombre, EAN, categoría)
  data/precios/supermercados/resumen.csv                                  control: cuántos productos se bajaron por día

Uso:  python scripts/scrapear_supermercados.py              (todas las cadenas)
      python scripts/scrapear_supermercados.py dia jumbo    (algunas)
"""
import sys
import time
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pandas as pd  # noqa: E402

from ipc_nowcast import DATA  # noqa: E402
from ipc_nowcast.scrapers import vtex  # noqa: E402

DIR = DATA / "precios" / "supermercados"
COLS_PRECIO = ["item_id", "precio", "precio_lista", "precio_sin_desc", "promos"]
COLS_CATALOGO = ["item_id", "producto_id", "ean", "nombre", "marca", "categoria", "unidad", "multiplicador"]


def actualizar_catalogo(cadena: str, df: pd.DataFrame, hoy: date) -> int:
    ruta = DIR / f"catalogo_{cadena}.parquet"
    nuevo = df[COLS_CATALOGO].copy()
    nuevo["ultima_vez"] = pd.Timestamp(hoy)
    if ruta.exists():
        viejo = pd.read_parquet(ruta)
        nuevo = nuevo.merge(viejo[["item_id", "primera_vez"]], on="item_id", how="left")
        nuevo["primera_vez"] = nuevo["primera_vez"].fillna(pd.Timestamp(hoy))
        resto = viejo[~viejo.item_id.isin(nuevo.item_id)]
        altas = int((nuevo["primera_vez"] == pd.Timestamp(hoy)).sum())
        cat = pd.concat([resto, nuevo], ignore_index=True)
    else:
        nuevo["primera_vez"] = pd.Timestamp(hoy)
        cat, altas = nuevo, len(nuevo)
    cat.to_parquet(ruta, index=False, compression="zstd")
    return altas


def main():
    cadenas = sys.argv[1:] or list(vtex.CADENAS)
    hoy = date.today()
    DIR.mkdir(parents=True, exist_ok=True)
    resumen = []
    fallas = 0
    for c in cadenas:
        t0 = time.time()
        errores = []
        try:
            df = vtex.scrapear(c, log=lambda m: (print(m), errores.append(m) if m.strip().startswith("!") else None))
        except Exception as e:  # noqa: BLE001
            print(f"ERROR {c}: {e}")
            df, errores = pd.DataFrame(), [str(e)]
        if len(df):
            destino = DIR / "diario" / f"{hoy:%Y-%m}"
            destino.mkdir(parents=True, exist_ok=True)
            df[COLS_PRECIO].to_parquet(destino / f"{hoy:%Y-%m-%d}_{c}.parquet", index=False, compression="zstd")
            altas = actualizar_catalogo(c, df, hoy)
        else:
            altas = 0
            fallas += 1
        resumen.append({"fecha": hoy, "cadena": c, "productos": len(df), "altas_catalogo": altas,
                        "errores": len(errores), "segundos": round(time.time() - t0)})
    r = pd.DataFrame(resumen)
    ruta = DIR / "resumen.csv"
    if ruta.exists():
        viejo = pd.read_csv(ruta)
        viejo = viejo[~((viejo.fecha == str(hoy)) & viejo.cadena.isin(r.cadena))]
        r = pd.concat([viejo, r], ignore_index=True)
    r.to_csv(ruta, index=False)
    print(r.tail(len(cadenas)).to_string(index=False))
    if fallas == len(cadenas):
        sys.exit("Ninguna cadena devolvió datos.")


if __name__ == "__main__":
    main()
