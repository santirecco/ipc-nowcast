"""ipc_nowcast: herramientas para replicar y anticipar el IPC de INDEC."""
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
DATA = RAIZ / "data"
CONFIG = RAIZ / "config"
REPORTS = RAIZ / "reports"
REGIONES = ["GBA", "Pampeana", "Noreste", "Noroeste", "Cuyo", "Patagonia"]
