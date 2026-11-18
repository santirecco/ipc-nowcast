"""Actualiza precios mayoristas: Mercado Central (verduras y frutas) y hacienda (Mercado Agroganadero).

Uso:  python scripts/actualizar_mayoristas.py           (mes en curso y anterior)
      python scripts/actualizar_mayoristas.py --todo    (todo lo publicado: Mercado Central 2026, hacienda desde 2017)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ipc_nowcast import mayoristas  # noqa: E402


def main():
    todo = "--todo" in sys.argv
    try:
        mc = mayoristas.actualizar_mercado_central(todos=todo)
        print("Mercado Central:", len(mc), "filas, último día", mc.fecha.max())
    except Exception as e:  # noqa: BLE001
        print("Mercado Central: error", e)
    try:
        h = mayoristas.actualizar_hacienda("2017-01" if todo else None)
        print("Hacienda:", h.mes.nunique(), "meses, hasta", h.hasta.max())
    except Exception as e:  # noqa: BLE001
        print("Hacienda: error", e)


if __name__ == "__main__":
    main()
