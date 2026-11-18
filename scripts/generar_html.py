"""Genera reports/tablero_ipc.html: el tablero en un único archivo HTML, con datos y gráficos adentro.

Se abre con doble clic, sin conexión. Es una foto del día en que se generó.
"""
import csv
import json
import re
import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
T = RAIZ / "tablero"
DATOS = RAIZ / "data" / "tablero"
ARCHIVOS = ["pronostico", "divisiones", "regiones", "informacion", "backtest", "recoleccion", "fuentes"]


def leer_csv(nombre):
    ruta = DATOS / f"{nombre}.csv"
    if not ruta.exists():
        return []
    with ruta.open(encoding="utf-8") as f:
        return [{k: (v if v != "" else None) for k, v in fila.items()} for fila in csv.DictReader(f)]


def main():
    html = (T / "index.html").read_text(encoding="utf-8")
    cuerpo = re.sub(r'<meta name="dash-one-writer">\n?|<link rel="stylesheet" href="style.css">\n?|<script src="[^"]+"></script>\n?', "", html)
    datos = {n: leer_csv(n) for n in ARCHIVOS}
    # cada archivo va en su propio ámbito, como en el tablero
    js = "\n".join("(function () {\n" + (T / f).read_text(encoding="utf-8") + "\n})();" for f in ["calcs.js", "ui.js", "charts.js"])
    salida = f"""<!DOCTYPE html>
<html lang="es-AR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Pronóstico IPC INDEC · {date.today():%d/%m/%Y}</title>
<style>
{(T / "tokens.css").read_text(encoding="utf-8")}
{(T / "style.css").read_text(encoding="utf-8")}
</style>
</head>
<body>
<div id="dash-root">
{cuerpo}
</div>
<script>{(T / "vendor" / "d3.min.js").read_text(encoding="utf-8")}</script>
<script>window.IPX_DATOS = {json.dumps(datos, ensure_ascii=False)};</script>
<script>{(T / "shim.js").read_text(encoding="utf-8")}</script>
<script>
{js}
</script>
</body>
</html>
"""
    destino = RAIZ / "reports" / "tablero_ipc.html"
    destino.write_text(salida, encoding="utf-8")
    print(f"{destino} ({len(salida) / 1024:.0f} KB)")


if __name__ == "__main__":
    sys.exit(main())
