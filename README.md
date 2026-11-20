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
coherente para la regla de prepagas (no alcanza el umbral) y reconstruir a mano el calendario histórico de tarifas.
Con los valores exactos de INDEC para luz, gas y transporte en todas las regiones (el mejor calendario posible), el
error nacional de fin de mes queda: 2018-19 1,10 -> 0,95; 2020-22 0,71 -> 0,68; 2023-jun24 3,47 -> 3,58;
jul-24 en adelante 0,36 -> 0,34; últimos 16 meses 0,20 -> 0,22. Mejora el rubro siempre, pero en el nacional el
efecto es mixto: en los últimos meses el error de tarifas compensaba un sesgo hacia arriba de alimentos. Un calendario
real (menos exacto) daría menos que esto, así que no vale reconstruirlo a mano; sigue validándose hacia adelante.

Rubros sin relevamiento (nov-2026, tercera tanda). Candidatas nuevas con historia, juzgadas por el error de su clase:
"alimentos del mes anterior" (INDEC) para restaurantes (entra: error de la clase 1,92 -> 1,48), "indexación con
demora" (inflación de t-2 a t-4) para alquileres, educación, telefonía, recreación y cuidado personal, dólar para
telefonía, recreación y papelería, salarios para ropa y calzado, y hacienda de dos meses antes para carnes. Con lo
que eligió la regla, el backtest desde jul-24 baja: inicio 0,408 -> 0,384; mitad 0,392 -> 0,371; fin 0,361 -> 0,341.
Ropa: ninguna fuente con historia le gana a la estadística; se relevan tiendas desde nov-2026 y se prueba reconstruir
su historia con el archivo web (`scripts/pruebas/wayback.py`). Descartado: decidir las fuentes con historia desde
2019 en vez de 2024 (mejora 2023, de 3,47 a 2,93 a fin de mes, pero empeora el régimen actual: 0,341 -> 0,379).

Dispersión de mitad y fin de mes (nov-2026). Descomponiendo el error de los últimos 16 meses, carnes explicaba la
mitad de la variabilidad a mitad de mes: la señal de hacienda exageraba, sobre todo las bajas. Entra la hacienda
asimétrica (subas y bajas con coeficientes distintos; estimado: las bajas casi no pasan a la carnicería) junto con
los cortes de SEPA. Últimos 16 meses: mitad de mes 0,255 -> 0,217 (peor mes 0,61 -> 0,47), día 22 0,244 -> 0,202,
fin 0,202 -> 0,190. Combustibles: el dato mensual de surtidor es el precio vigente y no el promedio del mes; se
guarda la foto diaria desde nov-2026 y una candidata con el promedio del mes entra sola cuando tenga historia.
Descartados: amortiguar el movimiento que traen los precios del mes, sumar parte del error del mes anterior,
medir el error de cada clase ponderado por región, y dar más peso a los meses recientes al elegir (vida media 12).

Cuarta tanda (nov-2026):
- **Eficiencia**: calibración de 4 min a 78 s y backtest de 10 min a 19 s (mismos resultados, verificados).
- **Señales para los "resto"** (lo que INDEC no publica aparte, serie implícita padre menos hijos): solo donde el
  resto pesa al menos 10% de su grupo en GBA y Pampeana (equipamiento, salud, recreación, bienes varios); en los
  demás la serie implícita es casi puro ruido (p. ej. el resto de alimentos pesa 0,2-0,4% en la estructura). Desde
  jul-24: mitad 0,349 -> 0,345; día 22 0,339 -> 0,334; fin 0,334 -> 0,327; últimos 16 meses sin cambios.
- **Carnes por tipo** (pollo, cerdo, fiambres en SEPA): no mejoran a cortes vacunos + hacienda asimétrica. Los
  índices se siguen calculando.
- **Verduras y frutas con la canasta de INDEC** (tomate, papa, cebolla, lechuga, zapallo, batata; banana, manzana,
  naranja, limón, con los pesos que revela la historia de INDEC): con los precios de INDEC explicaría la clase con
  ~2,3 pp de error, pero los de góndola de esas mismas variedades se mueven distinto; mejora frutas y empeora el fin
  de mes del índice, no entra. Se sigue calculando.
- **Combustibles por día con el archivo web**: hay solo ~30 copias de la página de precios desde 2023, no alcanza.
  Queda la foto diaria propia (desde nov-2026) y la candidata con el promedio del mes, que entra sola con historia.
- **Tiendas de ropa y electro** reconstruidas con el archivo web (`.github/workflows/wayback.yml`, corre sola).
  Panel de hasta 40 productos por tienda y mes (los que más meses duran). En el archivo el mismo producto casi nunca
  aparece en meses seguidos, así que el índice es de ventas repetidas (efecto producto + efecto mes), recalculado mes
  a mes solo con lo que se sabría a esa fecha (`indicadores.serie_tiendas`). Candidatas `tienda` y `tiendal` en ropa,
  calzado, equipamiento del hogar y equipos/recreación: entran solas si bajan el error de su clase con 6+ meses.

Quinta tanda (nov-2026):
- **SEPA ponderado por sucursales** (lo que más se vende pesa más; también raíz y por tamaño de cadena): mejora algo
  la mitad de mes y empeora el fin de mes; no entra. Queda como opción apagada (`IPC_PESO_SEPA`).
- **Precio con promoción vs. de lista** (historia de SEPA reprocesada con los dos precios, mismos días): diferencia
  mínima (fin de mes 0,189 vs. 0,188); solo ~3% de los productos tiene promoción. No entra.
- **Cache de SEPA completo**: desde dic-2025 había meses con la mitad de los días (se había reprocesado un día de cada
  dos). Se completaron todos los días que tiene el archivo (abr-jun 2026 no existen). No es una decisión de método
  sino de datos: en tiempo real esos días sí estaban. Últimos 16 meses: inicio 0,240 -> 0,231; mitad 0,214 -> 0,207;
  día 22 0,200 -> 0,196; fin 0,191 -> 0,198; víspera 0,128 -> 0,134.
- **Informe automático cuando publica INDEC** (`scripts/informe_mes.py`, corre en el workflow mensual):
  pronóstico en cada momento contra el dato, error por rubro y región, y qué señales acercaron o alejaron el
  pronóstico. Sale en `reports/informe_AAAA-MM.md` y en el JSON público (`informe`).

Sexta tanda (nov-2026), buscando bajar el fin de mes (0,198 en los últimos 16 meses):
- **Diagnóstico.** La réplica es exacta (con los rubros reales da error cero): todo el error es de pronóstico de
  rubros. Desde jul-24, alimentos y transporte explican la mayor parte de lo que se mueve mes a mes (carnes,
  verduras y el momento de los aumentos de combustible), y los bienes transables tienen un sesgo hacia arriba
  persistente: ropa +0,063 pp del nivel general (18 de 28 meses), equipamiento del hogar +0,043 (22 de 28),
  transporte +0,058. En los últimos 16 meses ese sesgo (+0,09 pp sin alimentos) lo compensaba un sesgo hacia abajo
  de alimentos (−0,09).
- **Historia del Mercado Central 2024-2025** (`mayoristas.promedios_informes`, textos en
  `data/precios/mayoristas/monitoreo/`, los baja `scripts/pruebas/monitoreo_mc.py`): los informes mensuales
  Monitoreo Federal traen el precio promedio del mes por especie (mes anterior y mismo mes del año previo).
  Coinciden con las planillas diarias de 2026 y la variación de verduras correlaciona 0,94 con INDEC. Mejora mucho
  la clase (verduras 5,2 -> 3,75 de error; ene-26: 6,4 -> 15,2 con real 28; may-26: 2,6 -> 19,0 con real 18,8) y
  saca el sesgo de alimentos (−0,09 -> −0,02), pero deja a la vista el de los bienes: el nacional empeora
  (fin 16 meses 0,198 -> 0,207; jul-24+ 0,331 -> 0,336). No entra; queda apagada (`IPC_MC_INFORMES=1`) para
  volver a probarla junto con una mejora en ropa y hogar (tiendas online). Con el mayorista como desvío de la
  temporada en vez de sumarlo (para no contar la estacionalidad dos veces): peor (0,212).
- **Historia mayorista o de surtidor no disponible**: las planillas diarias viejas del Mercado Central no están
  (servidor solo el año en curso; archivo web hasta mediados de 2022); el histórico de surtidores de Energía en el
  archivo web es de dic-2023 y el servidor no responde desde fuera del país.
- Descartadas también: promediar las fuentes que pasan la regla en cada clase (todas o las 2 mejores; mejora el
  inicio de mes pero empeora el fin desde jul-24: 0,331 -> 0,344/0,353), promediar solo las reglas estadísticas
  (fin jul-24+ 0,346), estacionalidad de la proyección de división neta de la tendencia relativa de cada rubro
  (proyección pura jul-24+ 0,462 -> 0,489), corrección del sesgo de los últimos 6/12/24 meses por división
  (ninguna variante mejora todos los períodos: la mejor baja jul-24+ pero empeora 2020-22) e inflación de bienes de
  la región como señal para ropa, hogar, recreación y cuidado personal (fin 16 meses 0,208).

## Conceptos clave

- **Peso base**: cuánto pesa cada rubro en la canasta de INDEC (ENGHo 2004/05, llevada a dic-2016).
- **Peso efectivo**: el que pondera la variación de cada mes. Cambia con los precios relativos: si un rubro sube más que el
  resto, pesa más el mes siguiente.
- **Arrastre**: INDEC compara promedios mensuales de precios. Un aumento a mitad de mes impacta una parte ese mes y el
  resto el siguiente.
- **Prueba fuera de muestra**: para decidir si una fuente sirve, cada mes del pasado se predice usando solo lo que
  se sabía antes de ese mes. Así el error medido es el que se hubiera tenido de verdad.
