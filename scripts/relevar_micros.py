"""Relevamiento diario de pasajes de micro de larga distancia (parte del 07.3 Transporte público de INDEC, que hoy el
modelo no mide). Fuente: páginas de ruta de Central de Pasajes, que publican el pasaje más barato y el precio
promedio de cada ruta desde Retiro. Se guarda una foto por día para evaluarlo cuando junte historia.
Salida: data/precios/servicios/micros_diario.csv (fecha, destino, mas_barato, promedio)."""
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
SALIDA = RAIZ / "data" / "precios" / "servicios" / "micros_diario.csv"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"
DESTINOS = ["cordoba", "rosario", "mar-del-plata", "mendoza", "tucuman", "salta", "bariloche", "neuquen", "bahia-blanca",
            "santa-fe", "parana", "corrientes", "posadas", "resistencia", "san-juan", "santiago-del-estero",
            "san-salvador-de-jujuy", "villa-carlos-paz", "puerto-madryn", "comodoro-rivadavia", "san-luis", "la-rioja",
            "catamarca", "necochea", "villa-gesell", "pinamar", "tandil", "puerto-iguazu", "rio-cuarto", "santa-rosa"]
NUM = r"\$\s?([\d.]+)"


def pagina(destino):
    url = f"https://www.centraldepasajes.com.ar/cdp/pasajes-micro/retiro-buenos-aires/{destino}/?DIda=1&CntPas=1"
    r = subprocess.run(["curl", "-sSL", "--compressed", "--max-time", "45", "--retry", "2", "-A", UA, url], capture_output=True)
    return r.stdout.decode("utf-8", "ignore")


def valor(texto, etiqueta):
    m = re.search(etiqueta + r"\s*(?:<[^>]+>\s*)*" + NUM, texto)
    return float(m.group(1).replace(".", "")) if m else None


def main():
    hoy = (datetime.now(timezone.utc) - timedelta(hours=3)).date().isoformat()
    filas = []
    for d in DESTINOS:
        t = re.sub(r"&#225;", "á", pagina(d))
        barato, prom = valor(t, r"Pasaje más barato"), valor(t, r"Precio promedio de pasajes")
        if barato or prom:
            filas.append({"fecha": hoy, "destino": d, "mas_barato": barato, "promedio": prom})
    print(f"micros: {len(filas)} de {len(DESTINOS)} rutas con precio")
    if not filas:
        sys.exit(1)
    nuevo = pd.DataFrame(filas)
    if SALIDA.exists():
        viejo = pd.read_csv(SALIDA)
        nuevo = pd.concat([viejo[viejo.fecha != hoy], nuevo], ignore_index=True)
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    nuevo.sort_values(["fecha", "destino"]).to_csv(SALIDA, index=False)


if __name__ == "__main__":
    main()
