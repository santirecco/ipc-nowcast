# ipc-nowcast

Predictor del IPC de INDEC: replica exactamente cómo INDEC arma el índice y, con precios que se
juntan todos los días (supermercados, tarifas, combustibles, etc.), anticipa el dato del mes antes de que se publique.

## Estado

| Fase | Qué es | Estado |
|---|---|---|
| 0 | Infraestructura (este repo + tareas automáticas) | ✅ |
| 1 | Réplica exacta de INDEC y pesos efectivos mes a mes | ✅ ver [`reports/replica_indec.md`](reports/replica_indec.md) |
| 2 | Mapa de la canasta: pesos de grupos y clases por región; clasificación de productos de supermercado | ✅ |
| 3 | Alimentos: SEPA/Precios Claros (todo el país, historia desde sep-2024), Mercado Central, hacienda, supermercados online | ✅ calibrado contra INDEC: ver [`reports/adelantados.md`](reports/adelantados.md) |
| 4 | Regulados: calendario mensual en `config/regulados/` (luz, gas, transporte, prepagas, combustibles, telefonía, colegios) | ✅ revisión automática semanal (lunes) |
| 5 | Núcleo no alimentario: electro, indumentaria, alquileres, servicios | ⏳ |
| 6 | Motor: proyección estadística, arrastre, información del mes, IPC CABA | ✅ ver [`reports/nowcast.md`](reports/nowcast.md) |
| 7 | Backtest y prueba en paralelo | ✅ backtest en [`reports/backtest.md`](reports/backtest.md); prueba en paralelo desde noviembre 2026 |

## Cómo está organizado

```
config/        Ponderaciones (las publicadas por INDEC y las calibradas por el modelo)
data/raw/      Datos tal como se bajan de cada fuente (no se tocan)
data/processed Datos limpios y resultados intermedios
src/           El código del modelo (paquete ipc_nowcast)
scripts/       Los pasos que se corren, en orden
reports/       Informes legibles que genera el modelo
tablero/       Página del tablero (lee los CSV de data/tablero/)
tests/         Controles automáticos (por ejemplo: que la réplica de INDEC siga siendo exacta)
.github/       Tareas automáticas que corre GitHub (descargas diarias/mensuales)
```

## Pasos que se corren

```bash
pip install -r requirements.txt
python scripts/actualizar_indec.py   # 1. baja las series oficiales de INDEC
python scripts/replicar_indec.py     # 2. replica el índice y calcula pesos efectivos
python scripts/scrapear_supermercados.py  # 3. precios del día de 5 supermercados online
python scripts/actualizar_sepa.py         # 4. SEPA: precios de góndola de las cadenas grandes de todo el país
python scripts/actualizar_mayoristas.py   # 5. Mercado Central (verduras y frutas) y hacienda (carne)
python scripts/actualizar_ipcba.py        # 6. IPC de la Ciudad de Buenos Aires
python scripts/calibrar_adelantados.py    # 7. cuánto anticipa cada fuente a cada clase de alimentos
python scripts/backtest.py                # 8. error histórico del modelo
python scripts/nowcast.py                 # 9. pronóstico del mes en curso
pytest                               # controles
```

Las tareas de `.github/workflows/` hacen esto solas y guardan los resultados en el repo.

## Tablero descargable

`reports/tablero_ipc.html` es el tablero completo en un solo archivo (datos y gráficos adentro).
Se regenera todos los días: en GitHub, abrilo y tocá el botón de descarga ("Download raw file").

## Fuentes de precios

| Fuente | Qué cubre | Cómo se obtiene | Historia |
|---|---|---|---|
| SEPA – Precios Claros | ~17 cadenas grandes (Día, Carrefour, Coto, ChangoMás, Cencosud, La Anónima, Cooperativa Obrera, Toledo, Farmacity…), ~3.000 sucursales en las 24 provincias | Archivo diario del proyecto abierto [preciazo](https://github.com/catdevnull/preciazo) (el sitio oficial bloquea servidores) | desde ago-2024 (faltan abr–jun 2026) |
| Mercado Central de Buenos Aires | Precio mayorista diario de ~100 especies de verduras y frutas | Planillas diarias publicadas en mercadocentral.gob.ar | desde ene-2026 |
| Mercado Agroganadero (Cañuelas) | Precio de la hacienda por categoría | Consulta pública por rango de fechas | desde 2017 |
| Combustibles (surtidores.com.ar) | Precio mensual de nafta súper, premium y gasoil de YPF en CABA | Tabla publicada en surtidores.com.ar (el dataset oficial de Energía está caído) | desde 2018 (se usa desde 2024) |
| Dólar mayorista (BCRA) | Tipo de cambio de referencia A 3500 | API pública del BCRA | desde 2017 (probado: hoy no mejora el pronóstico) |
| Supermercados online | ~60.000 productos con stock en Carrefour, Jumbo, Disco, Vea y Día (GBA) | API pública de las tiendas (VTEX) | desde 18-nov-2026 |
| IPC Ciudad de Buenos Aires | Anticipo del dato nacional | API de series de datos.gob.ar | desde 2012 |
| REM del BCRA | Mediana de los analistas para la inflación mensual (solo referencia) | Planilla mensual publicada por el BCRA | se baja sola cada día |

Los precios de SEPA procesados por día se guardan en el caché de GitHub Actions (`data/cache/sepa/`, no se suben
al repo); al repo van solo los índices por mes, región y clase (`data/precios/sepa/`).

## Tareas manuales

Ninguna. El calendario de regulados lo revisa una tarea programada todos los lunes (busca aumentos
anunciados y actualiza `config/regulados/`); conviene mirar sus cambios de vez en cuando. El tablero muestra el
estado de cada fuente (`data/tablero/fuentes.csv`): si alguna figura como "atrasada", dejó de publicar o cambió su sitio.

## Conceptos clave

- **Peso base**: cuánto pesa cada rubro en la canasta de INDEC (ENGHo 2004/05, llevada a dic-2016).
- **Peso efectivo**: el que pondera la variación de cada mes. Cambia con los precios relativos: si un rubro sube más que el
  resto, pesa más el mes siguiente.
- **Arrastre**: INDEC compara promedios mensuales de precios. Un aumento a mitad de mes impacta una parte ese mes y el
  resto el siguiente.
- **Prueba fuera de muestra**: para decidir si una fuente sirve, cada mes del pasado se predice usando solo lo que
  se sabía antes de ese mes. Así el error medido es el que se hubiera tenido de verdad.
