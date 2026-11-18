"""Fuentes auxiliares con historia: IPC de la Ciudad de Buenos Aires (IPCBA) vía la API de series de datos.gob.ar."""
from __future__ import annotations

import json
import urllib.request

import pandas as pd

from . import DATA

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
API_SERIES = "https://apis.datos.gob.ar/series/api/series/"

# IPCBA base 2021 = 100 (Instituto de Estadística y Censos de la Ciudad). Usa COICOP 2018 (13 divisiones):
# se mapean a las 12 divisiones de INDEC; "12" de INDEC = seguros/serv. financieros + cuidado personal.
IPCBA = {
    "00": "193.2_NIVEL_GENERAL_2021_0_13_2",
    "01": "193.2_ALIMENTOS_CAS_2021_0_32_80",
    "02": "193.2_BEBIDAS_ALACO_2021_0_26_81",
    "03": "193.2_PRENDAS_VEADO_2021_0_22_9",
    "04": "193.2_VIVIENDA_ALES_2021_0_45_98",
    "05": "193.2_EQUIPAMIENGAR_2021_0_32_39",
    "06": "193.2_SALUDLUD_2021_0_5_15",
    "07": "193.2_TRANSPORTERTE_2021_0_10_1",
    "08": "193.2_INFORMACIOION_2021_0_24_37",
    "09": "193.2_RECREACIONURA_2021_0_18_78",
    "10": "193.2_EDUCACIONION_2021_0_9_53",
    "11": "193.2_RESTAURANTLES_2021_0_20_90",
    "12a": "193.2_SEGUROS_SEROS_2021_0_29_0",
    "12b": "193.2_CUIDADO_PEROS_2021_0_40_67",
    "Estacional": "193.2_ESTACIONALLES_2021_0_12_84",
    "Regulados": "193.2_REGULADOSDOS_2021_0_9_38",
    "Resto": "193.2_RESTOSTO_2021_0_5_9",
}


def series(ids: dict[str, str]) -> pd.DataFrame:
    """Baja series de la API de datos.gob.ar. Devuelve índice mensual (columnas = claves de `ids`)."""
    claves, valores = list(ids), list(ids.values())
    partes = []
    for i in range(0, len(valores), 20):
        url = f"{API_SERIES}?ids={','.join(valores[i:i + 20])}&limit=1000&format=json"
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=60) as r:
            d = json.load(r)
        partes.append(pd.DataFrame(d["data"], columns=["periodo"] + claves[i:i + 20]).set_index("periodo"))
    df = pd.concat(partes, axis=1)
    df.index = pd.to_datetime(df.index)
    return df.sort_index()


def actualizar_ipcba() -> pd.DataFrame:
    df = series(IPCBA)
    destino = DATA / "raw" / "caba"
    destino.mkdir(parents=True, exist_ok=True)
    df.to_csv(destino / "ipcba.csv")
    return df


def leer_ipcba() -> pd.DataFrame:
    df = pd.read_csv(DATA / "raw" / "caba" / "ipcba.csv", index_col=0, parse_dates=True)
    return df


# ------------------------------------------------------------------ REM del BCRA
REM_PAGINA = "https://www.bcra.gob.ar/PublicacionesEstadisticas/Relevamiento_Expectativas_de_Mercado.asp"


def actualizar_rem() -> dict:
    """Baja la planilla del último REM y guarda la mediana de inflación mensual esperada en config/externos.yaml."""
    import io
    import re
    import subprocess

    import yaml

    from . import CONFIG
    ua = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"
    get = lambda u: subprocess.run(["curl", "-sSL", "--retry", "3", "--max-time", "90", "-A", ua, u], capture_output=True, check=True).stdout
    html = get(REM_PAGINA).decode("utf-8", "ignore")
    links = sorted(set(re.findall(r'href="([^"]*relevamiento-expectativas-mercado-tablas-(\d{4})-(\d{2})\.xlsx)"', html)), key=lambda x: (x[1], x[2]))
    if not links:
        raise RuntimeError("no se encontró la planilla del REM")
    url, anio, mes = links[-1]
    url = url if url.startswith("http") else "https://www.bcra.gob.ar" + url
    d = pd.read_excel(io.BytesIO(get(url)), sheet_name=0, header=None)
    # primera tabla: IPC nivel general nacional, filas con "var. % mensual"
    inicio = d.index[d.astype(str).apply(lambda r: r.str.contains("IPC nivel general", case=False)).any(axis=1)][0]
    nuevos = {}
    for i in range(inicio + 2, inicio + 12):
        per, ref, med = d.iloc[i, 1], str(d.iloc[i, 2]), d.iloc[i, 3]
        if "mensual" not in ref:
            break
        nuevos[pd.Timestamp(per).strftime("%Y-%m")] = round(float(med), 2)
    ruta = CONFIG / "externos.yaml"
    cfg = yaml.safe_load(ruta.read_text(encoding="utf-8")) or {}
    rem = cfg.get("rem") or {}
    meses_txt = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
    for m, v in nuevos.items():
        rem[m] = {"valor": v, "relevamiento": f"{meses_txt[int(mes) - 1]} {anio}", "fuente": url}
    cfg["rem"] = dict(sorted(rem.items()))
    ruta.write_text("# Referencias externas (se muestran junto al pronóstico; no entran en el cálculo).\n"
                    "# REM del BCRA: mediana de los analistas para la inflación mensual del IPC nacional (se actualiza solo).\n"
                    + yaml.safe_dump(cfg, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return nuevos
