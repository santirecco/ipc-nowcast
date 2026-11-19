"""Indicadores adelantados por clase de alimentos: SEPA (precios de góndola de todo el país),
Mercado Central (verduras y frutas mayoristas) y hacienda (carne).

Para cada clase se estima, con la historia, cuánto corrigen estas fuentes a la proyección estadística:

    real - proyección = a · (SEPA - proyección) + b0 · mayorista del mes + b1 · mayorista del mes anterior

con coeficientes no negativos (a ≤ 1), comunes a las seis regiones (hay pocos meses para estimarlos por región).
Se calibra por separado para dos momentos: mitad de mes (datos hasta el día 15) y mes completo.
Una fuente se usa en una clase solo si mejora el error fuera de muestra (cada mes se predice con coeficientes
estimados únicamente con los meses anteriores).
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import yaml
from scipy.optimize import nnls

from . import CONFIG, DATA, REGIONES, indicadores, mayoristas, sepa
from .modelo import proyeccion_componente

# REGLA ÚNICA (fijada en nov-2026, antes de mirar resultados): para cada clase se prueban TODAS las fuentes candidatas
# de abajo; una fuente se usa si baja el error de SU PROPIA clase, fuera de muestra, al menos MEJORA_MINIMA, con al
# menos MIN_MESES_ELEGIR meses evaluados desde EVAL_DESDE. Entre las que cumplen, se ordenan por error en los meses
# comunes y se usa la primera con datos. No se decide mirando el error del índice nacional (28 meses son pocos y
# premian compensaciones de suerte). El backtest reaplica esta misma regla mes a mes con los meses anteriores.
OPCIONES = {
    "01.1.1": [["sepa"], ["fx"], ["sepa", "fx"], ["arr"], ["sepai"]],
    "01.1.2": [["may"], ["sepa"], ["sepa", "may"], ["sepa_carne"], ["sepa_carne", "may"], ["arr"]],
    "01.1.4": [["sepa"], ["sepa", "fx"], ["arr"], ["sepai"]],
    "01.1.5": [["sepa"], ["fx"], ["sepa", "fx"], ["arr"], ["sepai"]],
    "01.1.6": [["sepa"], ["may"], ["arr"]],
    "01.1.7": [["sepa"], ["may"], ["arr"]],
    "01.1.8": [["sepa"], ["sepa", "fx"], ["arr"], ["sepai"]],
    "01.2.1": [["sepa"], ["fx"], ["sepa", "fx"], ["arr"], ["sepai"]],
    "01.2.2": [["sepa"], ["sepa", "fx"], ["arr"], ["sepai"]],
    "02.1": [["sepa"]],
    "02.2": [["ipc"]],
    "03.1": [["fx"], ["ipc"]],
    "03.2": [["ipc"]],
    "04.1.1": [["icl"], ["ipc"], ["icl", "ipc"]],
    "05": [["fx"]],
    "05.6": [["sepa"], ["ipc"]],
    "06.1": [["sepa"], ["ipc"]],
    "07.1": [["autos"], ["fx"]],
    "07.2.2": [["nafta"], ["nafta", "fx"]],
    "08.3": [["ipc"]],
    "09.5": [["ipc"]],
    "10": [["ipc"]],
    "11.1": [["ipc"]],
    "12.1": [["sepa"], ["ipc"]],
}
CLASES = list(OPCIONES)
MIN_MESES_ELEGIR = 6  # meses evaluados mínimos para decidir si una fuente sirve
T_MINIMO = 0.0  # se probó exigir t >= 2 (nov-2026): descartaba demasiadas fuentes y empeoraba mitad y fin de mes
ESTADISTICAS = {"ipc", "icl", "arr"}  # fuentes que no son datos del mes sino una mejor estimación con la historia
# fuentes que se conocen el día 1 del mes (se pueden usar al inicio): las estadísticas y las listas de autos 0 km
AL_INICIO = ESTADISTICAS | {"autos"}
RUTA_AUTOS = DATA / "precios" / "autos" / "listas_0km.csv"
NOMBRES = {"01.1.1": "Pan y cereales", "01.1.2": "Carnes y derivados", "01.1.4": "Leche, lácteos y huevos",
           "01.1.5": "Aceites, grasas y manteca", "01.1.6": "Frutas", "01.1.7": "Verduras, tubérculos y legumbres",
           "01.1.8": "Azúcar, dulces y golosinas", "01.2.1": "Café, té, yerba y cacao",
           "01.2.2": "Aguas, gaseosas y jugos", "07.2.2": "Combustibles", "07.1": "Compra de vehículos",
           "03.1": "Ropa", "09.1": "Equipos audiovisuales y de computación", "05": "Equipamiento del hogar",
           "02.1": "Bebidas alcohólicas", "02.2": "Tabaco", "03.2": "Calzado", "04.1.1": "Alquiler de la vivienda",
           "05.6": "Limpieza y mantenimiento del hogar", "06.1": "Medicamentos", "08.3": "Telefonía e internet",
           "09.5": "Diarios, libros y papelería", "11.1": "Restaurantes y comidas fuera del hogar", "12.1": "Cuidado personal",
           "10": "Educación"}
ETIQUETA = {"sepa": "góndolas (SEPA)", "sepa_carne": "cortes frescos en góndola (SEPA)", "may": "mayorista", "nafta": "precio de surtidor (YPF)", "fx": "dólar mayorista",
            "ipc": "inflación reciente", "icl": "índice de contratos de alquiler (ICL)",
            "arr": "arrastre del mes anterior (SEPA)",
            "sepai": "precios de SEPA de los productos que mide INDEC",
            "autos": "listas de precios de autos 0 km"}
MAYORISTA = {"01.1.7": "Mercado Central", "01.1.6": "Mercado Central", "01.1.2": "hacienda (Cañuelas)"}
CORTES = ["15", "22", "completo"]  # precios hasta el día 15, hasta el 22 y mes completo
CON_TENDENCIA = {"01.1.2"}
MIN_MESES_AJUSTE = 4       # meses mínimos de historia para estimar coeficientes (comunes a 6 regiones)
EVAL_DESDE = pd.Timestamp("2024-01-01")  # la decisión se toma con el error de 2024 en adelante (régimen actual)
MEJORA_MINIMA = 0.02       # pp de mejora del error medio fuera de muestra para usar la fuente
RUTA_CALIB = CONFIG / "calibracion_adelantados.yaml"
RUTA_BT = DATA / "precios" / "adelantados_backtest.csv"


def _mayorista(corte: str) -> pd.DataFrame:
    c = None if corte == "completo" else int(corte)
    mc = mayoristas.serie_mercado_central(c)
    hac = mayoristas.serie_hacienda(c)
    hac_full = mayoristas.serie_hacienda(None)
    mc_full = mayoristas.serie_mercado_central(None)
    out = pd.DataFrame(index=sorted(set(mc.index) | set(hac.index)))
    for clase in ("01.1.7", "01.1.6"):
        if clase in mc:
            out[clase] = mc[clase]
            out[clase + "_l1"] = mc_full[clase].shift(1, freq="MS").reindex(out.index)
    out["01.1.2"] = hac
    out["01.1.2_l1"] = hac_full.shift(1, freq="MS").reindex(out.index)
    return out


def _otros(corte: str) -> pd.DataFrame:
    c = None if corte == "completo" else int(corte)
    nafta = indicadores.serie_nafta()
    fx, fx_full = indicadores.serie_dolar(c), indicadores.serie_dolar(None)
    o = pd.DataFrame({"nafta": nafta, "fx": fx})
    o["nafta_l1"] = nafta.shift(1, freq="MS").reindex(o.index)
    o["fx_l1"] = fx_full.shift(1, freq="MS").reindex(o.index)
    icl = indicadores.serie_icl()
    o = o.join(icl, how="outer") if not icl.empty else o.assign(icl_a=np.nan, icl_m=np.nan)
    return o


def tabla(nc, corte: str) -> pd.DataFrame:
    """Una fila por mes, región y clase con: real, proyección estadística, SEPA, mayorista, combustibles y dólar."""
    idx = sepa.leer_indices()
    idx = idx[idx.corte.astype(str) == corte] if not idx.empty else idx
    may = _mayorista(corte)
    otros = _otros(corte)
    ipc = nc.V["Nacional"]["00"]
    ipc_l1 = ipc.shift(1, freq="MS")
    ipc_p3 = ipc.rolling(3).mean().shift(1, freq="MS")
    meses = sorted(set(idx.mes if not idx.empty else []) | set(may.index) | set(otros.dropna(how="all").index)
                   | {m for m in ipc_l1.index if m >= pd.Timestamp("2018-01-01")})
    filas = []
    for mes in meses:
        for r in REGIONES:
            for c in CLASES:
                if (r, c) not in nc.Vap.columns:
                    continue
                serie = nc.Vap[r][c]
                real = serie.get(mes, np.nan)
                p = float(proyeccion_componente(nc.Vap[r][[c]], mes).iloc[0])
                s, sc = np.nan, np.nan
                if not idx.empty:
                    f = idx[(idx.mes == mes) & (idx.region == r) & (idx.clase == c)]
                    if not f.empty and f.cadenas.iloc[0] >= 2:
                        s = float(f["var_%"].iloc[0])
                    if c == "01.1.2":
                        f = idx[(idx.mes == mes) & (idx.region == r) & (idx.clase == "01.1.2v")]
                        if not f.empty and f.cadenas.iloc[0] >= 2:
                            sc = float(f["var_%"].iloc[0])
                m0 = may[c].get(mes, np.nan) if c in may else np.nan
                m1 = may[c + "_l1"].get(mes, np.nan) if c + "_l1" in may else np.nan
                o = otros.loc[mes] if mes in otros.index else None
                ox = lambda k: float(o[k]) if o is not None and pd.notna(o[k]) else np.nan
                filas.append({"mes": mes, "region": r, "clase": c, "corte": corte, "real": real, "proy": p, "sepa": s, "sepa_carne": sc, "may": m0, "may_l1": m1,
                              "nafta": ox("nafta"), "nafta_l1": ox("nafta_l1"), "fx": ox("fx"), "fx_l1": ox("fx_l1"),
                              "icl_a": ox("icl_a"), "icl_m": ox("icl_m"),
                              "ipc_l1": float(ipc_l1.get(mes, np.nan)), "ipc_p3": float(ipc_p3.get(mes, np.nan))})
    t = pd.DataFrame(filas)
    if t.empty:
        return t
    # señal de SEPA hecha solo con los productos que INDEC mide (variedades con precio promedio publicado)
    rv = sepa.SALIDA / "indices_variedades.csv"
    if rv.exists():
        iv = pd.read_csv(rv, dtype={"clase": str})
        iv = iv[iv.corte.astype(str) == corte]
        iv = iv.groupby(["mes", "region", "clase"])["var_%"].mean().rename("sepai").reset_index()
        iv["mes"] = pd.to_datetime(iv.mes + "-01")
        t = t.merge(iv, on=["mes", "region", "clase"], how="left")
    else:
        t["sepai"] = np.nan
    # listas de precios de autos 0 km (aumento promedio del mes, igual para todas las regiones)
    if RUTA_AUTOS.exists():
        au = pd.read_csv(RUTA_AUTOS)
        au["mes"] = pd.to_datetime(au.mes + "-01")
        au = au.set_index("mes").aumento_lista_pct.astype(float)
        t["autos"] = t.mes.map(au)
        t["autos_l1"] = t.mes.map(au.shift(1, freq="MS"))
    else:
        t["autos"], t["autos_l1"] = np.nan, np.nan
    # arrastre del mes anterior medido con SEPA (se conoce el día 1): sorpresa respecto de su mediana reciente
    ra = sepa.SALIDA / "arrastre.csv"
    if ra.exists():
        ar = pd.read_csv(ra, dtype={"clase": str})
        ar["mes"] = pd.to_datetime(ar.mes + "-01")
        ar = ar[ar.cadenas >= 2][["mes", "region", "clase", "var_%"]].rename(columns={"var_%": "arr"}).sort_values("mes")
        ar["arr_s"] = ar.arr - ar.groupby(["region", "clase"]).arr.transform(lambda x: x.shift(1).rolling(6, min_periods=3).median())
        t = t.merge(ar, on=["mes", "region", "clase"], how="left")
    else:
        t["arr"], t["arr_s"] = np.nan, np.nan
    # tendencia del mayorista: mediana de sus variaciones (mes completo) en los 6 meses previos
    full = {"01.1.7": mayoristas.serie_mercado_central(None).get("01.1.7"),
            "01.1.6": mayoristas.serie_mercado_central(None).get("01.1.6"),
            "01.1.2": mayoristas.serie_hacienda(None)}
    t["tend"] = np.nan
    for c, serie in full.items():
        if serie is None or serie.empty:
            continue
        tend = serie.rolling(6, min_periods=3).median()
        tend.index = tend.index + pd.offsets.MonthBegin(1)  # la tendencia conocida al empezar el mes siguiente
        sel = t.clase == c
        t.loc[sel, "tend"] = t.loc[sel, "mes"].map(tend)
    return t


def _features(t: pd.DataFrame, fuentes: list[str]) -> np.ndarray:
    cols = []
    if "sepa" in fuentes:
        cols.append(t.sepa - t.proy)
    if "sepa_carne" in fuentes:
        cols.append(t.sepa_carne.astype(float) - t.proy)
    if "may" in fuentes:
        # Hacienda: desvío respecto de su tendencia (la carne minorista ajusta lento y con rezago).
        # Verduras y frutas: variación mayorista tal cual (restarle la tendencia empeoraba el error fuera de muestra).
        tend = np.where(t.clase.isin(CON_TENDENCIA), t.tend.fillna(0).astype(float), 0.0)
        cols.append(t["may"].astype(float) - tend)
        cols.append(t["may_l1"].astype(float) - tend)
    if "nafta" in fuentes:
        # a mitad de mes no se sabe todavía el precio de fin de mes: solo el cambio del mes anterior (arrastre)
        # forma "reemplazo": el precio de surtidor reemplaza a la proyección, repartido entre este mes y el anterior
        p = t.proy.astype(float)
        if (t.corte == "completo").any():
            cols.append(t["nafta"].astype(float) - p)
        cols.append(t["nafta_l1"].astype(float) - p)
    if "fx" in fuentes:
        cols.append(t["fx"].astype(float))
        cols.append(t["fx_l1"].astype(float))
    if "sepai" in fuentes:
        cols.append(t["sepai"].astype(float) - t.proy.astype(float))
    if "autos" in fuentes:
        cols.append(t["autos"].astype(float) - t.proy.astype(float))
        cols.append(t["autos_l1"].astype(float) - t.proy.astype(float))
    if "arr" in fuentes:
        cols.append(t["arr_s"].astype(float))
        cols.append(-t["arr_s"].astype(float))
    if "icl" in fuentes:
        p = t.proy.astype(float)
        cols.append(t["icl_a"].astype(float) - p)
        cols.append(t["icl_m"].astype(float) - p)
    if "ipc" in fuentes:
        p = t.proy.astype(float)
        cols.append(t["ipc_l1"].astype(float) - p)
        cols.append(t["ipc_p3"].astype(float) - p)
    return np.column_stack(cols) if cols else np.zeros((len(t), 0))


def _ajustar(t: pd.DataFrame, fuentes: list[str]) -> np.ndarray:
    X = _features(t, fuentes)
    y = (t.real - t.proy).values
    # ridge liviano para estabilidad: equivale a sumar un mes "neutro" (6 regiones con coeficiente cero),
    # que pesa mucho con poca historia y casi nada con mucha
    lam = np.sqrt(6.0)
    Xa = np.vstack([X, lam * np.eye(X.shape[1])])
    ya = np.concatenate([y, np.zeros(X.shape[1])])
    b, _ = nnls(Xa, ya)
    if "sepa" in fuentes:
        b[0] = min(b[0], 1.0)
    if "sepa_carne" in fuentes:  # los cortes de góndola se mueven menos que la carnicería: se permite amplificar
        b[0] = min(b[0], 3.0)
    return b


def _disponibles(t: pd.DataFrame, fuentes: list[str]) -> pd.Series:
    ok = t.real.notna() & t.proy.notna()
    if "sepa" in fuentes:
        ok &= t.sepa.notna()
    if "sepa_carne" in fuentes:
        ok &= t.sepa_carne.notna()
    if "may" in fuentes:
        ok &= t["may"].notna() & t["may_l1"].notna()
    if "nafta" in fuentes:
        ok &= t["nafta_l1"].notna() & (t["nafta"].notna() | (t.corte != "completo"))
    if "fx" in fuentes:
        ok &= t["fx"].notna() & t["fx_l1"].notna()
    if "ipc" in fuentes:
        ok &= t["ipc_l1"].notna() & t["ipc_p3"].notna()
    if "icl" in fuentes:
        ok &= t["icl_a"].notna() & t["icl_m"].notna()
    if "arr" in fuentes:
        ok &= t["arr_s"].notna()
    if "sepai" in fuentes:
        ok &= t["sepai"].notna()
    if "autos" in fuentes:
        ok &= t["autos"].notna() & t["autos_l1"].notna()
    return ok


def evaluar_clase(t: pd.DataFrame, clase: str) -> list[dict]:
    """Errores fuera de muestra de cada combinación de fuentes para una clase."""
    tc = t[t.clase == clase]
    opciones = OPCIONES.get(clase, [["sepa"]])
    res = []
    for fuentes in opciones:
        d = tc[_disponibles(tc, fuentes)].sort_values("mes")
        meses = sorted(d.mes.unique())
        preds = []
        for i, mes in enumerate(meses):
            if i < MIN_MESES_AJUSTE:
                continue
            ent = d[d.mes < mes]
            b = _ajustar(ent, fuentes)
            te = d[d.mes == mes]
            pr = te.proy.values + _features(te, fuentes) @ b
            preds.append(te.assign(pred=pr))
        if not preds:
            continue
        p = pd.concat(preds)
        p = p[p.mes >= EVAL_DESDE]
        if p.empty:
            continue
        res.append({"clase": clase, "fuentes": "+".join(fuentes), "meses": p.mes.nunique(), "obs": len(p),
                    "oos_todo": pd.concat(preds),
                    "error_proyeccion": float((p.real - p.proy).abs().mean()),
                    "error_con_fuente": float((p.real - p.pred).abs().mean()),
                    "coef": [round(float(x), 3) for x in _ajustar(d, fuentes)], "oos": p})
    return res


def _elegir(opciones: list[dict], hasta=None) -> list[dict]:
    """La regla única: opciones que bajan el error de su clase (meses EVAL_DESDE..hasta, sin incluir `hasta`),
    ordenadas por error en los meses comunes."""
    utiles = []
    for o in opciones:
        p = o["oos_todo"]
        p = p[(p.mes >= EVAL_DESDE) & ((p.mes < hasta) if hasta is not None else True)]
        if p.mes.nunique() < MIN_MESES_ELEGIR:
            continue
        ep, ef = float((p.real - p.proy).abs().mean()), float((p.real - p.pred).abs().mean())
        # diferencia de errores por mes (promedio de las regiones): ¿la mejora es clara o puede ser ruido?
        dm = ((p.real - p.proy).abs() - (p.real - p.pred).abs()).groupby(p.mes).mean()
        t = dm.mean() / (dm.std(ddof=1) / np.sqrt(len(dm))) if len(dm) > 1 and dm.std(ddof=1) > 0 else 0.0
        if ep - ef >= MEJORA_MINIMA and t >= T_MINIMO:
            utiles.append((o, p, ep, ef))
    if not utiles:
        return []
    comunes = set.intersection(*[set(p.mes) for _, p, _, _ in utiles])

    def err_comun(x):
        p = x[1][x[1].mes.isin(comunes)]
        return float((p.real - p.pred).abs().mean()) if len(p) else x[3]
    utiles.sort(key=err_comun)
    return [dict(o, error_proyeccion=ep, error_con_fuente=ef) for o, _, ep, ef in utiles]


def calibrar(nc) -> tuple[dict, pd.DataFrame, pd.DataFrame]:
    """Calibración vigente (regla única con todos los meses) y backtest anidado: en cada mes la regla se aplica
    solo con los meses anteriores, así el error del backtest incluye el costo de elegir fuentes."""
    calib, resumen, backtests = {}, [], []
    for corte in CORTES:
        t = tabla(nc, corte)
        calib[corte] = {}
        for clase in CLASES:
            opciones = evaluar_clase(t, clase)
            for o in opciones:
                resumen.append({k: v for k, v in o.items() if k not in ("oos", "oos_todo")} | {"corte": corte})
            utiles = _elegir(opciones)
            if utiles:
                calib[corte][clase] = [{"fuentes": o["fuentes"].split("+"), "coef": o["coef"],
                                        "error_proyeccion": round(o["error_proyeccion"], 3),
                                        "error_con_fuente": round(o["error_con_fuente"], 3), "meses": o["meses"]}
                                       for o in utiles]
            # backtest anidado
            meses = sorted({m for o in opciones for m in o["oos_todo"].mes if m >= EVAL_DESDE})
            for m in meses:
                el = _elegir(opciones, hasta=m)
                if not el:
                    continue
                pr = pd.concat([o["oos_todo"][o["oos_todo"].mes == m].assign(orden=k, fuentes=o["fuentes"])
                                for k, o in enumerate(el)])
                if pr.empty:
                    continue
                mejor = pr.sort_values("orden").drop_duplicates(["region"]).assign(solo_inicio=False)
                ini = np.array([set(str(x).split("+")) <= AL_INICIO for x in pr.fuentes], dtype=bool)
                est = pr[ini].sort_values("orden").drop_duplicates(["region"])
                ya = set(mejor[np.array([set(str(x).split("+")) <= AL_INICIO for x in mejor.fuentes], dtype=bool)].region)
                est = est[~est.region.isin(ya)].assign(solo_inicio=True)
                backtests.append(pd.concat([mejor, est]).assign(corte=corte)[
                    ["mes", "corte", "region", "clase", "fuentes", "real", "proy", "pred", "solo_inicio"]])
    RUTA_CALIB.write_text("# Generado por scripts/calibrar_adelantados.py: no editar a mano.\n"
                          "# Regla única: por clase, las fuentes que bajan el error de la clase fuera de muestra, de mejor a peor.\n"
                          + yaml.safe_dump(calib, allow_unicode=True, sort_keys=False), encoding="utf-8")
    bt = pd.concat(backtests) if backtests else pd.DataFrame()
    if not bt.empty:
        RUTA_BT.parent.mkdir(parents=True, exist_ok=True)
        bt.sort_values(["corte", "mes", "clase", "region"]).to_csv(RUTA_BT, index=False, float_format="%.4f")
    return calib, pd.DataFrame(resumen), bt


def leer_calibracion() -> dict:
    if not RUTA_CALIB.exists():
        return {}
    return yaml.safe_load(RUTA_CALIB.read_text(encoding="utf-8")) or {}


def informacion(nc, mes: pd.Timestamp, hoy: pd.Timestamp | None = None) -> list[dict]:
    """Ítems de información del mes (para Nowcast.informacion_del_mes) con los datos disponibles hoy."""
    calib = leer_calibracion()
    if not calib:
        return []
    hoy = hoy or pd.Timestamp.today()
    idx = sepa.leer_indices()
    actual = sepa.SALIDA / "indices_diarios.csv"
    # momento: si el mes ya terminó, mes completo; si no, mitad de mes (o completo desde el día 21)
    corte = "completo" if hoy >= mes + pd.offsets.MonthEnd(0) else "22" if hoy.day >= 22 else "15"
    temprano = hoy < mes + pd.Timedelta(days=4)  # muy pocos días: solo las mejoras estadísticas
    t = tabla(nc, corte)
    if t.empty:
        return []
    t = t[t.mes == mes]
    # SEPA en curso: usar el último corte disponible (los índices del mes en curso se recalculan a diario)
    if actual.exists():
        dd = pd.read_csv(actual, dtype={"clase": str})
        dd = dd[dd.mes == f"{mes:%Y-%m}"]
        if not dd.empty:
            u = dd[dd.fecha == dd.fecha.max()].set_index(["region", "clase"])["var_%"]
            t = t.copy()
            t["sepa"] = [u.get((r, c), s) for r, c, s in zip(t.region, t.clase, t.sepa)]
    # hacienda antes del día 15: todavía no hay primera quincena completa, se usa lo que va del mes
    if t[t.clase == "01.1.2"]["may"].isna().all():
        mtd = mayoristas.serie_hacienda(None)
        if mes in mtd.index:
            t = t.copy()
            t.loc[t.clase == "01.1.2", "may"] = float(mtd.loc[mes])
    info = []
    for clase, opciones in (calib.get(corte) or {}).items():
        if isinstance(opciones, dict):
            opciones = [opciones]
        for _, f in t[t.clase == clase].iterrows():
            fila = f.to_frame().T.astype({k: float for k in ["sepa", "sepa_carne", "may", "may_l1", "proy", "tend", "nafta", "nafta_l1", "fx", "fx_l1", "ipc_l1", "ipc_p3", "icl_a", "icl_m", "arr", "autos", "autos_l1"]})
            cfg = next((o for o in opciones if _disponibles(fila.assign(real=0.0), o["fuentes"]).iloc[0]
                        and (not temprano or set(o["fuentes"]) <= AL_INICIO)), None)
            if cfg is None:
                continue
            fuentes, b = cfg["fuentes"], np.array(cfg["coef"])
            pred = float(f.proy + (_features(fila, fuentes) @ b)[0])
            pc = lambda v: f"{v:+.1f}%".replace(".", ",").replace("-", "−")
            det = []
            if "sepa" in fuentes:
                det.append(f"góndolas de todo el país (SEPA) {pc(f.sepa)} en lo que va del mes")
            if "sepa_carne" in fuentes:
                det.append(f"cortes de carne fresca en góndola (SEPA) {pc(f.sepa_carne)} en lo que va del mes")
            if "may" in fuentes:
                det.append(f"{MAYORISTA[clase]} {pc(f['may'])} este mes y {pc(f['may_l1'])} el anterior")
            if "nafta" in fuentes:
                det.append(f"surtidor YPF {pc(f['nafta_l1'])} el mes anterior" + ("" if corte != "completo" or pd.isna(f["nafta"]) else f" y {pc(f['nafta'])} este mes"))
            if "fx" in fuentes:
                det.append(f"dólar mayorista {pc(f['fx'])} este mes y {pc(f['fx_l1'])} el anterior")
            if "ipc" in fuentes:
                det.append(f"inflación general {pc(f['ipc_l1'])} el mes pasado y {pc(f['ipc_p3'])} promedio de 3 meses")
            if "autos" in fuentes and pd.notna(f["autos"]):
                det.append(f"las automotrices subieron sus listas {pc(f['autos'])} este mes y {pc(f['autos_l1'])} el anterior")
            if "arr" in fuentes and pd.notna(f["arr"]):
                det.append(f"a fin del mes pasado los precios quedaron {pc(f['arr'])} sobre su promedio")
            if "icl" in fuentes:
                det.append(f"ICL: ajuste anual de contratos {pc(f['icl_a'] * 12)} y {pc(f['icl_m'])} en el mes")
            nombre_f = " + ".join(ETIQUETA[x] if x != "may" else f"mayorista: {MAYORISTA[clase]}" for x in fuentes)
            info.append({"region": f.region, "componente": clase,
                         "fuente": nombre_f[:1].upper() + nombre_f[1:],
                         "estadistica": set(fuentes) <= ESTADISTICAS,
                         "valor": pred, "parte": 1.0, "detalle": ("; ".join(det))[:1].upper() + ("; ".join(det))[1:]})
    return info


def informacion_historica(mes: pd.Timestamp, corte: str, solo_estadistica: bool = False) -> list[dict]:
    """Ítems con las predicciones fuera de muestra guardadas (para el backtest del modelo completo)."""
    if not RUTA_BT.exists():
        return []
    bt = pd.read_csv(RUTA_BT, dtype={"clase": str, "corte": str}, parse_dates=["mes"])
    bt = bt[(bt.mes == mes) & (bt.corte == corte)]
    if "solo_inicio" not in bt:
        bt = bt.assign(solo_inicio=False)
    est = bt.fuentes.apply(lambda x: set(str(x).split("+")) <= AL_INICIO)
    if solo_estadistica:
        bt = bt[est]
    else:
        bt = bt[~bt.solo_inicio.astype(bool)]
    return [{"region": f.region, "componente": f.clase, "fuente": f.fuentes, "valor": float(f.pred), "parte": 1.0,
             "estadistica": bool(e), "detalle": "backtest"} for (_, f), e in zip(bt.iterrows(), est.loc[bt.index])]
