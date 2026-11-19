"""Precios de SEPA (Precios Claros): la base oficial que las cadenas grandes informan todos los días.

El sitio oficial (datos.produccion.gob.ar) bloquea los accesos desde servidores, así que se usa el archivo
diario que mantiene el proyecto abierto *preciazo* (github.com/catdevnull/preciazo), que guarda una copia de
cada día desde agosto de 2024 en Backblaze, con su índice en github.com/catdevnull/sepa-precios-metadata.

Cada día se reduce a: mediana del precio de lista de cada producto (EAN) por cadena y región INDEC
(sobre todas las sucursales de esa cadena en la región), solo para productos clasificados en una clase del IPC.

Con eso se arma, para cada mes, la variación de cada clase en cada región como hace INDEC: promedio mensual
del precio de cada producto, relativo contra el promedio del mes anterior (mismo producto, cadena y región),
media geométrica dentro de cada cadena y promedio simple entre cadenas.

Los archivos diarios procesados se guardan en data/cache/sepa/ (no se suben al repo: pesan ~2 MB por día).
En GitHub Actions esa carpeta se conserva con el caché de Actions; si se pierde se reconstruye desde el archivo.
"""
from __future__ import annotations

import glob
import io
import json
import os
import shutil
import subprocess
import tarfile
import tempfile
import urllib.request
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

from . import DATA
from .clasificador_sepa import clasificar, clasificar_no_alimentos, es_carne_fresca

INDICE_URL = "https://raw.githubusercontent.com/catdevnull/sepa-precios-metadata/main/index.json"
CACHE = DATA / "cache" / "sepa"
SALIDA = DATA / "precios" / "sepa"
GBA_CP_MAX = 1899  # en provincia de Buenos Aires, los códigos postales 1600-1899 son los 24 partidos del GBA
REGION_PROV = {
    "C": "GBA", "B": "Pampeana", "X": "Pampeana", "S": "Pampeana", "E": "Pampeana", "L": "Pampeana",
    "W": "Noreste", "H": "Noreste", "P": "Noreste", "N": "Noreste",
    "Y": "Noroeste", "A": "Noroeste", "T": "Noroeste", "G": "Noroeste", "K": "Noroeste", "F": "Noroeste",
    "M": "Cuyo", "J": "Cuyo", "D": "Cuyo",
    "Q": "Patagonia", "R": "Patagonia", "U": "Patagonia", "Z": "Patagonia", "V": "Patagonia",
}
CADENAS = {"15": "Día", "10": "Carrefour", "11": "ChangoMás", "9": "Cencosud (Jumbo, Disco, Vea)", "12": "Coto",
           "2": "La Anónima", "13": "Cooperativa Obrera", "24": "Farmacity", "21": "Toledo", "8": "Mariano Max",
           "47": "Unicoop", "5": "California", "6": "Comodín", "3": "Deheza", "20": "La Agrícola Regional",
           "23": "Axion", "4": "Estación Lima", "36": "Cadena 36"}
RECORTE = (0.6, 1.67)  # relativos de precio fuera de este rango se descartan (errores de carga, cambios de envase)
MIN_PRODUCTOS = 20     # mínimo de productos por cadena, región y clase para que esa cadena cuente


# ------------------------------------------------------------------ descarga
def indice_archivo() -> dict[str, str]:
    """Fecha (AAAA-MM-DD) -> link de descarga del archivo de ese día (el primero válido)."""
    req = urllib.request.Request(INDICE_URL, headers={"User-Agent": "ipc-nowcast"})
    with urllib.request.urlopen(req, timeout=60) as r:
        d = json.load(r)
    out = {}
    for fecha, recursos in d.items():
        links = [x.get("link") for x in recursos if x.get("link")]
        if links:
            out[fecha] = links[0]
    return out


def _leer(fuente, cols: list[str]):
    """Lee un CSV de SEPA (separado por |) desde una ruta o desde bytes."""
    import polars as pl
    import pyarrow as pa
    import pyarrow.csv as pc
    if isinstance(fuente, (bytes, bytearray)):
        primera = bytes(fuente[:4000]).split(b"\n", 1)[0]
        origen = pa.BufferReader(fuente)
    else:
        with open(fuente, "rb") as f:
            primera = f.readline()
        origen = fuente
    bom = "\ufeff"
    cab = primera.decode("utf-8", "ignore").lstrip(bom).strip().split("|")
    renombre = {c: c.strip().lstrip(bom) for c in cab}
    usar = [c for c in cab if renombre[c] in cols]
    opts = pc.ParseOptions(delimiter="|", quote_char=False, invalid_row_handler=lambda r: "skip")
    conv = pc.ConvertOptions(include_columns=usar, column_types={c: pa.string() for c in usar})
    t = pc.read_csv(origen, parse_options=opts, convert_options=conv, read_options=pc.ReadOptions(encoding="utf8"))
    return pl.from_arrow(t).rename({c: renombre[c] for c in usar})


def _archivos_por_cadena(archivo_tar: str, tmp: str):
    """Recorre el .tar.zst en streaming y devuelve, por cadena, las rutas de sucursales.csv y productos.csv
    (se escriben de a uno en `tmp` y se borran después de usarlos: memoria y disco acotados)."""
    import zstandard
    pend: dict[str, dict[str, str]] = {}
    with open(archivo_tar, "rb") as f:
        t = tarfile.open(fileobj=zstandard.ZstdDecompressor().stream_reader(f), mode="r|")
        for k, m in enumerate(t):
            if not m.isfile():
                continue
            base = os.path.basename(m.name)
            if base.endswith(".zip"):
                try:
                    z = zipfile.ZipFile(io.BytesIO(t.extractfile(m).read()))
                    grupo = {}
                    for n in z.namelist():
                        b = os.path.basename(n)
                        if b in ("sucursales.csv", "productos.csv"):
                            ruta = os.path.join(tmp, f"z{k}_{b}")
                            with z.open(n) as src, open(ruta, "wb") as dst:
                                shutil.copyfileobj(src, dst, 1 << 20)
                            grupo[b] = ruta
                    if len(grupo) == 2:
                        yield grupo["sucursales.csv"], grupo["productos.csv"]
                except Exception:  # algunos días una cadena viene con el zip roto: se saltea
                    pass
                continue
            if base not in ("sucursales.csv", "productos.csv"):
                continue
            d = os.path.dirname(m.name)
            ruta = os.path.join(tmp, f"{k}_{base}")
            with open(ruta, "wb") as dst:
                shutil.copyfileobj(t.extractfile(m), dst, 1 << 20)
            pend.setdefault(d, {})[base] = ruta
            if len(pend[d]) == 2:
                g = pend.pop(d)
                yield g["sucursales.csv"], g["productos.csv"]


def _procesar_cadena(ruta_suc: str, ruta_prod: str):
    import polars as pl
    s = _leer(ruta_suc, ["id_comercio", "id_bandera", "id_sucursal", "sucursales_codigo_postal", "sucursales_provincia"])
    s = s.with_columns(prov=pl.col("sucursales_provincia").str.strip_chars().str.replace("AR-", ""),
                       cp=pl.col("sucursales_codigo_postal").str.extract(r"(\d{4})").cast(pl.Int32, strict=False))
    s = s.with_columns(region=pl.when((pl.col("prov") == "B") & (pl.col("cp") <= GBA_CP_MAX)).then(pl.lit("GBA"))
                       .otherwise(pl.col("prov").replace_strict(REGION_PROV, default=None)))
    s = s.select("id_comercio", "id_bandera", "id_sucursal", "region").drop_nulls("region")
    # productos: lectura perezosa y por partes (algunas cadenas tienen ~4 millones de filas por día)
    with open(ruta_prod, "rb") as f:
        cab = f.readline().decode("utf-8", "ignore").lstrip("\ufeff").strip().split("|")
    cols = {c.strip().lstrip("\ufeff"): c for c in cab}
    need = ["id_comercio", "id_bandera", "id_sucursal", "id_producto", "productos_descripcion", "productos_precio_lista"]
    if not all(n in cols for n in need):
        raise ValueError("faltan columnas")
    p = (pl.scan_csv(ruta_prod, separator="|", quote_char=None, infer_schema=False, truncate_ragged_lines=True,
                     ignore_errors=True, encoding="utf8-lossy")
           .rename({cols[n]: n for n in need}).select(need)
           .with_columns(precio=pl.col("productos_precio_lista").str.replace(",", ".").cast(pl.Float64, strict=False))
           .filter(pl.col("precio") > 0)
           .join(s.lazy(), on=["id_comercio", "id_bandera", "id_sucursal"])
           .group_by("id_comercio", "region", "id_producto")
           .agg(precio=pl.col("precio").median(), sucursales=pl.len(), desc=pl.col("productos_descripcion").first())
           .with_columns(pl.col("id_comercio").cast(pl.Utf8)))
    return p.collect(engine="streaming")


def procesar_dia(archivo_tar: str, fecha: str) -> pd.DataFrame:
    """Reduce un día de SEPA (.tar.zst del archivo) a mediana de precio por cadena, región y producto."""
    import gc
    import polars as pl
    partes = []
    tmp = tempfile.mkdtemp(prefix="sepa_csv_", dir=os.path.dirname(os.path.abspath(archivo_tar)))
    try:
        for bs, bp in _archivos_por_cadena(archivo_tar, tmp):
            try:
                partes.append(_procesar_cadena(bs, bp))
            except Exception:  # una cadena con archivos rotos no frena el día
                pass
            finally:
                for p in (bs, bp):
                    if os.path.exists(p):
                        os.remove(p)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if not partes:
        return pd.DataFrame()
    r = pl.concat(partes).to_pandas()
    descs = r.drop_duplicates("id_producto")[["id_producto", "desc"]]
    descs["clase"] = [clasificar(x) or clasificar_no_alimentos(x) for x in descs.desc]
    r = r.merge(descs[["id_producto", "clase"]], on="id_producto", how="left")
    # catálogo de carne vacuna fresca (se acumula día a día; ver indices_carne_fresca)
    fres = r[r.clase.isna() | (r.clase == "01.1.2")].drop_duplicates(["id_comercio", "id_producto"])
    fres = fres[[es_carne_fresca(x) for x in fres.desc]]
    if len(fres):
        import fcntl
        ruta_c = SALIDA / "carne_fresca_ids.csv"
        SALIDA.mkdir(parents=True, exist_ok=True)
        with open(str(ruta_c) + ".lock", "w") as lock:  # varios procesos en paralelo: uno por vez
            fcntl.flock(lock, fcntl.LOCK_EX)
            prev = pd.read_csv(ruta_c, dtype=str) if ruta_c.exists() else pd.DataFrame(columns=["id_comercio", "id_producto", "desc"])
            nuevo = fres[["id_comercio", "id_producto", "desc"]].astype(str)
            pd.concat([prev, nuevo]).drop_duplicates(["id_comercio", "id_producto"]).to_csv(ruta_c, index=False)
    # catálogo de descripciones (EAN -> descripción) de los productos clasificados, para emparejar con INDEC
    dd = descs[descs.clase.notna() & descs.id_producto.astype(str).str.fullmatch(r"\d{8,14}")][["id_producto", "desc", "clase"]].astype(str)
    if len(dd):
        import fcntl
        ruta_d = SALIDA / "descripciones.csv"
        with open(str(ruta_d) + ".lock", "w") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            prev = pd.read_csv(ruta_d, dtype=str) if ruta_d.exists() else pd.DataFrame(columns=["id_producto", "desc", "clase"])
            pd.concat([prev, dd]).drop_duplicates("id_producto").to_csv(ruta_d, index=False)
    r = r[r.clase.notna()].drop(columns="desc")
    r["fecha"] = fecha
    r["id_comercio"] = r.id_comercio.astype(str)
    return r[["fecha", "id_comercio", "region", "id_producto", "clase", "precio", "sucursales"]]


def bajar_dia(fecha: str, link: str, destino: Path = CACHE) -> str:
    """Descarga, procesa y guarda un día. Devuelve 'ok', 'vacio' o el error."""
    destino.mkdir(parents=True, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix=f"sepa_{fecha}_")
    try:
        arch = os.path.join(tmp, "d.tar.zst")
        subprocess.run(["curl", "-sS", "--retry", "3", "-o", arch, link], check=True)
        df = procesar_dia(arch, fecha)
        if df.empty:
            return "vacio"
        df.to_parquet(destino / f"{fecha}.parquet", index=False)
        return "ok"
    except Exception as e:  # noqa: BLE001
        return f"error: {e}"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def dias_en_cache(destino: Path = CACHE) -> list[str]:
    return sorted(p.stem for p in destino.glob("????-??-??.parquet"))


# ------------------------------------------------------------------ índices
def promedios_mensuales(meses: list[str], corte: int | None = None, origen: Path = CACHE) -> pd.DataFrame:
    """Promedio del precio de cada producto (cadena x región) en cada mes, con los días hasta `corte` (inclusive)."""
    import polars as pl
    archivos = [str(p) for m in meses for p in sorted(origen.glob(f"{m}-??.parquet"))
                if corte is None or int(p.stem[-2:]) <= corte]
    if not archivos:
        return pd.DataFrame()
    lf = pl.scan_parquet(archivos).select("fecha", "id_comercio", "region", "id_producto", "clase", "precio")
    lf = lf.with_columns(mes=pl.col("fecha").str.slice(0, 7))
    return (lf.group_by("mes", "id_comercio", "region", "id_producto", "clase")
              .agg(p=pl.col("precio").mean(), dias=pl.col("fecha").n_unique())
              .collect(engine="streaming").to_pandas())


def variacion(prev: pd.DataFrame, act: pd.DataFrame, min_dias_prev: int = 8, min_dias_act: int = 3,
              min_productos: int = MIN_PRODUCTOS) -> pd.DataFrame:
    """Variación % por región y clase entre dos meses (promedios por producto)."""
    a = prev[prev.dias >= min_dias_prev]
    b = act[act.dias >= min_dias_act]
    j = a.merge(b, on=["id_comercio", "region", "id_producto", "clase"], suffixes=("_a", "_b"))
    if j.empty:
        return pd.DataFrame()
    j["r"] = np.log(j.p_b / j.p_a)
    j = j[(j.r > np.log(RECORTE[0])) & (j.r < np.log(RECORTE[1]))]
    pc = j.groupby(["region", "clase", "id_comercio"]).agg(r=("r", "mean"), n=("r", "size")).reset_index()
    pc = pc[pc.n >= min_productos]
    pr = pc.groupby(["region", "clase"]).agg(r=("r", "mean"), cadenas=("id_comercio", "nunique"), productos=("n", "sum")).reset_index()
    pr["var_%"] = (np.exp(pr.r) - 1) * 100
    return pr.drop(columns="r")


def indices_del_mes(mes: str, corte: int | None = None, origen: Path = CACHE) -> pd.DataFrame:
    """Variación del mes `mes` (AAAA-MM) contra el anterior, usando los días del mes hasta `corte`."""
    previo = (pd.Timestamp(mes + "-01") - pd.offsets.MonthBegin(1)).strftime("%Y-%m")
    pm = promedios_mensuales([previo], origen=origen)
    am = promedios_mensuales([mes], corte=corte, origen=origen)
    if pm.empty or am.empty:
        return pd.DataFrame()
    v = variacion(pm, am)
    if v.empty:
        return v
    dias_act = sorted({p.stem for p in origen.glob(f"{mes}-??.parquet") if corte is None or int(p.stem[-2:]) <= corte})
    dias_prev = len(list(origen.glob(f"{previo}-??.parquet")))
    v.insert(0, "mes", mes)
    v["dias_mes"] = len(dias_act)
    v["dias_mes_anterior"] = dias_prev
    v["ultimo_dia"] = dias_act[-1] if dias_act else None
    return v


def indices_carne_fresca(mes: str, corte: int | None = None, origen: Path = CACHE) -> pd.DataFrame:
    """Igual que indices_del_mes pero solo con cortes de carne vacuna fresca (clase "01.1.2v")."""
    import polars as pl
    ruta_c = SALIDA / "carne_fresca_ids.csv"
    if not ruta_c.exists():
        return pd.DataFrame()
    claves = pl.from_pandas(pd.read_csv(ruta_c, dtype=str)[["id_comercio", "id_producto"]].drop_duplicates())
    previo = (pd.Timestamp(mes + "-01") - pd.offsets.MonthBegin(1)).strftime("%Y-%m")
    def prom(m, c):
        fs = [str(p) for p in sorted(origen.glob(f"{m}-??.parquet")) if c is None or int(p.stem[-2:]) <= c]
        if not fs:
            return pd.DataFrame()
        lf = (pl.scan_parquet(fs).filter(pl.col("clase") == "01.1.2").select("fecha", "id_comercio", "region", "id_producto", "precio")
                .join(claves.lazy(), on=["id_comercio", "id_producto"]))
        return (lf.group_by("id_comercio", "region", "id_producto").agg(p=pl.col("precio").mean(), dias=pl.col("fecha").n_unique())
                  .collect().to_pandas().assign(clase="01.1.2v"))
    a, b = prom(previo, None), prom(mes, corte)
    if a.empty or b.empty:
        return pd.DataFrame()
    a, b = a.assign(mes=previo), b.assign(mes=mes)
    v = variacion(a, b, min_productos=10)  # hay menos cortes frescos que productos envasados por cadena
    if v.empty:
        return v
    v.insert(0, "mes", mes)
    return v


def leer_indices() -> pd.DataFrame:
    ruta = SALIDA / "indices_mensuales.csv"
    if not ruta.exists():
        return pd.DataFrame()
    d = pd.read_csv(ruta, dtype={"clase": str})
    d["mes"] = pd.to_datetime(d.mes + "-01")
    return d


def recoleccion(dias: int = 60, origen: Path = CACHE) -> pd.DataFrame:
    """Productos clasificados relevados por día y cadena (para el tablero)."""
    filas = []
    for p in sorted(origen.glob("????-??-??.parquet"))[-dias:]:
        d = pd.read_parquet(p, columns=["id_comercio"])
        for c, n in d.id_comercio.value_counts().items():
            filas.append({"fecha": p.stem, "cadena": CADENAS.get(str(c), f"Cadena {c}"), "productos": int(n)})
    return pd.DataFrame(filas)


def arrastre(mes: str, desde_dia: int = 24, origen: Path = CACHE) -> pd.DataFrame:
    """Arrastre que deja el mes anterior: precio de sus últimos días (desde `desde_dia`) contra su promedio, en %.
    Se conoce el día 1 de `mes` y anticipa parte de su variación (INDEC compara promedios mensuales)."""
    import polars as pl
    previo = (pd.Timestamp(mes + "-01") - pd.offsets.MonthBegin(1)).strftime("%Y-%m")
    pm = promedios_mensuales([previo], origen=origen)
    archivos = [str(p) for p in sorted(origen.glob(f"{previo}-??.parquet")) if int(p.stem[-2:]) >= desde_dia]
    if pm.empty or not archivos:
        return pd.DataFrame()
    lf = pl.scan_parquet(archivos).select("fecha", "id_comercio", "region", "id_producto", "clase", "precio")
    fin = (lf.group_by("id_comercio", "region", "id_producto", "clase")
             .agg(p=pl.col("precio").mean(), dias=pl.col("fecha").n_unique())
             .collect(engine="streaming").to_pandas())
    v = variacion(pm, fin, min_dias_act=2)
    if not v.empty:
        v.insert(0, "mes", mes)
    return v
