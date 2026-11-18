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
     - índices propios de supermercados (cuando hay dos meses de datos)
3. Agregación exacta como INDEC (pesos efectivos calibrados) -> nacional "de abajo hacia arriba".
4. Si ya salió el IPC de la Ciudad (IPCBA) del mismo mes, se combina con él (peso estimado en el backtest).
"""
from __future__ import annotations

import calendar
from datetime import date

import numpy as np
import pandas as pd
import yaml

from . import CONFIG, REGIONES, canasta, replica

PESO_CABA = 0.7  # surge del backtest 2025-2026 (ver reports/backtest.md)
# Corrección estacional de la brecha IPC Ciudad vs. INDEC: solo para meses en que la brecha tuvo el mismo signo
# todos los años anteriores (hoy: enero y julio, cuando turismo y servicios hacen subir más a la Ciudad).
AJUSTE_CABA_UMBRAL = 0.2   # pp: correcciones menores se ignoran
AJUSTE_CABA_FACTOR = 0.75  # se aplica el 75% del desvío típico (prudencia)
PARTE_SUPER = 0.6  # parte de cada clase de alimentos que se toma de los supermercados online (a calibrar)


# ---------------------------------------------------------------- proyección estadística
def proyeccion_estadistica(var: pd.DataFrame, nucleo: pd.Series, mes: pd.Timestamp) -> pd.Series:
    """Proyección de la variación % de cada columna de `var` para `mes`, con datos hasta el mes anterior."""
    pasado = var[var.index < mes].dropna(how="all")
    nuc = nucleo[nucleo.index < mes].dropna()
    nuc3 = nuc.iloc[-3:].mean()
    persist = pasado.iloc[-1]
    med3 = pasado.iloc[-3:].median()
    mismos = [m for m in pasado.index if m.month == mes.month and m.year >= 2017 and m in nuc.index]
    desvios = pd.DataFrame({m: (pasado.loc[m] - nuc.loc[m]) / max(nuc.loc[m], 0.3) for m in mismos}).T
    estac_tipica = nuc3 * (1 + desvios.median())
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

    def informacion_del_mes(self, mes, usar_regulados=True, usar_super=True, super_mensual=None) -> list[dict]:
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
        if usar_super and super_mensual is not None and not super_mensual.empty:
            sm = super_mensual[(super_mensual.mes == mes) & super_mensual["var_mensual_%"].notna()]
            for _, f in sm.iterrows():
                if f.clase in ("05.6", "06.1", "12.1", "02.1"):
                    continue  # por ahora solo alimentos y bebidas no alcohólicas
                info.append({"region": "GBA", "componente": f.clase, "fuente": "supermercados online",
                             "valor": float(f["var_mensual_%"]), "parte": PARTE_SUPER, "detalle": f"{int(f.dias)} días"})
        return info

    def celdas(self, mes, usar_regulados=True, usar_super=True, super_mensual=None):
        """Variación proyectada de cada celda región x división, con la información del mes incorporada."""
        cols = [(r, d) for r in REGIONES for d in replica.DIVISIONES]
        Y = pd.DataFrame({c: self.V[c[0]][c[1]] for c in cols})
        base = proyeccion_estadistica(Y, self.nucleo, mes)
        info = self.informacion_del_mes(mes, usar_regulados, usar_super, super_mensual)
        if not info:
            return base, []
        comp_ef = canasta.peso_efectivo_en_division(self.ap, self.base_comp, mes)
        ajustada = base.copy()
        aplicados = []
        for it in info:
            r, c = it["region"], it["componente"]
            if (r, c) not in self.Vap.columns:
                continue
            base_c = float(proyeccion_componente(self.Vap[r][[c]], mes).iloc[0])
            fila = comp_ef[(comp_ef.region == r) & (comp_ef.codigo == c)]
            if fila.empty:
                continue
            if it.get("aditivo"):
                nuevo = base_c + it["parte"] * it["valor"]
            else:
                nuevo = it["parte"] * it["valor"] + (1 - it["parte"]) * base_c
            w_div = float(fila.peso_en_division_ef.iloc[0])
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

    def calcular(self, mes, usar_regulados=True, usar_caba=True, usar_super=True, super_mensual=None):
        celdas, aplicados = self.celdas(mes, usar_regulados, usar_super, super_mensual)
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
        final = PESO_CABA * (caba + ajuste) + (1 - PESO_CABA) * abajo_arriba if caba is not None else abajo_arriba
        aporte = (celdas * w / 100).rename("incidencia_pp")
        return {
            "mes": mes, "estimacion": final, "abajo_arriba": abajo_arriba, "caba": caba, "ajuste_caba": ajuste,
            "celdas": pd.DataFrame({"variacion": celdas, "peso_%": w, "incidencia_pp": aporte}),
            "informacion": pd.DataFrame(aplicados),
        }


def backtest(nc: Nowcast, desde="2024-07-01") -> pd.DataFrame:
    """Simula el modelo mes a mes con la información que había en cada momento (sin calendario de regulados)."""
    real = nc.V["Nacional"]["00"]
    filas = []
    for mes in real.index[real.index >= pd.Timestamp(desde)]:
        r0 = nc.calcular(mes, usar_regulados=False, usar_caba=False)
        r1 = nc.calcular(mes, usar_regulados=False, usar_caba=True)
        filas.append({"mes": mes, "real": real.loc[mes], "inicio_de_mes": r0["estimacion"],
                      "caba": r1["caba"], "vispera_con_caba": r1["estimacion"]})
    return pd.DataFrame(filas).set_index("mes")
