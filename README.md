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
| 5 | Núcleo no alimentario: electro, indumentaria, alquileres, servicios | 🟡 medicamentos (SEPA) y reglas para restaurantes y papelería; ropa y electrónica se relevan desde nov-2026 y se evalúan cuando haya historia; alquileres (ICL) probado y descartado |
| 6 | Motor: proyección estadística, arrastre, información del mes (cortes día 15, día 22 y mes completo), IPC CABA por rubro | ✅ ver [`reports/nowcast.md`](reports/nowcast.md) |
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
| Tiendas de ropa, calzado, electrónica y hogar | ~73.000 productos con stock de 13 tiendas online (Equus, Port Said, Tascani, Levi's, Legacy, Mimo, Topper, Naldo, Cetrogar, Coppel, Pardo) y hogar y materiales (Easy, Blaisten) | API pública de las tiendas (VTEX) | desde 18-nov-2026 (se evalúan cuando haya historia: electrónica en ~6 meses, ropa en ~1 año por la estacionalidad) |
| IPC Ciudad de Buenos Aires | Anticipo del dato nacional | API de series de datos.gob.ar | desde 2012 |
| REM del BCRA | Mediana de los analistas para la inflación mensual (solo referencia) | Planilla mensual publicada por el BCRA | se baja sola cada día |

Los precios de SEPA procesados por día se guardan en el caché de GitHub Actions (`data/cache/sepa/`, no se suben
al repo); al repo van solo los índices por mes, región y clase (`data/precios/sepa/`).

## Tareas manuales

Ninguna. El calendario de regulados lo revisa una tarea programada todos los lunes (busca aumentos
anunciados y actualiza `config/regulados/`); conviene mirar sus cambios de vez en cuando. El tablero muestra el
estado de cada fuente (`data/tablero/fuentes.csv`): si alguna figura como "atrasada", dejó de publicar o cambió su sitio.

## Regla para sumar fuentes

Una fuente o un cambio de método entra solo si baja el error del índice nacional fuera de muestra (cada mes del
pasado se predice con lo que se sabía antes), mirando todo el período y no solo los meses recientes.
`scripts/pruebas/evaluar_candidatas.py` prueba cualquier fuente candidata con ese criterio. Probadas y descartadas
(nov-2026): ICL para alquileres, historia 2020-2022 del Mercado Central, combinar con el REM, corregir el sesgo
reciente, SEPA para bebidas alcohólicas, limpieza y cuidado personal, el IPC de la Ciudad por rubro para regiones
fuera del GBA, y señales de SEPA armadas solo con los productos que mide INDEC (precios promedio publicados).
Incorporadas en nov-2026: IPC de la Ciudad por rubro (víspera), corte del día 22, arrastre de frutas y listas de
autos 0 km (inicio de mes, `data/precios/autos/listas_0km.csv`, la actualiza la tarea de los lunes), frutas y
verduras frescas de SEPA sin envasados, y proyección de temporada por componente: en cada región y componente se
elige, solo con meses anteriores, entre la mediana de 6 meses y "núcleo + desvío típico de ese mes del año"
(verduras, frutas y transporte dejan de proyectar lo último). Las señales calibradas parten de esa proyección; el
calendario de tarifas y la regla de prepagas se miden contra la mediana de 6 meses, que es la que asume la
proyección de la división (medirlas contra la de temporada inflaba salud y otros rubros; el backtest lo confirma).

**Backtest largo** (`scripts/backtest_largo.py`, `reports/backtest_largo.md`): el error por período desde 2018
(2018-19, 2020-22, 2023 a jun-2024, desde jul-2024 y últimos 16 meses), para que ninguna mejora gane solo en un tramo.

**Calendario de tarifas: base coherente.** Un aumento anunciado se compara contra el valor que la proyección de su
división supone para ese componente (proyección de la división menos la suma de las de sus componentes, todos con
mediana de 6 meses, incluido el "resto" que INDEC no publica aparte). Prueba con el valor exacto que midió INDEC,
error de la división 2018-2026: luz y gas 2,29 -> 1,32; transporte 1,76 -> 1,70; prepagas 1,62 -> 1,52. Con la base
anterior, un dato exacto de luz y gas llegaba a empeorar vivienda.

Probadas y descartadas (nov-2026, segunda tanda): dólar en la proyección estadística (mejora 2023 pero empeora mucho
desde 2024: el traspaso cambió de régimen), elegir por rubro la combinación de reglas estadísticas (el promedio fijo
gana en todos los períodos), base coherente para las señales de precios (empeora; también recalibradas), base
coherente para la regla de prepagas (no alcanza el umbral) y reconstruir a mano el calendario histórico de tarifas:
la prueba con los valores exactos de INDEC muestra que, desde 2024, ni siquiera el dato perfecto de tarifas baja el
error nacional (sí el de vivienda), así que no vale el esfuerzo.

## Conceptos clave

- **Peso base**: cuánto pesa cada rubro en la canasta de INDEC (ENGHo 2004/05, llevada a dic-2016).
- **Peso efectivo**: el que pondera la variación de cada mes. Cambia con los precios relativos: si un rubro sube más que el
  resto, pesa más el mes siguiente.
- **Arrastre**: INDEC compara promedios mensuales de precios. Un aumento a mitad de mes impacta una parte ese mes y el
  resto el siguiente.
- **Prueba fuera de muestra**: para decidir si una fuente sirve, cada mes del pasado se predice usando solo lo que
  se sabía antes de ese mes. Así el error medido es el que se hubiera tenido de verdad.
