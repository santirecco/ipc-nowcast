"""Actualiza combustibles (precios de YPF en surtidor) y dólar mayorista (BCRA)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ipc_nowcast import indicadores  # noqa: E402


def main():
    try:
        t = indicadores.actualizar_combustibles()
        print("Combustibles:", len(t), "filas; último mes", int(t.anio.max()), int(t[t.anio == t.anio.max()].mes.max()))
    except Exception as e:  # noqa: BLE001
        print("Combustibles: error", e)
    try:
        d = indicadores.actualizar_dolar()
        print("Dólar mayorista:", len(d), "días; último", d.fecha.max())
    except Exception as e:  # noqa: BLE001
        print("Dólar: error", e)


if __name__ == "__main__":
    main()
