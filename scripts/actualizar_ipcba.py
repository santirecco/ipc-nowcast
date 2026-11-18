"""Baja el IPC de la Ciudad de Buenos Aires (IPCBA) por división desde la API de series de datos.gob.ar."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ipc_nowcast import fuentes  # noqa: E402

if __name__ == "__main__":
    df = fuentes.actualizar_ipcba()
    print(f"IPCBA hasta {df.index.max():%Y-%m}")
