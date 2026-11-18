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

from . import CONFIG, DATA, REGIONES, mayoristas, sepa
from .modelo import proyeccion_componente

CLASES = ["01.1.1", "01.1.2", "01.1.4", "01.1.5", "01.1.6", "01.1.7", "01.1.8", "01.2.1", "01.2.2"]
NOMBRES = {"01.1.1": "Pan y cereales", "01.1.2": "Carnes y derivados", "01.1.4": "Leche, lácteos y huevos",
           "01.1.5": "Aceites, grasas y manteca", "01.1.6": "Frutas", "01.1.7": "Verduras, tubérculos y legumbres",
           "01.1.8": "Azúcar, dulces y golosinas", "01.2.1": "Café, té, yerba y cacao",
           "01.2.2": "Aguas, gaseosas y jugos"}
MAYORISTA = {"01.1.7": "Mercado Central", "01.1.6": "Mercado Central", "01.1.2": "hacienda (Cañuelas)"}
CORTES = ["15", "completo"]
CON_TENDENCIA = {"01.1.2"}
MIN_MESES_AJUSTE = 4       # meses mínimos de historia para estimar coeficientes (comunes a 6 regiones)
MEJORA_MINIMA = 0.02       # pp de mejora del error medio fuera de muestra para usar la fuente
RUTA_CALIB = CONFIG / "calibracion_adelantados.yaml"
RUTA_BT = DATA / "precios" / "adelantados_backtest.csv"


def _mayorista(corte: str) -> pd.DataFrame:
    c = 15 if corte == "15" else None
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


def tabla(nc, corte: str) -> pd.DataFrame:
    """Una fila por mes, región y clase con: real, proyección estadística, SEPA y mayorista (actual y anterior)."""
    idx = sepa.leer_indices()
    idx = idx[idx.corte.astype(str) == corte] if not idx.empty else idx
    may = _mayorista(corte)
    meses = sorted(set(idx.mes) if not idx.empty else set()) + [m for m in may.index if idx.empty or m not in set(idx.mes)]
    meses = sorted(set(meses))
    filas = []
    for mes in meses:
        for r in REGIONES:
            for c in CLASES:
                if (r, c) not in nc.Vap.columns:
                    continue
                serie = nc.Vap[r][c]
                real = serie.get(mes, np.nan)
                p = float(proyeccion_componente(nc.Vap[r][[c]], mes).iloc[0])
                s = np.nan
                if not idx.empty:
                    f = idx[(idx.mes == mes) & (idx.region == r) & (idx.clase == c)]
                    if not f.empty and f.cadenas.iloc[0] >= 2:
                        s = float(f["var_%"].iloc[0])
                m0 = may[c].get(mes, np.nan) if c in may else np.nan
                m1 = may[c + "_l1"].get(mes, np.nan) if c + "_l1" in may else np.nan
                filas.append({"mes": mes, "region": r, "clase": c, "real": real, "proy": p, "sepa": s, "may": m0, "may_l1": m1})
    t = pd.DataFrame(filas)
    if t.empty:
        return t
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
    if "may" in fuentes:
        # Hacienda: desvío respecto de su tendencia (la carne minorista ajusta lento y con rezago).
        # Verduras y frutas: variación mayorista tal cual (restarle la tendencia empeoraba el error fuera de muestra).
        tend = np.where(t.clase.isin(CON_TENDENCIA), t.tend.fillna(0).astype(float), 0.0)
        cols.append(t["may"].astype(float) - tend)
        cols.append(t["may_l1"].astype(float) - tend)
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
    return b


def _disponibles(t: pd.DataFrame, fuentes: list[str]) -> pd.Series:
    ok = t.real.notna() & t.proy.notna()
    if "sepa" in fuentes:
        ok &= t.sepa.notna()
    if "may" in fuentes:
        ok &= t["may"].notna() & t["may_l1"].notna()
    return ok


def evaluar_clase(t: pd.DataFrame, clase: str) -> list[dict]:
    """Errores fuera de muestra de cada combinación de fuentes para una clase."""
    tc = t[t.clase == clase]
    opciones = [["sepa"]]
    if clase in MAYORISTA:
        opciones += [["may"], ["sepa", "may"]]
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
        res.append({"clase": clase, "fuentes": "+".join(fuentes), "meses": p.mes.nunique(), "obs": len(p),
                    "error_proyeccion": float((p.real - p.proy).abs().mean()),
                    "error_con_fuente": float((p.real - p.pred).abs().mean()),
                    "coef": [round(float(x), 3) for x in _ajustar(d, fuentes)], "oos": p})
    return res


def calibrar(nc) -> tuple[dict, pd.DataFrame, pd.DataFrame]:
    """Para cada clase y momento, ordena las combinaciones de fuentes que mejoran (de mejor a peor, comparadas en
    los mismos meses) y guarda sus coeficientes. En cada mes se usa la primera que tenga datos."""
    calib, resumen, backtests = {}, [], []
    for corte in CORTES:
        t = tabla(nc, corte)
        calib[corte] = {}
        for clase in CLASES:
            opciones = evaluar_clase(t, clase)
            for o in opciones:
                resumen.append({k: v for k, v in o.items() if k != "oos"} | {"corte": corte})
            utiles = [o for o in opciones if o["error_proyeccion"] - o["error_con_fuente"] >= MEJORA_MINIMA]
            if not utiles:
                continue
            # comparación justa: error en los meses que tienen todas las opciones útiles
            comunes = set.intersection(*[set(o["oos"].mes) for o in utiles])

            def err_comun(o):
                p = o["oos"][o["oos"].mes.isin(comunes)]
                return float((p.real - p.pred).abs().mean()) if len(p) else o["error_con_fuente"]
            utiles.sort(key=err_comun)
            calib[corte][clase] = [{"fuentes": o["fuentes"].split("+"), "coef": o["coef"],
                                    "error_proyeccion": round(o["error_proyeccion"], 3),
                                    "error_con_fuente": round(o["error_con_fuente"], 3), "meses": o["meses"]}
                                   for o in utiles]
            # backtest: en cada mes y región, la predicción de la mejor opción disponible
            preds = pd.concat([o["oos"].assign(orden=k, fuentes=o["fuentes"]) for k, o in enumerate(utiles)])
            preds = preds.sort_values("orden").drop_duplicates(["mes", "region"])
            backtests.append(preds.assign(corte=corte)[["mes", "corte", "region", "clase", "fuentes", "real", "proy", "pred"]])
    RUTA_CALIB.write_text("# Generado por scripts/calibrar_adelantados.py: no editar a mano.\n"
                          "# Por clase, las combinaciones de fuentes que mejoran, de mejor a peor: se usa la primera con datos.\n"
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
    corte = "completo" if (hoy >= mes + pd.offsets.MonthEnd(0) or hoy.day >= 21) else "15"
    if hoy < mes + pd.Timedelta(days=4):
        return []  # muy pocos días: la información todavía no alcanza
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
            fila = f.to_frame().T.astype({"sepa": float, "may": float, "may_l1": float, "proy": float, "tend": float})
            cfg = next((o for o in opciones if _disponibles(fila.assign(real=0.0), o["fuentes"]).iloc[0]), None)
            if cfg is None:
                continue
            fuentes, b = cfg["fuentes"], np.array(cfg["coef"])
            pred = float(f.proy + (_features(fila, fuentes) @ b)[0])
            pc = lambda v: f"{v:+.1f}%".replace(".", ",").replace("-", "−")
            det = []
            if "sepa" in fuentes:
                det.append(f"góndolas de todo el país (SEPA) {pc(f.sepa)} en lo que va del mes")
            if "may" in fuentes:
                det.append(f"{MAYORISTA[clase]} {pc(f['may'])} este mes y {pc(f['may_l1'])} el anterior")
            info.append({"region": f.region, "componente": clase,
                         "fuente": "precios de góndola y mayoristas" if len(fuentes) > 1 else
                                   ("precios de góndola (SEPA)" if fuentes == ["sepa"] else f"mayorista: {MAYORISTA[clase]}"),
                         "valor": pred, "parte": 1.0, "detalle": ("; ".join(det))[:1].upper() + ("; ".join(det))[1:]})
    return info


def informacion_historica(mes: pd.Timestamp, corte: str) -> list[dict]:
    """Ítems con las predicciones fuera de muestra guardadas (para el backtest del modelo completo)."""
    if not RUTA_BT.exists():
        return []
    bt = pd.read_csv(RUTA_BT, dtype={"clase": str, "corte": str}, parse_dates=["mes"])
    bt = bt[(bt.mes == mes) & (bt.corte == corte)]
    return [{"region": f.region, "componente": f.clase, "fuente": f.fuentes, "valor": float(f.pred), "parte": 1.0,
             "detalle": "backtest"} for _, f in bt.iterrows()]
