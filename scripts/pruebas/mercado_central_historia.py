"""Recupera la historia 2017-2022 del Mercado Central desde el archivo de Internet (web.archive.org) y la suma
a data/precios/mayoristas/mercado_central.csv. Se corre una sola vez."""
import io, sys, zipfile, subprocess
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
import pandas as pd
from ipc_nowcast import mayoristas as M

BASE = "https://web.archive.org/web/2022id_/http://www.mercadocentral.gob.ar/sites/default/files/precios_mayoristas/"
ARCH = [f"PM-{t}-{a}.zip" for t in ("Frutas", "Hortalizas") for a in (2017, 2018)] + \
       ["PM-Frutas-2019_0.zip", "PM-Hortalizas-2019.zip", "PM-Frutas-2020_0.zip", "PM-Hortalizas-2020_0.zip",
        "PM-Frutas-2021.zip", "PM-Hortalizas-2021.zip"] + \
       [f"PM-{t}-{m}-2022{s}.zip" for t, m, s in [("Frutas", "Enero", "_0"), ("Frutas", "Febrero", ""), ("Frutas", "Marzo", "_0"),
                                                  ("Frutas", "Abril", ""), ("Hortalizas", "Enero", "_0"), ("Hortalizas", "Febrero", ""),
                                                  ("Hortalizas", "Marzo", ""), ("Hortalizas", "Abril", "")]]
EXTRA = ["https://web.archive.org/web/2022id_/http://mercadocentral.gob.ar/sites/default/files/precios_mayoristas/PM-Frutas-Mayo-2022%20-_0.zip",
         "https://web.archive.org/web/2022id_/http://mercadocentral.gob.ar/sites/default/files/precios_mayoristas/PM-Hortalizas-Mayo-2022.zip",
         "https://web.archive.org/web/2022id_/http://mercadocentral.gob.ar/sites/default/files/precios_mayoristas/PM-Hortalizas-junio-2022_0.zip"]


def recorrer(z, tipo, out):
    for n in z.namelist():
        b = z.read(n)
        if n.lower().endswith(".zip"):
            try:
                recorrer(zipfile.ZipFile(io.BytesIO(b)), tipo, out)
            except zipfile.BadZipFile:
                pass
        else:
            d = M._parsear_dia(b, n.rsplit("/", 1)[-1], tipo)
            if not d.empty:
                out.append(d)


out = []
for u in [BASE + a for a in ARCH] + EXTRA:
    tipo = "frutas" if "Frutas" in u else "hortalizas"
    b = subprocess.run(["curl", "-sSL", "--retry", "3", "--max-time", "300", u], capture_output=True).stdout
    try:
        n0 = len(out); recorrer(zipfile.ZipFile(io.BytesIO(b)), tipo, out); print(u.rsplit("/", 1)[-1], len(out) - n0, "días", flush=True)
    except zipfile.BadZipFile:
        print(u.rsplit("/", 1)[-1], "no se pudo leer", flush=True)
ruta = M.DIR / "mercado_central.csv"
previo = pd.read_csv(ruta)
todo = pd.concat([pd.concat(out)] + [previo], ignore_index=True).drop_duplicates(["fecha", "tipo", "especie"], keep="last")
todo.sort_values(["fecha", "tipo", "especie"]).to_csv(ruta, index=False, float_format="%.2f")
print("filas", len(todo), "desde", todo.fecha.min())
