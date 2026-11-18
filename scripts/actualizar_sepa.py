"""Baja los días de SEPA que falten y recalcula los índices por región y clase.

Uso:
  python scripts/actualizar_sepa.py                    # mes en curso y anterior (uso diario)
  python scripts/actualizar_sepa.py 2024-08 2026-11    # rango de meses (reconstrucción del histórico)
  python scripts/actualizar_sepa.py --solo-indices     # no baja nada, solo recalcula con lo que hay

Salidas:
  data/cache/sepa/AAAA-MM-DD.parquet        (no se sube al repo)
  data/precios/sepa/indices_mensuales.csv   (variación por mes, región y clase; corte 15 y mes completo)
  data/precios/sepa/indices_diarios.csv     (mes en curso: variación acumulada con los días hasta cada fecha)
"""
import os
import sys
from concurrent.futures import ProcessPoolExecutor
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pandas as pd  # noqa: E402

from ipc_nowcast import sepa  # noqa: E402

TRABAJADORES = int(os.environ.get("SEPA_TRABAJADORES", "2"))


def _bajar(args):
    fecha, link = args
    return fecha, sepa.bajar_dia(fecha, link)


def meses_entre(a: str, b: str) -> list[str]:
    return [str(p) for p in pd.period_range(a, b, freq="M")]


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    solo_indices = "--solo-indices" in sys.argv
    hoy = pd.Timestamp(date.today())
    if len(args) == 2:
        meses = meses_entre(args[0], args[1])
    else:
        meses = meses_entre(str((hoy - pd.offsets.MonthBegin(2)).to_period("M")), str(hoy.to_period("M")))
    if len(args) != 2 and "--sin-limpiar" not in sys.argv:
        # uso diario: el caché guarda solo el mes en curso y los dos anteriores
        for p in sepa.CACHE.glob("????-??-??.parquet"):
            if p.stem[:7] < meses[0]:
                p.unlink()
    if not solo_indices:
        indice = sepa.indice_archivo()
        hechos = set(sepa.dias_en_cache())
        pendientes = [(f, indice[f]) for f in sorted(indice) if f[:7] in meses and f not in hechos]
        # --cada N: para reprocesar historia más rápido, un día de cada N (el índice usa el promedio del mes)
        cada = next((int(a.split("=")[1]) for a in sys.argv if a.startswith("--cada=")), 1)
        if cada > 1:
            pendientes = [p for p in pendientes if pd.Timestamp(p[0]).dayofyear % cada == 0]
        print(f"{len(pendientes)} días para bajar", flush=True)
        with ProcessPoolExecutor(TRABAJADORES) as ex:
            for f, estado in ex.map(_bajar, pendientes):
                print(f, estado, flush=True)

    # índices mensuales: cortes día 15 y día 22, y mes completo, para cada mes con datos del mes anterior
    sepa.SALIDA.mkdir(parents=True, exist_ok=True)
    ruta = sepa.SALIDA / "indices_mensuales.csv"
    previo = pd.read_csv(ruta, dtype={"clase": str}) if ruta.exists() else pd.DataFrame()
    nuevos = []
    for m in meses:
        for corte in (15, 22, None):
            for fn in (sepa.indices_del_mes, sepa.indices_carne_fresca):
                v = fn(m, corte=corte)
                if not v.empty:
                    v.insert(1, "corte", str(corte) if corte else "completo")
                    nuevos.append(v)
    if nuevos:
        nuevos = pd.concat(nuevos)
        if not previo.empty:
            previo = previo[~previo.mes.isin(nuevos.mes.unique())]
        todo = pd.concat([previo, nuevos]).sort_values(["mes", "corte", "region", "clase"])
        todo.to_csv(ruta, index=False, float_format="%.4f")
        print(f"índices: {len(todo)} filas, meses {todo.mes.min()} a {todo.mes.max()}")

    rec = sepa.recoleccion()
    if not rec.empty:
        rec.to_csv(sepa.SALIDA / "recoleccion.csv", index=False)

    # seguimiento diario del mes en curso: variación con los días hasta cada fecha
    mes = max(sepa.dias_en_cache())[:7] if sepa.dias_en_cache() else None
    if mes:
        dias = sorted(d for d in sepa.dias_en_cache() if d.startswith(mes))
        filas = []
        for d in dias:
            v = sepa.indices_del_mes(mes, corte=int(d[-2:]))
            if not v.empty:
                v.insert(1, "fecha", d)
                filas.append(v)
        if filas:
            pd.concat(filas).to_csv(sepa.SALIDA / "indices_diarios.csv", index=False, float_format="%.4f")


if __name__ == "__main__":
    main()
