"""Paso 1: baja las series oficiales del IPC de INDEC y las deja limpias en data/processed/.

Uso:  python scripts/actualizar_indec.py            (descarga y procesa)
      python scripts/actualizar_indec.py --sin-descarga   (solo procesa lo que ya está en data/raw)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ipc_nowcast import DATA, indec  # noqa: E402


def main():
    if "--sin-descarga" not in sys.argv:
        indec.descargar()
    salida = DATA / "processed"
    salida.mkdir(parents=True, exist_ok=True)
    for clave in indec.ARCHIVOS:
        df = indec.leer(clave)
        df.to_parquet(salida / f"indec_{clave}.parquet", index=False)
        print(f"{clave}: {len(df):,} filas, {df.periodo.min():%Y-%m} a {df.periodo.max():%Y-%m}")


if __name__ == "__main__":
    main()
