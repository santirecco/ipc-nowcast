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
        i["nombre_componente"] = i.componente.map(COMPONENTES).fillna(i.componente)
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
    print("Tablero:", sorted(p.name for p in OUT.glob("*.csv")))


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
