"""Prueba fuentes candidatas contra el error del índice nacional (fuera de muestra), sin tocar la calibración.

Uso: python scripts/pruebas/evaluar_candidatas.py 04.1.1:icl 04.1.1:icl+ipc ...
Para cada candidata: error de la clase (proyección vs. con fuente) y efecto en el error nacional en inicio, mitad
y fin de mes, en todo el período, por mitades y en los últimos 16 meses.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
import numpy as np
import pandas as pd
from ipc_nowcast import modelo, adelantados as A

DESDE = pd.Timestamp(sys.argv[sys.argv.index("--desde") + 1]) if "--desde" in sys.argv else pd.Timestamp("2024-07-01")
cand = [(c.split(":")[0], c.split(":")[1].split("+")) for c in sys.argv[1:] if ":" in c]
d = pd.read_parquet("data/processed/indec_divisiones.parquet"); a = pd.read_parquet("data/processed/indec_aperturas.parquet")
nc = modelo.Nowcast(d, a, None); real = nc.V["Nacional"]["00"]
meses = [m for m in real.index if m >= DESDE]
clases = sorted({c for c, _ in cand})
A.CLASES = clases
A.OPCIONES = {c: [f for cc, f in cand if cc == c] for c in clases}


def resumen(e):
    e = e.abs(); n = len(e) // 2
    return f"todo {e.mean():.4f} | 1ra mitad {e.iloc[:n].mean():.4f} | 2da mitad {e.iloc[n:].mean():.4f} | últ.16 {e.iloc[-16:].mean():.4f}"


for corte, momento in [("15", "inicio"), ("15", "mitad"), ("completo", "fin")]:
    t = A.tabla(nc, corte)
    preds = {}
    for c in clases:
        for o in A.evaluar_clase(t, c):
            preds[(c, o["fuentes"])] = o
    base_items = {m: A.informacion_historica(m, corte, solo_estadistica=(momento == "inicio")) for m in meses}
    b = pd.Series({m: nc.calcular(m, usar_regulados=False, usar_caba=False, extra=base_items[m])["estimacion"] for m in meses})
    print(f"\n== {momento} ==  base: {resumen(b - real[meses])}")
    for (c, f), o in preds.items():
        est = set(f.split("+")) <= A.ESTADISTICAS
        if momento == "inicio" and not est:
            continue
        oos = o["oos"]
        v = {}
        for m in meses:
            x = oos[oos.mes == m]
            it = [{"region": r.region, "componente": c, "fuente": f, "valor": float(r.pred), "parte": 1.0, "estadistica": est} for _, r in x.iterrows()]
            v[m] = nc.calcular(m, usar_regulados=False, usar_caba=False, extra=[i for i in base_items[m] if i["componente"] != c] + it)["estimacion"] if it else b[m]
        v = pd.Series(v)
        print(f"  {c}:{f}  clase {o['error_proyeccion']:.2f}->{o['error_con_fuente']:.2f} ({o['meses']} m) | nacional {resumen(v - real[meses])}")
