"""Descarga y lectura de las series oficiales del IPC de INDEC."""
from __future__ import annotations

import urllib.request
from pathlib import Path

import pandas as pd
import yaml

from . import CONFIG, DATA

BASE_URL = "https://www.indec.gob.ar/ftp/cuadros/economia/"
ARCHIVOS = {
    "divisiones": "serie_ipc_divisiones.csv",  # nacional + 6 regiones: divisiones, bienes/servicios, categorías
    "aperturas": "serie_ipc_aperturas.csv",    # 6 regiones: divisiones, grupos y clases
}
RAW = DATA / "raw" / "indec"


def descargar(destino: Path = RAW) -> dict[str, Path]:
    """Baja los CSV de INDEC y los guarda tal cual (latin-1, separador ';')."""
    destino.mkdir(parents=True, exist_ok=True)
    salida = {}
    for clave, nombre in ARCHIVOS.items():
        ruta = destino / nombre
        req = urllib.request.Request(BASE_URL + nombre, headers={"User-Agent": "Mozilla/5.0 ipc-nowcast"})
        with urllib.request.urlopen(req, timeout=120) as r:
            contenido = r.read()
        if len(contenido) < 100_000:
            raise RuntimeError(f"{nombre}: descarga sospechosamente chica ({len(contenido)} bytes)")
        ruta.write_bytes(contenido)
        salida[clave] = ruta
    return salida


def leer(clave: str, ruta: Path | None = None) -> pd.DataFrame:
    """Devuelve la serie en formato largo y limpio.

    Columnas: region, codigo, descripcion, clasificador, periodo (fin de mes), indice, var_m, var_ia
    """
    ruta = ruta or RAW / ARCHIVOS[clave]
    df = pd.read_csv(ruta, sep=";", encoding="latin-1", dtype=str)
    df.columns = [c.strip() for c in df.columns]
    desc = [c for c in df.columns if c.lower().startswith("descripcion")][0]
    num = lambda s: pd.to_numeric(s.str.replace(",", ".", regex=False), errors="coerce")
    out = pd.DataFrame({
        "region": df["Region"].str.strip(),
        "codigo": df["Codigo"].str.strip().replace({"0": "00"}),
        "descripcion": df[desc].str.strip(),
        "clasificador": df["Clasificador"].str.strip(),
        "periodo": pd.to_datetime(df["Periodo"].str.strip(), format="%Y%m"),
        "indice": num(df["Indice_IPC"]),
        "var_m": num(df["v_m_IPC"]),
        "var_ia": num(df["v_i_a_IPC"]),
    })
    return out.sort_values(["region", "codigo", "periodo"]).reset_index(drop=True)


def ponderaciones_base() -> tuple[dict[str, float], pd.DataFrame, dict[str, str]]:
    """(pesos regionales, matriz división x región en %, nombres de divisiones)."""
    cfg = yaml.safe_load((CONFIG / "ponderaciones_base.yaml").read_text(encoding="utf-8"))
    regiones = {k: float(v) for k, v in cfg["regiones"].items()}
    nombres = {k: v["nombre"] for k, v in cfg["divisiones"].items()}
    w = pd.DataFrame({k: {r: v[r] for r in regiones} for k, v in cfg["divisiones"].items()}).T
    return regiones, w.astype(float), nombres
