"""Prepara los archivos que lee el tablero (data/tablero/*.csv), con nombres de columna simples."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pandas as pd  # noqa: E402

from ipc_nowcast import DATA  # noqa: E402

NC = DATA / "nowcast"
OUT = DATA / "tablero"
COMPONENTES = {"04.5": "Electricidad, gas y otros combustibles", "06.4.1": "Prepagas", "07.3": "Transporte público",
               "07.2.2": "Combustibles", "02.2": "Tabaco", "08.3": "Telefonía e internet", "10": "Educación",
               "01.1.1": "Pan y cereales", "01.1.2": "Carnes", "01.1.4": "Lácteos y huevos", "01.1.5": "Aceites y grasas",
               "01.1.6": "Frutas", "01.1.7": "Verduras", "01.1.8": "Azúcar, dulces y golosinas",
               "01.2.1": "Café, té y yerba", "01.2.2": "Aguas, gaseosas y jugos", "01.1.resto": "Otros alimentos",
               "07.1": "Compra de vehículos", "03.1": "Ropa", "05": "Equipamiento del hogar"}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    h = pd.read_csv(NC / "historial.csv")
    if "ajuste_caba" not in h.columns:
        h["ajuste_caba"] = 0.0
    if "momento" not in h.columns:
        h["momento"] = None
    h.rename(columns={"solo_modelo_estadistico": "solo_modelo"})[
        ["fecha_calculo", "mes", "estimacion", "rango_bajo", "rango_alto", "solo_modelo", "ipc_caba", "ajuste_caba", "rem", "dias_supermercados",
         "momento"]
    ].round(3).to_csv(OUT / "pronostico.csv", index=False)

    d = pd.read_csv(NC / "ultimo_divisiones.csv", dtype={"division": str})
    if "cobertura" not in d:
        d["cobertura"] = 0.0
    d.rename(columns={"variacion_%": "variacion", "peso_%": "peso", "incidencia_pp": "incidencia"})[
        ["division", "nombre", "variacion", "peso", "incidencia", "cobertura"]].round(3).to_csv(OUT / "divisiones.csv", index=False)

    r = pd.read_csv(NC / "ultimo_regiones.csv")
    r.rename(columns={"variacion_%": "variacion", "peso_%": "peso", "incidencia_pp": "incidencia"})[
        ["region", "variacion", "peso", "incidencia"]].round(3).to_csv(OUT / "regiones.csv", index=False)

    ruta = NC / "ultimo_informacion.csv"
    if ruta.exists():
        i = pd.read_csv(ruta, dtype={"componente": str})
        from ipc_nowcast.adelantados import NOMBRES
        i["nombre_componente"] = i.componente.map(COMPONENTES).fillna(i.componente.map(NOMBRES)).fillna(i.componente)
        def grupo(c, f):
            if c.startswith("01"):
                return "Alimentos: precios reales del mes"
            if f in ("calendario de regulados", "arrastre del mes anterior") or f.startswith("regla"):
                return "Tarifas, aumentos anunciados y reglas de ajuste"
            return "Combustibles y otros precios del mes"
        i["grupo"] = [grupo(c, f) for c, f in zip(i.componente, i.fuente)]
        i["clave"] = i.region + " · " + i.nombre_componente + " · " + i.fuente
        if "efecto_nacional_pp" not in i:
            i["efecto_nacional_pp"], i["peso_celda_%"] = 0.0, 0.0
        i.rename(columns={"valor": "dato", "proyeccion_estadistica": "proyeccion", "efecto_en_division_pp": "efecto_pp",
                          "efecto_nacional_pp": "efecto_nacional", "peso_celda_%": "peso", "con_informacion": "con"})[
            ["clave", "grupo", "region", "componente", "nombre_componente", "fuente", "detalle", "dato", "proyeccion", "con",
             "efecto_pp", "efecto_nacional", "peso"]
        ].round(4).to_csv(OUT / "informacion.csv", index=False)

    b = pd.read_csv(NC / "backtest.csv", parse_dates=["mes"])
    b["mes"] = b.mes.dt.strftime("%Y-%m")
    b.rename(columns={"real": "indec", "caba": "ipc_caba", "vispera_con_caba": "vispera"}).round(3).to_csv(OUT / "backtest.csv", index=False)

    s = pd.read_csv(DATA / "precios" / "supermercados" / "resumen.csv")[["fecha", "cadena", "productos"]]
    s["fuente"] = "Supermercados online"
    filas = [s]
    sd = DATA / "precios" / "sepa" / "recoleccion.csv"
    if sd.exists():
        filas.append(pd.read_csv(sd).assign(fuente="SEPA (todo el país)"))
    mc = DATA / "precios" / "mayoristas" / "mercado_central.csv"
    if mc.exists():
        m = pd.read_csv(mc)
        m = m[m.fecha >= s.fecha.min()].groupby("fecha").size().rename("productos").reset_index()
        filas.append(m.assign(cadena="Mercado Central", fuente="Mayoristas"))
    pd.concat(filas)[["fecha", "fuente", "cadena", "productos"]].sort_values(["fecha", "fuente", "cadena"]).to_csv(
        OUT / "recoleccion.csv", index=False)
    estado_fuentes().to_csv(OUT / "fuentes.csv", index=False)
    exportar_json()
    print("Tablero:", sorted(p.name for p in OUT.glob("*.csv")))


def exportar_json():
    """data/publico/ipc_predictor.json: un único archivo chico con todo lo que muestra el tablero, para que otros
    tableros (p. ej. Argenfunds, solapa Macro) lo lean directo de GitHub sin tocar el modelo."""
    import json
    from datetime import datetime, timezone
    import numpy as np

    def limpio(df):
        df = df.replace({np.nan: None})
        return df.to_dict("records")
    pr = pd.read_csv(OUT / "pronostico.csv")
    ult = pr.iloc[-1].to_dict()
    hraw = pd.read_csv(NC / "historial.csv")
    pura = hraw.iloc[-1].get("proyeccion_pura") if "proyeccion_pura" in hraw else None
    hist_mes = pr[pr.mes == ult["mes"]][["fecha_calculo", "estimacion", "rango_bajo", "rango_alto", "solo_modelo", "momento"]]
    div = pd.read_csv(OUT / "divisiones.csv", dtype={"division": str})
    reg = pd.read_csv(OUT / "regiones.csv")
    bt = pd.read_csv(OUT / "backtest.csv")
    errores = []
    for desde, nombre in [("2024-07", "Desde jul-2024"), ("2025-01", "2025-2026"), ("2025-07", "Últimos 16 meses")]:
        x = bt[bt.mes >= desde]
        fila = {"periodo": nombre, "meses": int(len(x))}
        for col in ["inicio_de_mes", "mitad_de_mes", "dia_22", "fin_de_mes", "vispera"]:
            e = (x[col] - x.indec).abs()
            fila[col] = round(float(e.mean()), 3)
        errores.append(fila)
    info = pd.read_csv(OUT / "informacion.csv", dtype={"componente": str}) if (OUT / "informacion.csv").exists() else pd.DataFrame()
    grupos, top = [], []
    if not info.empty:
        g = info.groupby("grupo").agg(efecto=("efecto_nacional", "sum"), datos=("clave", "size")).reset_index()
        grupos = limpio(g.round(4))
        t = info.groupby(["nombre_componente", "fuente"]).agg(efecto=("efecto_nacional", "sum"), dato=("dato", "median"),
                                                               regiones=("region", "nunique")).reset_index()
        t = t.reindex(t.efecto.abs().sort_values(ascending=False).index).head(10)
        top = limpio(t.round(4))
    indec = pd.read_parquet(DATA / "processed" / "indec_divisiones.parquet")
    nac = indec[(indec.region == "Nacional") & (indec.codigo.isin(["00", "Núcleo"]))]
    nac = nac.pivot_table(index="periodo", columns="codigo", values="indice").sort_index()
    v = (nac / nac.shift(1) - 1) * 100
    ia = (nac / nac.shift(12) - 1) * 100
    serie = pd.DataFrame({"mes": v.index.strftime("%Y-%m"), "mensual": v["00"].values, "nucleo": v["Núcleo"].values,
                          "interanual": ia["00"].values}).dropna().tail(25)
    cob = float((div.peso * div.cobertura).sum() / div.peso.sum()) if len(div) else None
    # precisión por momento (últimos 16 meses): error medio, error cuadrático y % de meses dentro de ±0,25 pp
    precision = []
    x16 = bt.tail(16)
    for col in ["inicio_de_mes", "mitad_de_mes", "dia_22", "fin_de_mes", "vispera"]:
        e = (x16[col] - x16.indec).dropna()
        precision.append({"momento": col, "mae": round(float(e.abs().mean()), 3), "rmse": round(float(np.sqrt((e ** 2).mean())), 3),
                          "dentro_025": round(float((e.abs() <= 0.25).mean()), 3), "sesgo": round(float(e.mean()), 3)})
    # puente: de la proyección con la historia al pronóstico
    puente = []
    if pura is not None and pd.notna(pura):
        puente.append({"paso": "Proyección con la historia", "valor": round(float(pura), 3), "tipo": "base"})
        puente.append({"paso": "Correcciones conocidas el día 1", "valor": round(float(ult["solo_modelo"] - pura), 3), "tipo": "delta"})
        acum = float(ult["solo_modelo"])
        for g in grupos:
            puente.append({"paso": g["grupo"], "valor": round(float(g["efecto"]), 3), "tipo": "delta"})
            acum += float(g["efecto"])
        resto = float(ult["estimacion"]) - acum
        if abs(resto) >= 0.005:
            puente.append({"paso": "Interacciones y ajustes", "valor": round(resto, 3), "tipo": "delta"})
        puente.append({"paso": "Pronóstico", "valor": round(float(ult["estimacion"]), 3), "tipo": "total"})
    relevamiento = relevamiento_fuentes()
    celdas = []
    rc = NC / "ultimo_celdas.csv"
    if rc.exists():
        cc = pd.read_csv(rc, dtype={"division": str})
        cc["division"] = cc.division.str.zfill(2)
        celdas = limpio(cc.rename(columns={"peso_%": "peso"}).round(3))
    out = {
        "version": 1, "generado": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "pronostico": {k: (None if pd.isna(v) else v) for k, v in ult.items()}, "cobertura": round(cob, 3) if cob is not None else None,
        "historial_mes": limpio(hist_mes), "historial": limpio(pr[["fecha_calculo", "mes", "estimacion", "rango_bajo", "rango_alto"]]),
        "divisiones": limpio(div), "regiones": limpio(reg), "informacion_grupos": grupos, "informacion_top": top,
        "indec": limpio(serie.round(3)), "backtest": limpio(bt[["mes", "indec", "inicio_de_mes", "mitad_de_mes", "dia_22", "fin_de_mes", "vispera"]]),
        "errores": errores, "fuentes": limpio(pd.read_csv(OUT / "fuentes.csv")),
        "precision": precision, "puente": puente, "celdas": celdas, "relevamiento": relevamiento["fuentes"], "relevamiento_total": {k: v for k, v in relevamiento.items() if k != "fuentes"},
    }
    inf = NC / "informe_ultimo.json"
    if inf.exists():
        out["informe"] = json.loads(inf.read_text(encoding="utf-8"))
    dest = DATA.parent / "publico"
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "ipc_predictor.json").write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")


def relevamiento_fuentes() -> list:
    """De dónde salen los precios que releva el predictor: qué mide cada fuente, para qué rubros, cada cuánto y
    cuánto junta (con el último día de recolección)."""
    P = DATA / "precios"
    est = pd.read_csv(OUT / "fuentes.csv").set_index("fuente") if (OUT / "fuentes.csv").exists() else pd.DataFrame()

    def estado(nombre):
        if nombre in est.index:
            return str(est.loc[nombre, "estado"]), str(est.loc[nombre, "ultimo_dato"])
        return "", ""
    r = pd.read_csv(OUT / "recoleccion.csv") if (OUT / "recoleccion.csv").exists() else pd.DataFrame(columns=["fecha", "fuente", "cadena", "productos"])
    def ult(fuente):
        x = r[r.fuente == fuente]
        if x.empty:
            return 0, 0, []
        x = x[x.fecha == x.fecha.max()]
        return int(x.cadena.nunique()), int(x.productos.sum()), sorted(x.cadena.astype(str).unique())
    sc, sp, _ = ult("SEPA (todo el país)")
    oc, op, onl = ult("Supermercados online")
    _, mp, _ = ult("Mayoristas")
    try:
        t = pd.read_csv(P / "tiendas" / "resumen.csv")
        t = t[t.fecha >= sorted(t.fecha.unique())[-min(3, t.fecha.nunique())]].groupby("cadena").productos.max()
        tc, tp = int(len(t)), int(t.sum())
    except Exception:  # noqa: BLE001
        tc, tp = 0, 0
    f = lambda n: f"{n:,}".replace(",", ".")  # noqa: E731
    filas = [
        {"fuente": "SEPA · Precios Claros", "origen": "Secretaría de Comercio (datos abiertos)", "tipo": "precios",
         "que": "Precios de góndola que las cadenas de supermercados informan por ley, sucursal por sucursal, en todo el país.",
         "rubros": "Alimentos, bebidas, limpieza, medicamentos y cuidado personal",
         "alcance": f"{sc} cadenas · {f(sp)} precios por día · 6 regiones", "frecuencia": "diaria", "clave": "SEPA (Precios Claros)"},
        {"fuente": "Supermercados online", "origen": "Tiendas web de " + ", ".join(c.capitalize() for c in onl) if onl else "Tiendas web de supermercados",
         "tipo": "precios", "que": "Precios publicados con stock en las tiendas online del GBA.",
         "rubros": "Alimentos y bebidas (GBA)", "alcance": f"{oc} cadenas · {f(op)} productos por día", "frecuencia": "diaria", "clave": "Supermercados online"},
        {"fuente": "Mercado Central de Buenos Aires", "origen": "Precios mayoristas publicados por el Mercado Central", "tipo": "mayorista",
         "que": "Precio mayorista de frutas y verduras: se anticipa a lo que pasa en la verdulería.",
         "rubros": "Frutas y verduras", "alcance": f"{f(mp)} productos por día", "frecuencia": "diaria (días hábiles)", "clave": "Mercado Central"},
        {"fuente": "Hacienda · Mercado Agroganadero de Cañuelas", "origen": "Mercado Agroganadero (ex Liniers)", "tipo": "mayorista",
         "que": "Precio del ganado por categoría. Las subas pasan a la carnicería; las bajas casi no.",
         "rubros": "Carnes", "alcance": "precio promedio y cabezas vendidas", "frecuencia": "diaria", "clave": "Hacienda (Cañuelas)"},
        {"fuente": "Surtidores YPF", "origen": "surtidores.com.ar (precios de YPF en la Ciudad)", "tipo": "precios",
         "que": "Precio de nafta súper, premium y gasoil. Desde nov-2026 se guarda una foto diaria para armar el promedio del mes.",
         "rubros": "Combustibles", "alcance": "3 productos · foto diaria", "frecuencia": "diaria", "clave": "Combustibles (YPF)"},
        {"fuente": "Tarifas y aumentos anunciados", "origen": "ENRE, ENARGAS, Boletín Oficial, gobiernos y prensa", "tipo": "regulados",
         "que": "Aumentos de luz, gas, transporte y prepagas ya publicados, con su fecha de vigencia. Se revisa todos los lunes.",
         "rubros": "Vivienda, transporte y salud", "alcance": "calendario mensual por región", "frecuencia": "semanal", "clave": "Calendario de tarifas"},
        {"fuente": "Listas de autos 0 km", "origen": "Listas de precios de las automotrices", "tipo": "precios",
         "que": "Aumento promedio de las listas del mes, que se conoce a principio de mes.",
         "rubros": "Compra de vehículos", "alcance": "aumento promedio del mes", "frecuencia": "mensual", "clave": ""},
        {"fuente": "Tiendas de ropa, calzado, electro y hogar", "origen": "Equus, Port Said, Tascani, Levi's, Legacy, Mimo, Topper, Naldo, Cetrogar, Coppel, Pardo, Easy y Blaisten",
         "tipo": "evaluacion", "que": "Se relevan desde nov-2026; entran al modelo cuando junten historia y pasen la regla (bajar el error de su rubro).",
         "rubros": "Ropa, calzado, electro y hogar", "alcance": f"{tc} tiendas · {f(tp)} productos", "frecuencia": "diaria", "clave": "Tiendas de ropa y electrónica"},
        {"fuente": "IPC de la Ciudad de Buenos Aires", "origen": "Instituto de Estadística de la Ciudad (IDECBA)", "tipo": "estadistica",
         "que": "Sale días antes que INDEC: en la víspera ajusta el pronóstico del GBA rubro por rubro.",
         "rubros": "Todos (GBA)", "alcance": "12 divisiones", "frecuencia": "mensual", "clave": "IPC Ciudad de Buenos Aires"},
        {"fuente": "INDEC", "origen": "Instituto Nacional de Estadística y Censos", "tipo": "estadistica",
         "que": "El IPC oficial y sus pesos, los precios promedio de 59 productos y el índice de salarios.",
         "rubros": "Todos", "alcance": "12 divisiones × 6 regiones", "frecuencia": "mensual", "clave": "INDEC"},
        {"fuente": "BCRA", "origen": "Banco Central de la República Argentina", "tipo": "estadistica",
         "que": "Dólar mayorista (A3500), índice de contratos de alquiler y el REM, la expectativa de los analistas.",
         "rubros": "Referencias y pruebas", "alcance": "series diarias y mensuales", "frecuencia": "diaria", "clave": "Dólar mayorista (BCRA)"},
    ]
    for x in filas:
        x["estado"], x["ultimo_dato"] = estado(x.pop("clave"))
        if x["fuente"].startswith("Tarifas"):
            x["ultimo_dato"] = ""  # el calendario llega hasta el mes próximo: la fecha confunde
    return {"fuentes": filas, "precios_por_dia": sp + op + tp + mp, "cadenas": sc + oc + tc}


def estado_fuentes() -> pd.DataFrame:
    """Último dato de cada fuente y si está al día (para detectar a simple vista si algo dejó de actualizarse)."""
    import yaml
    from datetime import date
    from ipc_nowcast import CONFIG
    hoy = pd.Timestamp(date.today())
    P = DATA / "precios"
    filas = []

    def agregar(nombre, que, ultimo, tolerancia_dias, frecuencia):
        if ultimo is None or pd.isna(ultimo):
            filas.append({"fuente": nombre, "que_aporta": que, "ultimo_dato": "", "frecuencia": frecuencia, "estado": "sin datos"})
            return
        u = pd.Timestamp(ultimo)
        filas.append({"fuente": nombre, "que_aporta": que, "ultimo_dato": u.strftime("%Y-%m-%d"), "frecuencia": frecuencia,
                      "estado": "al día" if (hoy - u).days <= tolerancia_dias else "atrasada"})

    def leer(ruta, col, **kw):
        try:
            return pd.read_csv(ruta, **kw)[col].max()
        except Exception:  # noqa: BLE001
            return None
    try:
        ult = pd.read_parquet(DATA / "processed" / "indec_divisiones.parquet").periodo.max()
        agregar("INDEC", "Dato oficial y pesos de la canasta", pd.Timestamp(ult) + pd.offsets.MonthEnd(0), 50, "mensual (día ~12)")
    except Exception:  # noqa: BLE001
        agregar("INDEC", "Dato oficial y pesos de la canasta", None, 50, "mensual")
    try:
        ip = pd.read_csv(DATA / "raw" / "caba" / "ipcba.csv")
        ult = pd.to_datetime(ip.iloc[:, 0]).max() + pd.offsets.MonthEnd(0)
    except Exception:  # noqa: BLE001
        ult = None
    agregar("IPC Ciudad de Buenos Aires", "Anticipo del dato nacional (víspera)", ult, 50, "mensual")
    agregar("SEPA (Precios Claros)", "Precios de góndola de ~17 cadenas, todo el país", leer(P / "sepa" / "recoleccion.csv", "fecha"), 3, "diaria")
    agregar("Supermercados online", "Precios del GBA con stock", leer(P / "supermercados" / "resumen.csv", "fecha"), 3, "diaria")
    agregar("Tiendas de ropa y electrónica", "Se juntan desde nov-2026; se prueban cuando haya historia",
            leer(P / "tiendas" / "resumen.csv", "fecha"), 3, "diaria")
    agregar("Mercado Central", "Verduras y frutas mayoristas", leer(P / "mayoristas" / "mercado_central.csv", "fecha"), 5, "diaria (días hábiles)")
    agregar("Hacienda (Cañuelas)", "Precio del ganado: anticipa la carne", leer(P / "mayoristas" / "hacienda.csv", "hasta"), 5, "diaria")
    agregar("Combustibles (YPF)", "Precio en surtidor", leer(P / "combustibles" / "ypf_caba_diario.csv", "fecha"), 3, "diaria")
    agregar("Dólar mayorista (BCRA)", "Se prueba como señal; hoy no se usa", leer(P / "cambio" / "a3500.csv", "fecha"), 5, "diaria")
    try:
        rem = (yaml.safe_load((CONFIG / "externos.yaml").read_text(encoding="utf-8")) or {}).get("rem", {})
        meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
        fechas = []
        for v in rem.values():
            p = str(v.get("relevamiento", "")).split()
            if len(p) >= 2 and p[0] in meses and p[1].isdigit():
                fechas.append(pd.Timestamp(int(p[1]), meses.index(p[0]) + 1, 1) + pd.offsets.MonthEnd(0))
        agregar("REM del BCRA", "Expectativa de los analistas (relevamiento mensual)", max(fechas) if fechas else None, 45, "mensual")
    except Exception:  # noqa: BLE001
        agregar("REM del BCRA", "Expectativa de los analistas", None, 120, "mensual")
    regs = sorted((CONFIG / "regulados").glob("????-??.yaml"))
    agregar("Calendario de tarifas", "Aumentos anunciados (revisión automática los lunes)",
            pd.Timestamp(regs[-1].stem + "-01") + pd.offsets.MonthEnd(0) if regs else None, 45, "semanal")
    return pd.DataFrame(filas)


if __name__ == "__main__":
    main()
