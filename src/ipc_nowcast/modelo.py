"""Modelo de nowcast del IPC.

Estructura (de abajo hacia arriba):

1. Proyección estadística de cada celda región x división (72 celdas) y de los grupos/clases publicados:
   promedio de cuatro reglas simples y robustas (elegidas por backtest):
     - persistencia: la variación del mes anterior
     - mediana de los últimos 3 meses
     - núcleo reciente + estacionalidad típica de ese mes (mediana de años anteriores)
     - núcleo reciente + estacionalidad del mismo mes del año pasado
2. Información conocida del mes reemplaza la parte del componente que cubre:
     - calendario de regulados (config/regulados/AAAA-MM.yaml), con arrastre por fecha de vigencia
     - índices propios de supermercados online (GBA; se usan solo si no hay SEPA para esa clase)
     - indicadores adelantados por clase de alimentos (adelantados.py): precios de góndola de todo el país
       (SEPA), verduras y frutas mayoristas (Mercado Central) y hacienda (carne), calibrados con la historia
3. Agregación exacta como INDEC (pesos efectivos calibrados) -> nacional "de abajo hacia arriba".
4. Si ya salió el IPC de la Ciudad (IPCBA) del mismo mes, se combina con él (peso estimado en el backtest).
"""
from __future__ import annotations

import calendar
import os
from datetime import date

import numpy as np
import pandas as pd
import yaml

from . import CONFIG, DATA, REGIONES, canasta, replica

PESO_CABA = 0.7  # valor por defecto si no hay historia suficiente para estimarlo
# El peso del IPC de la Ciudad en la víspera se estima con la historia: el que hubiera minimizado el error en los
# meses anteriores (backtest), entre 0,3 y 0,8. En nov-2026 daba 0,5-0,55 (con 0,7 fijo el error era mayor).
PESOS_CABA_GRILLA = np.round(np.arange(0.3, 0.801, 0.05), 2)
MIN_MESES_PESO_CABA = 12  # un año completo (con 8 o 10 las primeras estimaciones eran inestables)


def estimar_peso_caba(hist: pd.DataFrame) -> float:
    """hist: columnas fin_de_mes, caba_corregido y real de meses ya publicados."""
    h = hist.dropna(subset=["fin_de_mes", "caba_corregido", "real"])
    if len(h) < MIN_MESES_PESO_CABA:
        return PESO_CABA
    err = [float((w * h.caba_corregido + (1 - w) * h.fin_de_mes - h.real).abs().mean()) for w in PESOS_CABA_GRILLA]
    return float(PESOS_CABA_GRILLA[int(np.argmin(err))])


# Víspera por rubro: cada división del GBA se corrige hacia la misma división del IPC de la Ciudad,
# var = modelo + k_div * (ciudad - modelo), con k_div estimado con la historia (grilla 0-1, mínimo 12 meses).
# Fuera de muestra (jul-25 a oct-26) baja el error de la víspera de 0,164 a 0,125 pp frente a mezclar solo el
# nivel general. Si no hay historia suficiente se usa la mezcla del nivel general.
RUTA_CABA_DIV = DATA / "nowcast" / "caba_divisiones.csv"
K_CABA_GRILLA = np.round(np.arange(0, 1.001, 0.05), 2)


def estimar_k_caba(hist: pd.DataFrame) -> dict | None:
    """hist: mes, div, var (modelo a fin de mes, GBA), real_div (INDEC GBA) y caba (IPC Ciudad) de meses publicados."""
    h = hist.dropna(subset=["var", "real_div", "caba"])
    if h.empty or h.mes.nunique() < MIN_MESES_PESO_CABA:
        return None
    k = {}
    for d, g in h.groupby("div"):
        err = [float((g["var"] + x * (g.caba - g["var"]) - g.real_div).abs().mean()) for x in K_CABA_GRILLA]
        k[str(d)] = float(K_CABA_GRILLA[int(np.argmin(err))])
    return k


def k_caba_vigente() -> dict | None:
    try:
        return estimar_k_caba(pd.read_csv(RUTA_CABA_DIV, dtype={"div": str}))
    except Exception:  # noqa: BLE001
        return None


def peso_caba_vigente() -> float:
    """Peso estimado con todo el backtest guardado (para el pronóstico en vivo)."""
    ruta = DATA / "nowcast" / "backtest.csv"
    try:
        b = pd.read_csv(ruta)
        if "caba_corregido" not in b:
            b["caba_corregido"] = b["caba"]
        return estimar_peso_caba(b)
    except Exception:  # noqa: BLE001
        return PESO_CABA
# Corrección estacional de la brecha IPC Ciudad vs. INDEC: solo para meses en que la brecha tuvo el mismo signo
# todos los años anteriores (hoy: enero y julio, cuando turismo y servicios hacen subir más a la Ciudad).
AJUSTE_CABA_UMBRAL = 0.2   # pp: correcciones menores se ignoran
AJUSTE_CABA_FACTOR = 0.75  # se aplica el 75% del desvío típico (prudencia)
PARTE_SUPER = 0.6  # parte de cada clase de alimentos que se toma de los supermercados online (a calibrar)

# Subsidios al gas (04.5): cuando cambian las bonificaciones o los bloques de consumo subsidiado, la factura de los
# hogares con subsidio se mueve distinto de la del cuadro tarifario. Brecha mensual (pp) entre la factura de gas de
# los usuarios con subsidio y la de los usuarios sin subsidio, según los reportes del IIEP-UBA
# (data/precios/regulados/subsidios_gas.csv). Hasta ene-26 se usa la factura (N2/N3 contra N1); desde abr-26 (esquema
# SEF) el reporte da el cargo variable, que es cerca de la mitad de la factura.
# Parte del 04.5 alcanzada = peso del gas en el 04.5 x hogares con subsidio (~50%). Solo en las regiones donde el gas
# es calefacción: en GBA (la factura la domina la luz) y en el norte el 04.5 no respondió a la brecha en 2024-26.
SUBSIDIOS_GAS = os.environ.get("IPC_SUBSIDIOS_GAS", "1") == "1"
PARTE_SUBSIDIO_GAS = {"Pampeana": 0.45 * 0.5, "Cuyo": 0.45 * 0.5, "Patagonia": 0.55 * 0.5}
FACTOR_MEDIDA = {"factura": 1.0, "variable": 0.5}


def brecha_subsidio_gas(mes: pd.Timestamp) -> float | None:
    ruta = DATA / "precios" / "regulados" / "subsidios_gas.csv"
    if not ruta.exists():
        return None
    t = pd.read_csv(ruta)
    f = t[t.mes == f"{mes:%Y-%m}"]
    if f.empty:
        return None
    return float(f.brecha.iloc[0]) * FACTOR_MEDIDA.get(str(f.medida.iloc[0]), 1.0)


# ---------------------------------------------------------------- proyección estadística
DIVISIONES_TRANSABLES = set(__import__("os").environ.get("IPC_TRANSABLES", "03,05").split(",")) - {""}


DIVISIONES_SALTO_MARZO = set(__import__("os").environ.get("IPC_SALTO_MARZO", "10").split(",")) - {""}


def proyeccion_estadistica(var: pd.DataFrame, nucleo: pd.Series, mes: pd.Timestamp) -> pd.Series:
    """Proyección de la variación % de cada columna de `var` para `mes`, con datos hasta el mes anterior."""
    pasado = var[var.index < mes].dropna(how="all")
    nuc = nucleo[nucleo.index < mes].dropna()
    nuc3 = nuc.iloc[-3:].mean()
    persist = pasado.iloc[-1].copy()
    med3 = pasado.iloc[-3:].median()
    # Educación: el salto de marzo (comienzo de clases) no se repite en abril; la persistencia y la mediana de 3
    # meses se miden sin los marzos (2018-26: error de la división 2,60 -> 2,27; abril 5,7 -> 1,9; resto igual)
    cols_m = [c for c in pasado.columns if isinstance(c, tuple) and c[1] in DIVISIONES_SALTO_MARZO]
    if cols_m and mes.month != 3:
        sin_marzo = pasado.loc[[m.month != 3 for m in pasado.index], cols_m]
        persist[cols_m] = sin_marzo.iloc[-1]
        med3[cols_m] = sin_marzo.iloc[-3:].median()
    mismos = [m for m in pasado.index if m.month == mes.month and m.year >= 2017 and m in nuc.index]
    desvios = pd.DataFrame({m: (pasado.loc[m] - nuc.loc[m]) / max(nuc.loc[m], 0.3) for m in mismos}).T
    estac_tipica = nuc3 * (1 + desvios.median())
    # Bienes transables (ropa, equipamiento del hogar): su precio relativo frente a la núcleo cambia de régimen
    # (hasta 2022 subían más que la núcleo; desde 2024, menos). La estacionalidad se mide neta de la tendencia
    # relativa de los 12 meses que terminan en cada mes, y se le suma la tendencia relativa de los últimos 12 meses.
    cols_t = [c for c in pasado.columns if isinstance(c, tuple) and c[1] in DIVISIONES_TRANSABLES]
    if cols_t and len(mismos):
        rel = pasado[cols_t].sub(nuc, axis=0).div(nuc.clip(lower=0.3), axis=0)
        tend = rel.rolling(12, min_periods=10).mean()
        neto = (rel.loc[mismos] - tend.loc[mismos]).median()
        ajustada = nuc3 * (1 + neto + tend.iloc[-1])
        estac_tipica = estac_tipica.copy()
        estac_tipica[cols_t] = ajustada.where(ajustada.notna(), estac_tipica[cols_t])
    estac_ultima = nuc3 * (1 + desvios.iloc[-1]) if len(desvios) else estac_tipica
    reglas = pd.DataFrame({"persist": persist, "med3": med3, "estac": estac_tipica, "estac_ult": estac_ultima})
    return reglas.mean(axis=1)


# ---------------------------------------------------------------- regulados
def impacto_en_mes(variacion: float, vigencia: date, mes: pd.Timestamp) -> float:
    """Parte de un aumento que impacta en la variación mensual (INDEC compara promedios mensuales)."""
    dias = calendar.monthrange(mes.year, mes.month)[1]
    if vigencia.year == mes.year and vigencia.month == mes.month:
        return variacion * (dias - vigencia.day + 1) / dias
    previo = (mes - pd.offsets.MonthBegin(1))
    if vigencia.year == previo.year and vigencia.month == previo.month:  # arrastre del mes anterior
        dias_p = calendar.monthrange(previo.year, previo.month)[1]
        return variacion * (vigencia.day - 1) / dias_p
    return 0.0


def proyeccion_componente(var: pd.DataFrame, mes: pd.Timestamp) -> pd.Series:
    """Proyección robusta para componentes con información propia: mediana de los últimos 6 meses
    (evita arrastrar saltos puntuales, como cambios de régimen tarifario)."""
    return var[var.index < mes].iloc[-6:].median()


# Proyección por componente, elegida con la historia (regla única, anidada): para cada región y componente se
# comparan dos métodos, (a) mediana de los últimos 6 meses y (b) núcleo reciente + desvío típico del componente en
# ese mes del año respecto de la núcleo (temporada). En cada mes se usa (b) solo si en los meses anteriores
# (desde PROY_DESDE, mínimo PROY_MIN_MESES) tuvo menor error por al menos MEJORA_PROY. Así, rubros de temporada
# (frutas, verduras, transporte) dejan de proyectar "lo último" y los estables siguen con la mediana.
# Base contra la que se mide un dato de un componente (dato - base = cuánto cambia la división):
# - COHERENTE (todo): el valor que la proyección de la división supone para el componente (proyección del
#   componente + desvío de la división respecto de la suma de sus componentes). Probado para las señales de precios:
#   empeora (fin de mes últimos 16 meses 0,198 -> 0,233), queda apagado.
COHERENTE = __import__("os").environ.get("IPC_COHERENTE", "0") == "1"
# Probado nov-2026: medir las correcciones estadísticas del día 1 contra la base coherente empeora mucho
# (inicio de mes, últimos 16 meses: 0,240 -> 0,313). Queda apagado.
ESTADISTICAS_COHERENTES = __import__("os").environ.get("IPC_EST_COHERENTES", "1") == "1"
METODO_EST_COHERENTES = __import__("os").environ.get("IPC_EST_METODO", "elegida")
# Datos casi exactos (calendario de tarifas): se miden contra el valor que la proyección de la división supone para
# el componente, armada con medianas de 6 meses. Con el dato que midió INDEC, el error de la división en toda la
# historia (2018-2026) queda: luz y gas 2,29 -> 1,32; transporte 1,76 -> 1,70; prepagas 1,62 -> 1,52.
FUENTES_COHERENTES = {"calendario de regulados"}  # probada también para la regla de prepagas: no alcanza el umbral
PROY_DESDE = pd.Timestamp("2019-01-01")
PROY_MIN_MESES = 24
MEJORA_PROY = 0.02


def proyecciones_serie(s: pd.Series, nucleo: pd.Series) -> pd.DataFrame:
    """Para cada mes: proyección mediana-6, proyección de temporada y la elegida, usando solo meses anteriores."""
    s = s.dropna()
    idx = s.index.union(s.index[-1:] + pd.offsets.MonthBegin(1)) if len(s) else s.index
    if not len(s):
        return pd.DataFrame(columns=["p1", "p2", "real", "p"])
    sv = s.values
    si = s.index
    nuc = nucleo.dropna()
    nv, ni = nuc.values, nuc.index
    nuc_en_s = nuc.reindex(si).values
    dev_all = sv - nuc_en_s  # desvío de cada mes respecto de la núcleo (NaN si falta)
    meses_s = si.month.values
    filas = []
    for m in idx:
        k = si.searchsorted(m)  # meses anteriores: [0, k)
        if k < 6:
            continue
        p1 = float(np.median(sv[k - 6:k]))
        kn = ni.searchsorted(m)
        dv = dev_all[:k]
        sel = (meses_s[:k] == m.month) & ~np.isnan(dv)
        p2 = float(nv[kn - 3:kn].mean() + np.median(dv[sel])) if sel.sum() >= 3 and kn >= 3 else np.nan
        filas.append((m, p1, p2, s.get(m, np.nan)))
    t = pd.DataFrame(filas, columns=["mes", "p1", "p2", "real"]).set_index("mes")
    if t.empty:
        return t
    e1 = (t.p1 - t.real).abs().values
    e2 = (t.p2 - t.real).abs().values
    ok = (t.index >= PROY_DESDE) & ~np.isnan(e1) & ~np.isnan(e2)
    c1 = np.concatenate([[0.0], np.cumsum(np.where(ok, e1, 0.0))])
    c2 = np.concatenate([[0.0], np.cumsum(np.where(ok, e2, 0.0))])
    cn = np.concatenate([[0], np.cumsum(ok)])
    p2v, p1v = t.p2.values, t.p1.values
    elegidas = np.empty(len(t))
    for i in range(len(t)):
        n = cn[i]
        usar2 = n >= PROY_MIN_MESES and not np.isnan(p2v[i]) and c2[i] / n < c1[i] / n - MEJORA_PROY
        elegidas[i] = p2v[i] if usar2 else p1v[i]
    t["p"] = elegidas
    return t


def leer_regulados(mes: pd.Timestamp, previo: bool = False) -> list[dict]:
    """Ítems del calendario del mes (o del mes anterior, si previo=True)."""
    m = mes - pd.offsets.MonthBegin(1) if previo else mes
    ruta = CONFIG / "regulados" / f"{m:%Y-%m}.yaml"
    if not ruta.exists():
        return []
    return yaml.safe_load(ruta.read_text(encoding="utf-8")).get("items", []) or []


# ---------------------------------------------------------------- nowcast
class Nowcast:
    def __init__(self, divisiones: pd.DataFrame, aperturas: pd.DataFrame, ipcba: pd.DataFrame | None = None):
        self.div = divisiones
        self.ap = aperturas
        self.piv = replica.pivotear(divisiones)
        self.pesos = replica.calibrar(self.piv)
        self.base_comp = canasta.calibrar(aperturas)
        self.V = self.piv.pct_change() * 100
        pa = aperturas.pivot_table(index="periodo", columns=["region", "codigo"], values="indice").sort_index()
        self.Vap = pa.pct_change() * 100
        self.nucleo = self.V["Nacional"]["Núcleo"]
        self.ipcba = ipcba
        self._proy = {}
        self._piv_ap = pa
        self._W = {}
        self._resto = None

    def pesos_comp(self, mes) -> pd.DataFrame:
        """Peso efectivo de cada grupo/clase (y de su "resto") dentro de su división, para `mes` (con caché)."""
        if mes not in self._W:
            self._W[mes] = canasta.peso_efectivo_en_division(self.ap, self.base_comp, mes, piv=self._piv_ap)
        return self._W[mes]

    def _var(self, r, code, m):
        if len(code) == 2:
            return self.V[r][code].get(m, np.nan)
        return self.Vap[r][code].get(m, np.nan) if (r, code) in self.Vap.columns else np.nan

    def series_resto(self) -> dict:
        """Variación implícita de cada "resto" (lo que INDEC no publica aparte dentro de un grupo o división):
        variación del padre menos la de los hijos publicados, con los pesos efectivos de cada mes."""
        if self._resto is None:
            filas = {}
            for m in self.Vap.index[1:]:
                ce = self.pesos_comp(m)
                for (r, p), g in ce.groupby(["region", "padre"]):
                    resto = g[g.codigo.str.endswith(".resto")]
                    if resto.empty or resto.peso_en_padre_ef.iloc[0] < 1e-6:
                        continue
                    hijos = g[~g.codigo.str.endswith(".resto")]
                    s = sum(f.peso_en_padre_ef * self._var(r, f.codigo, m) for _, f in hijos.iterrows())
                    filas.setdefault((r, resto.codigo.iloc[0]), {})[m] = (self._var(r, p, m) - s) / resto.peso_en_padre_ef.iloc[0]
            self._resto = {k: pd.Series(v).sort_index().dropna() for k, v in filas.items()}
        return self._resto

    def desvio_division(self, r, d, mes, proy_div, f=None) -> float:
        """Cuánto difiere la proyección de la división de la suma de las proyecciones de sus componentes
        (todos, incluido el resto). Es el valor que la proyección de la división "supone" de más (o de menos) para
        cada componente: un dato de un componente se compara contra su proyección + este desvío, así reemplaza
        exactamente su parte de la división (con todos los componentes cubiertos, la división es la suma de los datos)."""
        ce = self.pesos_comp(mes)
        g = ce[(ce.region == r) & (ce.division == d)]
        if g.empty:
            return 0.0
        hojas = g[~g.codigo.isin(set(g.padre))]
        f = f or self.proy_comp
        bu = 0.0
        for _, h in hojas.iterrows():
            v = f(r, h.codigo, mes)
            if not np.isfinite(v):
                return 0.0
            bu += h.peso_en_division_ef * v
        return float(proy_div - bu / hojas.peso_en_division_ef.sum())

    def proy_div(self, mes) -> pd.Series:
        """Proyección estadística de cada celda región x división para `mes` (con caché)."""
        if not hasattr(self, "_pdiv"):
            self._pdiv = {}
        if mes not in self._pdiv:
            cols = [(r, d) for r in REGIONES for d in replica.DIVISIONES]
            Y = pd.DataFrame({c: self.V[c[0]][c[1]] for c in cols})
            self._pdiv[mes] = proyeccion_estadistica(Y, self.nucleo, mes)
        return self._pdiv[mes]

    def base_comp_mes(self, r: str, c: str, mes: pd.Timestamp) -> float:
        """Punto de partida de un componente: su proyección, corregida (si COHERENTE) por el desvío de la
        división, para que el valor coincida con lo que supone la proyección de la división."""
        return self.base_coherente(r, c, mes) if COHERENTE else self.proy_comp(r, c, mes)

    def proy_p1(self, r: str, c: str, mes: pd.Timestamp) -> float:
        """Mediana de los últimos 6 meses del componente (también para los "resto")."""
        self.proy_comp(r, c, mes)
        t = self._proy[(r, c)]
        if mes in t.index:
            return float(t.p1.loc[mes])
        return np.nan if c.endswith(".resto") else float(proyeccion_componente(self.Vap[r][[c]], mes).iloc[0])

    def base_coherente(self, r: str, c: str, mes: pd.Timestamp, metodo: str = "elegida") -> float:
        f = self.proy_p1 if metodo == "p1" else self.proy_comp
        p = f(r, c, mes)
        if c in replica.DIVISIONES or (self.V.index < mes).sum() < 13:
            return p
        return p + self.desvio_division(r, c[:2], mes, float(self.proy_div(mes)[(r, c[:2])]), f)

    def proy_comp(self, r: str, c: str, mes: pd.Timestamp) -> float:
        """Proyección estadística del componente c en la región r para `mes` (método elegido con la historia)."""
        if (r, c) not in self._proy:
            serie = self.series_resto().get((r, c), pd.Series(dtype=float)) if c.endswith(".resto") else self.Vap[r][c]
            self._proy[(r, c)] = proyecciones_serie(serie, self.nucleo)
        t = self._proy[(r, c)]
        if mes in t.index:
            return float(t.p.loc[mes])
        if c.endswith(".resto"):
            return np.nan
        return float(proyeccion_componente(self.Vap[r][[c]], mes).iloc[0])

    # pesos efectivos para un mes (pueden ser futuros: se usan los niveles del último mes publicado)
    def _pesos_mes(self, mes):
        s, w = self.pesos["region_en_nacional"], self.pesos["division_en_region"]
        ant = self.piv.index[self.piv.index < mes].max()
        niv_nac = sum(s[r] * self.piv[r]["00"].loc[ant] for r in REGIONES)
        filas = {}
        for r in REGIONES:
            reg = s[r] * self.piv[r]["00"].loc[ant] / niv_nac
            for d in replica.DIVISIONES:
                filas[(r, d)] = reg * w.loc[d, r] * self.piv[r][d].loc[ant] / self.piv[r]["00"].loc[ant]
        return pd.Series(filas)

    def informacion_del_mes(self, mes, usar_regulados=True, usar_super=True, super_mensual=None, extra=None,
                            usar_reglas=True) -> list[dict]:
        """Lista de datos conocidos del mes que reemplazan parte de un componente:
        {region, componente, fuente, valor (var %), parte (0-1 del componente que cubre)}."""
        info = []
        if usar_regulados:
            # arrastre: aumentos que entraron después del día 1 del mes anterior suman la parte que faltaba
            for it in leer_regulados(mes, previo=True):
                arr = impacto_en_mes(it["variacion"], pd.Timestamp(it["vigencia"]).date(), mes)
                if arr > 0:
                    for r in it["regiones"]:
                        info.append({"region": r, "componente": it["componente"], "fuente": "arrastre del mes anterior",
                                     "valor": arr, "parte": it["parte"], "aditivo": True, "detalle": it["nombre"]})
            items = leer_regulados(mes)
            claves = {(r, it["componente"]) for it in items for r in it["regiones"]}
            for r, c in sorted(claves):
                its = [it for it in items if it["componente"] == c and r in it["regiones"]]
                parte = min(1.0, sum(it["parte"] for it in its))
                imp = sum(it["parte"] * impacto_en_mes(it["variacion"], pd.Timestamp(it["vigencia"]).date(), mes) for it in its)
                info.append({"region": r, "componente": c, "fuente": "calendario de regulados",
                             "valor": imp / parte if parte else 0.0, "parte": parte,
                             "detalle": "; ".join(it["nombre"] for it in its)})
        extra = list(extra or [])
        # Un mismo componente no se cuenta dos veces: si el calendario anuncia una parte p del componente, la otra
        # señal (precios relevados o regla) cubre solo el resto (1 - p). Si la otra señal mide el precio efectivo
        # (no es estadística), ya incluye el arrastre del mes anterior: ese arrastre no se suma aparte.
        parte_cal = {}
        for it in info:
            if not it.get("aditivo"):
                k = (it["region"], it["componente"])
                parte_cal[k] = min(1.0, parte_cal.get(k, 0.0) + it["parte"])
        medidos = {(it["region"], it["componente"]) for it in extra if not it.get("estadistica")}
        info = [it for it in info if not (it.get("aditivo") and (it["region"], it["componente"]) in medidos)]
        ajustados = []
        for it in extra:
            p = parte_cal.get((it["region"], it["componente"]), 0.0)
            if p >= 1.0:
                continue
            ajustados.append({**it, "parte": it["parte"] * (1 - p)} if p > 0 else it)
        extra = [{**it, "senal": it.get("senal", True)} for it in ajustados]
        cubiertos = {(it["region"], it["componente"]) for it in extra}
        info += extra
        # Reglas conocidas de antemano: las prepagas ajustan por el IPC de dos meses antes (backtest 2025-26: error
        # medio 0,2 pp contra 0,7 pp de la estadística). Solo si el calendario del mes no trae el dato.
        ya = {(it["region"], it["componente"]) for it in info}
        m2 = mes - pd.offsets.MonthBegin(2)
        ipc = self.V["Nacional"]["00"]
        if usar_reglas and m2 in ipc.index and pd.notna(ipc.loc[m2]):
            for r in REGIONES:
                if (r, "06.4.1") not in ya:
                    info.append({"region": r, "componente": "06.4.1", "fuente": "regla: IPC de dos meses antes",
                                 "valor": float(ipc.loc[m2]), "parte": 1.0,
                                 "detalle": f"Las prepagas ajustan por la inflación de dos meses antes ({ipc.loc[m2]:.1f}%)".replace(".", ",")})
        brecha = brecha_subsidio_gas(mes) if (usar_reglas and SUBSIDIOS_GAS) else None
        if brecha:
            for r, parte in PARTE_SUBSIDIO_GAS.items():
                info.append({"region": r, "componente": "04.5", "fuente": "regla: subsidios al gas",
                             "valor": brecha, "parte": parte, "aditivo": True,
                             "detalle": f"Factura de gas de los hogares con subsidio {brecha:+.1f} pp respecto de la de los "
                                        f"hogares sin subsidio (bonificaciones y bloques de consumo)".replace(".", ",")})
        if usar_super and super_mensual is not None and not super_mensual.empty:
            sm = super_mensual[(super_mensual.mes == mes) & super_mensual["var_mensual_%"].notna()]
            for _, f in sm.iterrows():
                if f.clase in ("05.6", "06.1", "12.1", "02.1") or ("GBA", f.clase) in cubiertos:
                    continue  # solo alimentos y bebidas no alcohólicas, y solo si SEPA no cubre la clase
                info.append({"region": "GBA", "componente": f.clase, "fuente": "supermercados online",
                             "valor": float(f["var_mensual_%"]), "parte": PARTE_SUPER, "detalle": f"{int(f.dias)} días"})
        return info

    def celdas(self, mes, usar_regulados=True, usar_super=True, super_mensual=None, extra=None, usar_reglas=True):
        """Variación proyectada de cada celda región x división, con la información del mes incorporada."""
        cols = [(r, d) for r in REGIONES for d in replica.DIVISIONES]
        Y = pd.DataFrame({c: self.V[c[0]][c[1]] for c in cols})
        base = proyeccion_estadistica(Y, self.nucleo, mes)
        info = self.informacion_del_mes(mes, usar_regulados, usar_super, super_mensual, extra, usar_reglas)
        if not info:
            return base, []
        comp_ef = self.pesos_comp(mes)
        ajustada = base.copy()
        desvio = {}
        aplicados = []
        for it in info:
            r, c = it["region"], it["componente"]
            if (r, c) not in self.Vap.columns and not (c.endswith(".resto") and (r, c) in self.series_resto()):
                continue
            if c in replica.DIVISIONES:  # el ítem cubre una división entera (ej. "10" Educación)
                base_c, w_div = float(base[(r, c)]), 1.0
            else:
                # base de la diferencia: la proyección elegida del componente. Se probó medirla contra la mediana
                # de 6 meses (más coherente con la proyección de la división en teoría): empeora mucho el backtest
                # honesto (fin de mes últimos 16: 0,204 -> 0,301), así que queda la elegida.
                if COHERENTE and it.get("fuente") not in FUENTES_COHERENTES:
                    base_c = self.base_coherente(r, c, mes)
                elif ESTADISTICAS_COHERENTES and it.get("estadistica"):
                    base_c = self.base_coherente(r, c, mes, metodo=METODO_EST_COHERENTES)
                elif it.get("fuente") in FUENTES_COHERENTES:
                    base_c = self.base_coherente(r, c, mes, metodo="p1")
                elif it.get("senal"):
                    base_c = self.proy_comp(r, c, mes)
                else:
                    base_c = float(proyeccion_componente(self.Vap[r][[c]], mes).iloc[0])
                fila = comp_ef[(comp_ef.region == r) & (comp_ef.codigo == c)]
                if fila.empty:
                    continue
                w_div = float(fila.peso_en_division_ef.iloc[0])
            if it.get("aditivo"):
                nuevo = base_c + it["parte"] * it["valor"]
            else:
                nuevo = it["parte"] * it["valor"] + (1 - it["parte"]) * base_c
            d = c[:2]
            ajustada[(r, d)] += w_div * (nuevo - base_c)
            aplicados.append({**it, "division": d, "proyeccion_estadistica": base_c, "con_informacion": nuevo,
                              "peso_en_division": w_div, "efecto_en_division_pp": w_div * (nuevo - base_c)})
        return ajustada, aplicados

    def ajuste_caba(self, mes) -> float:
        """Desvío típico INDEC - IPC Ciudad para este mes del año, si fue sistemático (mismo signo todos los años)."""
        if self.ipcba is None:
            return 0.0
        c = self.ipcba["00"].pct_change() * 100
        c.index = c.index.to_period("M").to_timestamp()
        real = self.V["Nacional"]["00"]
        brecha = (real - c).dropna()
        pasado = brecha[(brecha.index < mes) & (brecha.index.month == mes.month)]
        if len(pasado) < 3:
            return 0.0
        nivel = lambda m: max(self.nucleo[self.nucleo.index < m].iloc[-3:].mean(), 0.3)
        rel = np.array([pasado[m] / nivel(m) for m in pasado.index])
        if not (np.all(rel > 0) or np.all(rel < 0)):
            return 0.0
        g = float(np.median(rel) * nivel(mes) * AJUSTE_CABA_FACTOR)
        return g if abs(g) >= AJUSTE_CABA_UMBRAL else 0.0

    def caba_divisiones(self, mes) -> pd.Series:
        """Variación % de cada división del IPC de la Ciudad en `mes` (vacía si no se publicó)."""
        if self.ipcba is None:
            return pd.Series(dtype=float)
        v = self.ipcba.pct_change() * 100
        v.index = v.index.to_period("M").to_timestamp()
        if mes not in v.index:
            return pd.Series(dtype=float)
        return v.loc[mes].dropna()

    def calcular(self, mes, usar_regulados=True, usar_caba=True, usar_super=True, super_mensual=None, extra=None, usar_reglas=True,
                 peso_caba=None, k_caba="vigente"):
        celdas, aplicados = self.celdas(mes, usar_regulados, usar_super, super_mensual, extra, usar_reglas)
        w = self._pesos_mes(mes)
        w = w / w.sum() * 100
        abajo_arriba = float((celdas * w).sum() / 100)
        caba = None
        if usar_caba and self.ipcba is not None:
            v = self.ipcba["00"].pct_change() * 100
            v.index = v.index.to_period("M").to_timestamp()
            if mes in v.index and not np.isnan(v.loc[mes]):
                caba = float(v.loc[mes])
        ajuste = self.ajuste_caba(mes) if caba is not None else 0.0
        if k_caba == "vigente":
            if not hasattr(self, "_k_caba"):
                self._k_caba = k_caba_vigente()
            k_caba = self._k_caba
        if caba is not None and k_caba:
            # víspera por rubro: el GBA se corrige con cada división de la Ciudad
            cd = self.caba_divisiones(mes)
            celdas = celdas.copy()
            for (r, dv) in celdas.index:
                if r == "GBA" and dv in cd.index and k_caba.get(dv, 0) > 0:
                    celdas[(r, dv)] += k_caba[dv] * (cd[dv] - celdas[(r, dv)])
            final = float((celdas * w).sum() / 100)
            peso_caba = None
        else:
            if peso_caba is None:
                if not hasattr(self, "_peso_caba"):
                    self._peso_caba = peso_caba_vigente()
                peso_caba = self._peso_caba
            final = peso_caba * (caba + ajuste) + (1 - peso_caba) * abajo_arriba if caba is not None else abajo_arriba
        aporte = (celdas * w / 100).rename("incidencia_pp")
        return {
            "mes": mes, "estimacion": final, "abajo_arriba": abajo_arriba, "caba": caba, "ajuste_caba": ajuste,
            "peso_caba": peso_caba if caba is not None else None,
            "celdas": pd.DataFrame({"variacion": celdas, "peso_%": w, "incidencia_pp": aporte}),
            "informacion": pd.DataFrame(aplicados),
        }


def backtest(nc: Nowcast, desde="2024-07-01") -> pd.DataFrame:
    """Simula el modelo mes a mes con la información que había en cada momento (sin calendario de regulados,
    que no tiene historia). Los indicadores adelantados entran con sus predicciones fuera de muestra."""
    from . import adelantados
    real = nc.V["Nacional"]["00"]
    filas, filas_div, celdas_fin = [], [], {}
    for mes in real.index[real.index >= pd.Timestamp(desde)]:
        e15 = adelantados.informacion_historica(mes, "15")
        e22 = adelantados.informacion_historica(mes, "22")
        ec = adelantados.informacion_historica(mes, "completo")
        e0 = adelantados.informacion_historica(mes, "15", solo_estadistica=True)
        r0 = nc.calcular(mes, usar_regulados=False, usar_caba=False, extra=e0)
        r15 = nc.calcular(mes, usar_regulados=False, usar_caba=False, extra=e15)
        r22 = nc.calcular(mes, usar_regulados=False, usar_caba=False, extra=e22)
        rc = nc.calcular(mes, usar_regulados=False, usar_caba=False, extra=ec)
        r1 = nc.calcular(mes, usar_regulados=False, usar_caba=True, extra=ec, peso_caba=0.0, k_caba=None)
        cd = nc.caba_divisiones(mes)
        for (r, dv), f in rc["celdas"].iterrows():
            if r == "GBA":
                filas_div.append({"mes": mes, "div": dv, "var": f["variacion"], "peso": f["peso_%"],
                                  "real_div": nc.V["GBA"][dv].get(mes, np.nan), "caba": cd.get(dv, np.nan)})
        celdas_fin[mes] = rc["celdas"]
        filas.append({"mes": mes, "real": real.loc[mes], "inicio_de_mes": r0["estimacion"],
                      "mitad_de_mes": r15["estimacion"], "dia_22": r22["estimacion"], "fin_de_mes": rc["estimacion"],
                      "caba": r1["caba"], "caba_corregido": (r1["caba"] + r1["ajuste_caba"]) if r1["caba"] is not None else np.nan,
                      "clases_con_datos": len(ec)})
    df = pd.DataFrame(filas).set_index("mes")
    hist = pd.DataFrame(filas_div)
    RUTA_CABA_DIV.parent.mkdir(parents=True, exist_ok=True)
    hist.to_csv(RUTA_CABA_DIV, index=False, float_format="%.4f")
    # víspera fuera de muestra: con cada mes se usa solo lo aprendido de los meses anteriores. Si ya hay 12 meses,
    # corrección por rubro del GBA; si no, mezcla del nivel general con el peso estimado (o el de por defecto)
    pesos, visp, metodo = [], [], []
    for i, (mes, f) in enumerate(df.iterrows()):
        k = estimar_k_caba(hist[hist.mes < mes])
        w = estimar_peso_caba(df.iloc[:i])
        if pd.isna(f.caba_corregido):
            pesos.append(w); visp.append(f.fin_de_mes); metodo.append("")
        elif k:
            c = celdas_fin[mes]
            cd = hist[hist.mes == mes].set_index("div").caba
            var = c["variacion"].copy()
            for (r, dv) in var.index:
                if r == "GBA" and pd.notna(cd.get(dv, np.nan)):
                    var[(r, dv)] += k.get(dv, 0) * (cd[dv] - var[(r, dv)])
            pesos.append(np.nan); visp.append(float((var * c["peso_%"]).sum() / c["peso_%"].sum())); metodo.append("por rubro")
        else:
            pesos.append(w); visp.append(w * f.caba_corregido + (1 - w) * f.fin_de_mes); metodo.append("nivel general")
    df["peso_caba"] = pesos
    df["vispera_con_caba"] = visp
    df["metodo_caba"] = metodo
    return df
