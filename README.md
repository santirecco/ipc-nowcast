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
| Pasajes de micro de larga distancia | Pasaje más barato y precio promedio de 30 rutas desde Retiro (parte del 07.3 Transporte público) | Páginas de ruta de centraldepasajes.com.ar (`scripts/relevar_micros.py`) | desde 26-nov-2026 (se evalúa con ~6 meses de historia) |
| IPC Ciudad de Buenos Aires | Anticipo del dato nacional | API de series de datos.gob.ar | desde 2012 |
| REM del BCRA | Mediana de los analistas para la inflación mensual (solo referencia) | Planilla mensual publicada por el BCRA | se baja sola cada día |

Los precios de SEPA procesados por día se guardan en el caché de GitHub Actions (`data/cache/sepa/`, no se suben
al repo); al repo van solo los índices por mes, región y clase (`data/precios/sepa/`).

## Tareas manuales

Ninguna. El calendario de regulados lo revisa una tarea programada todos los lunes (busca aumentos
anunciados y actualiza `config/regulados/`); conviene mirar sus cambios de vez en cuando. El tablero muestra el
estado de cada fuente (`data/tablero/fuentes.csv`): si alguna figura como "atrasada", dejó de publicar o cambió su sitio.

## Regla para sumar fuentes

**Criterio vigente (desde el 23-nov-2026): rubro por rubro.** El camino es bajar el error de cada rubro; el
nacional baja como consecuencia. Un cambio entra si baja el error fuera de muestra de su rubro (clase o división, con
la contabilidad coherente de abajo) y tiene una razón que lo explique. El nacional se mira como control, sin vetar
mejoras de rubro por errores que dejan de compensarse. Herramientas: `/home/claude/exp/rubros.py` (clases) y
`divs.py`/`divs_cmp.py` (divisiones en día 1, mitad y fin).

**Criterio anterior (20 al 23-nov-2026).** Todo se mide fuera de muestra: cada mes del pasado se predice solo con
lo que se sabía en ese momento, y una fuente se usa solo con datos que ya eran públicos entonces. Un cambio entra si:
1. baja el error de su rubro (clase o división) con suficientes observaciones (regiones × meses);
2. tiene una razón económica que lo explique (no se elige entre muchas variantes la que mejor da);
3. no empeora el error nacional de forma estadísticamente clara (t > 2 en la diferencia mes a mes) en ningún
   período del backtest largo.

Antes se exigía que bajara el error nacional en cada período. Con 16-28 meses por período eso premia errores que se
compensan por casualidad (en 2025-2026, subestimar verduras tapaba sobreestimar ropa y hogar) y bloquea cada
arreglo por separado. Las pruebas anteriores al 20-nov-2026 se decidieron con la regla vieja.

Regla anterior: una fuente o un cambio de método entraba solo si bajaba el error del índice nacional fuera de muestra,
mirando todo el período y no solo los meses recientes.
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
  **Evaluadas el 21-nov-2026, no entran.** Con unos 7.100 precios de 8 tiendas (2023-2026), la variación mensual no
  se parece a la de INDEC (correlación 0,02 en ropa y −0,17 en electro/hogar, saltos de ±15%: el archivo guarda sobre
  todo liquidaciones y promociones sueltas). En el backtest se eligió solo un mes (equipos/recreación) y el fin de mes
  jul-24+ empeoró de 0,320 a 0,326. Candidatas sacadas de `OPCIONES` y workflow apagado (queda a mano).

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
  (fin 16 meses 0,198 -> 0,207; jul-24+ 0,331 -> 0,336; diferencia no significativa, t = 0,3). Con la regla vieja
  no entraba; con el criterio nuevo entra junto con el ajuste de ropa y hogar (abajo). Con el mayorista como desvío de la
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

**Adoptado el 20-nov-2026 (criterio nuevo):**
- **Historia del Mercado Central 2024-2025** (arriba): verduras pasa a usar el mayorista con historia desde 2024.
- **Ropa y equipamiento del hogar: estacionalidad neta de la tendencia relativa** (`modelo.DIVISIONES_TRANSABLES`).
  En la proyección de división, la regla de temporada compara cada rubro con la núcleo usando el desvío típico desde
  2017; en los bienes transables ese desvío cambió de régimen (hasta 2022 subían más que la núcleo, desde 2024 menos:
  apertura y dólar quieto). Ahora la temporada se mide neta de la tendencia relativa de 12 meses y se le suma la
  tendencia relativa actual. Error de la división por región, modelo completo: ropa jul-24+ 1,32 -> 1,26 (sesgo
  +0,063 -> +0,048 pp del nivel general), últimos 16 meses 1,03 -> 0,93 (sesgo +0,042 -> +0,021); hogar 0,92 -> 0,88.
  Antes: 2018-19 igual, 2020-22 algo peor (ropa 2,04 -> 2,09), 2023-jun24 mejor. Aplicada a todos los rubros empeora:
  solo donde está el mecanismo.
- Resultado conjunto (nacional, fin de mes): 2018-19 1,097 -> 1,096; 2020-22 0,706 -> 0,720 (t = 1,4);
  2023-jun24 3,470 -> 3,460; jul-24+ 0,331 -> 0,326; últimos 16 meses 0,198 -> 0,196. Ninguna diferencia es
  significativa en contra. Inicio de mes en los últimos 16 meses 0,231 -> 0,243 y mitad 0,207 -> 0,215 (t = 1,7 y
  1,1): sin precios del mes, el sesgo de alimentos queda menos compensado. Víspera 0,134 -> 0,145.

**Arrastre mayorista para el pronóstico del día 1 (20-nov-2026)** (`arrm`, `mayoristas.arrastre_mercado_central` y
`arrastre_hacienda`). Un mes que termina más caro de lo que empezó arrastra suba al siguiente, y eso se sabe el día 1.
Verduras y frutas: variación entre el primer y el último día del mes anterior en el Mercado Central (planillas
diarias; antes, las tablas de precio al principio y al final del mes de los informes mensuales, que coinciden con las
planillas en ene-26). Carnes: hacienda de consumo de la segunda quincena contra el promedio del mes. Solo para el
pronóstico de inicio de mes (`SOLO_INICIO`): usado también a fin de mes mejoraba carnes (error 1,47 -> 1,20) pero el
nacional empeoraba con t = 2,0 (destapaba el error de combustibles de mar-26). Resultado: inicio de mes jul-24+
0,379 -> 0,356 y últimos 16 meses 0,243 -> 0,197 (mejor en 11 de 18 meses); ningún período empeora. Corrección
del 21-nov: la baja de mitad y fin de mes jul-24+ que se vio ese día (0,342 -> 0,335 y 0,326 -> 0,320) venía de
que el modelo eligió la señal de tiendas para ropa en dic-24 con datos parciales; sin tiendas, mitad y fin quedan
igual que antes (0,342 y 0,326). Correlación del arrastre con la sorpresa de verduras: 0,41.
Combustibles (`arrn`, `indicadores.arrastre_nafta`): mismo criterio con la foto diaria del surtidor (último día del
mes anterior contra su promedio; el error de mar-26 fue un aumento de fin de mes que INDEC repartió entre marzo y
abril). La foto diaria empezó el 18-nov-2026: el primer arrastre sale en ene-2027 y la candidata se evalúa sola cuando
junte meses.
**Carnes: hacienda en forma de reemplazo (23-nov-2026)** (`hacr`). A fin de mes carnes andaba peor que el día 1
(error 1,47 contra 1,21 en los últimos 16 meses): la hacienda entraba como desvío de su tendencia sumado a la
proyección de temporada, y así se perdía la señal (correlación con la sorpresa ≈ 0). Pero la carnicería sigue el
nivel de la hacienda con un mes de rezago (correlación de la hacienda del mes anterior con la carne de INDEC: 0,80;
nov-25 hacienda +15% -> carne +5,7% y +8,2% en dic). Ahora la hacienda de este mes y del anterior reemplaza en parte
a la proyección (como el surtidor en combustibles), sola o con SEPA de cortes frescos (la mejor señal de góndola:
0,61 con la sorpresa; pollo, cerdo y fiambres no suman) y con el arrastre del mes anterior (que combinado con datos
del mes vale en todos los momentos; solo, sigue siendo solo del día 1). Carnes a fin de mes: jul-24+ 1,66 -> 1,29,
últimos 16 meses 1,47 -> 1,07; mitad de mes 1,77 -> 1,38. Nacional, todo dentro del ruido (|t| < 0,6): día 22
jul-24+ 0,334 -> 0,318, fin 0,326 -> 0,327, últimos 16 meses fin 0,196 -> 0,204, mitad 0,215 -> 0,223.
SEPA de carne vacuna reacciona menos que la carnicería (dic-24 +4,5% contra +8,2%; feb-25 +4,4% contra +7,9%): el
coeficiente puede amplificarla (hasta 3).

**Rubro por rubro (23-nov-2026).** Ranking de rubros por error aportado a fin de mes (últimos 16 meses): tarifas
04.5 (0,126 pp), carnes (0,105), combustibles (0,102), verduras (0,087), turismo/juguetes (0,086), ropa (0,077),
restaurantes (0,070), transporte público (0,048), prepagas (0,046). Cambios:
- **Contabilidad coherente para las correcciones estadísticas** (`modelo.ESTADISTICAS_COHERENTES`, base `elegida`):
  cada corrección reemplaza la parte del rubro dentro de la proyección de la división, en vez de sumarse encima.
  Sin esto, la inercia de ropa se sumaba al ajuste de transables de la división (doble conteo: sesgo de ropa
  +0,021 -> −0,025).
- **Inercia propia** (`propio`: mes anterior y promedio de 3 meses del rubro) como candidata en todos los rubros
  (menos combustibles) y combinada con SEPA (`sepa+propio`): precios regulados o indexados suben en escalones
  parecidos. Prepagas 1,26 -> 0,34; ropa 1,19 -> 1,00; calzado 1,50 -> 1,22; medicamentos 0,59 -> 0,46 (día 1).
- **Prepagas** como rubro a pronosticar (desde 2024 aumentan según la inflación de dos meses antes).
- **Combustibles a fin de mes sin el precio de cierre** (`NAFTA_FIN_DE_MES = False`): sin saber el día del aumento
  exageraba los meses con aumentos tardíos (mar-26: 19% contra 7%). Rubro 16m 2,03 -> 1,49.
- **Arrastre solo también a mitad de mes** (`ARRASTRE_A_MITAD`): verduras mitad 4,77 -> 4,27, frutas 2,95 -> 2,72.
  Combinaciones `may+arrm` y `sepaf+may+arrm` disponibles (a día 22 verduras sigue eligiendo el arrastre: en los 6
  meses comparables 3,40 contra 3,96 del Mercado Central del mes).
- Resultado por división (error medio, puntos de la división): fin de mes 16m 0,770 -> 0,634, jul-24+ 1,041 -> 0,816;
  día 1 16m 0,763 -> 0,664. Sumando el aporte de cada división: fin 16m 0,696 -> 0,573 (−18%), jul-24+ 0,965 -> 0,752
  (−22%). Nacional: fin 16m 0,204 -> 0,197; jul-24+ 0,327 -> 0,359; día 1 16m 0,197 -> 0,246 (sesgo −0,10: tarifas
  subestimadas en el backtest, que no tiene el calendario de resoluciones; en vivo sí lo usa). Pendiente: reconstruir
  el calendario histórico de tarifas para medir bien 04.5, y verduras a mitad de mes (se arregla solo cuando el
  Mercado Central diario junte meses).
- **Límite de SEPA (24-nov-2026).** Aun para el mismo producto, la variación mensual de SEPA y la del precio promedio
  que publica INDEC casi no se parecen (leche fresca −0,01; pan 0,23; promedio de 23 variedades 0,40), aunque los
  promedios de largo plazo coinciden. INDEC releva también almacenes y comercios de barrio, y su propia muestra tiene
  ruido: SEPA no puede seguir eso mes a mes. Probadas sin ganancia: las variedades de INDEC en SEPA ponderadas con los
  pesos que revela INDEC (`sepaw`, casi nunca elegida) y SEPA del mes anterior (`sepa+sepal`: medicamentos 0,55 ->
  0,49 pero pan, azúcar y bebidas peor; en conjunto empate). Conclusión: para bajar el fin de mes, más que exprimir
  SEPA hay que relevar lo que hoy no se mide (tarifas, transporte público, cigarrillos, diarios, servicios).
- **Calendario histórico de aumentos anunciados (24-nov-2026)** (`regulados_hist`, `data/precios/regulados/
  eventos.csv`, candidata `cal`). Cada aumento con fecha de vigencia, ítem, componente, parte, regiones, % y fuente.
  Se convierte a la variación del promedio del mes (un aumento del 29 pega casi entero en el mes siguiente); a mitad
  de mes solo cuentan los aumentos vigentes hasta ese día. Empieza por cigarrillos (Massalin 72%, BAT 28%; precios
  nacionales): sigue al tabaco de INDEC con correlación 0,88. Tabaco a fin de mes 16m 1,39 -> 0,52 (t = −2,5),
  jul-24+ 1,58 -> 1,00. Nacional fin 16m 0,197 -> 0,193. Con las listas de BAT de junio y agosto de 2026, tabaco a
  mitad de mes 0,56 -> 0,53 y día 22 0,53 -> 0,50 (16m).
- **Descartadas: luz, gas y transporte del AMBA en el calendario (24-nov-2026).** Se reconstruyeron mes a mes desde
  jul-24 con los 44 reportes de tarifas del IIEP-UBA (`scripts/pruebas/iiep_tarifas.py`; cargo fijo y variable del
  cuadro tarifario, y gasto en transporte). Quedan en `eventos.csv`, pero no como candidata: el cuadro del usuario sin
  subsidio no sigue al 04.5 de INDEC (correlación 0,6 solo por la quita de subsidios de feb-26; sin ese mes, ~0), y
  con el calendario el rubro empeoraba (fin 16m 2,40 -> 2,84, t = 2,0; nacional 0,193 -> 0,227). INDEC promedia
  usuarios con y sin subsidio, y lo que mueve su índice son las bonificaciones y los topes de consumo subsidiado, que
  el reporte no cuantifica. En transporte (correlación 0,62 con el 07.3 del GBA) la selección nunca la eligió frente a
  la inflación reciente. Siguen: diarios y colegios.
- **Regla de subsidios al gas (26-nov-2026)** (`modelo.brecha_subsidio_gas`, `data/precios/regulados/
  subsidios_gas.csv`). Lo que mueve el 04.5 de INDEC fuera del GBA no es el cuadro tarifario sino las bonificaciones
  y los bloques de consumo subsidiado (ejemplo: en oct-26 terminó la bonificación extra de invierno del gas y el 04.5
  subió 10-11% en Pampeana, Cuyo y Patagonia contra ~2% proyectado; fue −0,21 pp del error de ese mes). Los reportes
  del IIEP traen, mes a mes, cuánto cambió la factura de gas de los hogares con subsidio y de los sin subsidio
  (N2/N3 contra N1 hasta ene-26; cargo variable con y sin subsidio desde abr-26, que se toma a la mitad). La brecha
  se suma al 04.5 con parte = peso del gas en el 04.5 × hogares con subsidio (~50%): Pampeana y Cuyo 0,225,
  Patagonia 0,275. Se conoce antes del mes (resoluciones de la Secretaría de Energía) y la tarea de los lunes la
  carga. La brecha sigue al error del 04.5 en esas tres regiones en los dos tramos (correlación 0,4-0,7 en 2024-25 y
  0,7-0,9 en 2026); en GBA y el norte no (en GBA la factura la domina la luz; en el norte el gas no es calefacción),
  así que ahí no se aplica. La elección de regiones se hizo mirando estos mismos datos: es la parte menos probada.
  Resultado: división 04 a fin de mes 16m Pampeana 0,99 -> 0,78, Cuyo 1,53 -> 1,24, Patagonia 1,57 -> 1,40 (las
  demás igual). Nacional 16m: inicio 0,246 -> 0,242, mitad 0,232 -> 0,221, día 22 0,208 -> 0,196, fin 0,193 -> 0,184,
  víspera 0,163 -> 0,151; jul-24+ fin 0,358 -> 0,355. Oct-26 a fin de mes: 1,99 -> 2,10 (INDEC 2,17). No cubre la
  quita de subsidios de feb-26 (+12% en todo el país), que cambió el esquema entero y no tiene una brecha comparable.
- **Boleto de colectivo urbano del interior en el calendario (26-nov-2026).** El 07.3 (transporte público) tenía
  mucho más error fuera del GBA (16m: Cuyo 2,89, Noroeste 2,23, Patagonia 2,01) y los saltos coincidían con aumentos
  del boleto que fijan provincias y municipios con días o semanas de anticipación (ej.: Cuyo +13,8% en ene-26, cuando
  Mendoza pasó de $1.200 a $1.400 el 1/1, contra −0,2% proyectado). Se reconstruyó con la prensa local el boleto desde
  jul-24 de Mendoza (parte 0,30 del 07.3 de Cuyo), San Miguel de Tucumán (0,20 de Noroeste), Neuquén (0,12 de
  Patagonia), Córdoba (0,06) y Rosario (0,05 de Pampeana), con fecha de vigencia y fuente de cada aumento en
  `eventos.csv`; vuelve `cal` como candidata del 07.3. Resultado a fin de mes 16m: 07.3 2,02 -> 1,75 (Cuyo 2,89 ->
  1,94, Noroeste 2,23 -> 1,82, Patagonia 2,01 -> 1,88, GBA 1,50 -> 1,40 con el gasto en transporte del IIEP, Pampeana
  y Noreste igual). Nacional 16m: mitad 0,221 -> 0,216, día 22 0,196 -> 0,191, fin 0,184 -> 0,183. Quedaron afuera
  Corrientes (el +46% de nov-25 no aparece en el Noreste de INDEC) y Posadas (falta un aumento de jul-26), y Salta
  (historia incompleta). Los ítems sin eventos se toman sin cambios desde jul-24 (antes quedaban vacíos y anulaban la
  región). La tarea de los lunes agrega los aumentos nuevos de estas ciudades.
- **Saltos de temporada que no persisten (26-nov-2026)** (`modelo.MESES_SALTO`). La proyección de cada división
  promedia 4 reglas; dos de ellas (último mes y mediana de 3 meses) arrastraban al mes siguiente saltos que son de
  temporada: en educación, el aumento de cuotas de marzo se proyectaba de nuevo en abril (error de abril 4,3 pp en
  jul-24+). Ahora esas dos reglas se miden sin los meses de salto: educación marzo; ropa marzo-abril y
  septiembre-octubre (cambio de temporada); recreación enero y julio (vacaciones); restaurantes enero. Educación a fin
  de mes: jul-24+ 2,23 -> 2,00, 16m 1,34 -> 1,26, abril 4,27 -> 1,30; recreación 16m 1,06 -> 1,05; ropa igual (su
  proyección la reemplazan las clases 03.1/03.2). Nacional fin: 16m 0,183 -> 0,178, jul-24+ 0,355 -> 0,348; backtest
  largo 2018-19 1,095 -> 1,072, 2020-22 0,715 -> 0,696. Se probaron y no entraron: transporte enero-julio (peor en los
  últimos meses), varios enero (mixto) y, en educación, usar solo las reglas estacionales en marzo (mejor en la
  historia larga, peor en 16m porque mar-25 fue excepcional). El salto de marzo en sí sigue siendo el mayor error de
  educación (mar-25: 16-32% contra 7-12% proyectado): lo resolvería un calendario de cuotas por provincia.
- **Probado y descartado el 27-nov-2026.** (1) Tendencia de precio relativo (la corrección de ropa y hogar) en
  todas las divisiones: Vivienda tiene un sesgo grande y persistente (16m −0,95 pp por mes: tarifas −1,6 y alquileres
  −0,8 en las clases), pero la corrección casi no lo mueve y el nacional empeora (fin 16m 0,178 -> 0,186, jul-24+
  t = 2,6). (2) Corregir cada clase por su sesgo de los 6 o 12 meses anteriores (entero o a la mitad): en promedio
  no mejora (1,336 -> 1,337-1,404); solo ayudaría en tabaco y lácteos, y elegir esas a mano sería ajustar al ruido.
  (3) IPC provinciales como anticipo para la víspera (como el de CABA): Córdoba, Mendoza y Neuquén publican el mismo
  día que INDEC, no antes. (4) Parte de cigarrillos según participación de mercado (Massalin 0,60, BAT 0,20): el
  calendario pasa ~92% de las listas al dato de INDEC, pero el coeficiente de la regresión ya lo compensa (tabaco
  igual); se revirtió.
- **Fuentes para restaurantes y turismo (26-nov-2026, `scripts/pruebas/servicios_sondeo*.py`).** Se sondearon ~40
  sitios. PedidosYa (403), Rappi (429), McDonald's, KFC, Starbucks, Despegar, Almundo, Turismocity y Flechabus
  bloquean a los servidores; Flybondi y JetSMART no responden; las cadenas con web propia (Mostaza, Burger King,
  Kentucky, Grido, Havanna, Mi Gusto, El Noble) no publican precios en la web. Lo único que funcionó: (1) Central
  de Pasajes publica el pasaje más barato y el promedio de cada ruta de micro: queda relevándose a diario (tabla de
  fuentes); (2) Tucán, plataforma de pedidos propia de restaurantes argentinos, tiene un directorio público
  (POST `app.loveat.la/api/menu/near`, ~620 comercios en CABA) pero el menú con precios
  (`/api/diner/{sucursal}/menu/{menu}`) responde error 500 sin la sesión del navegador: pendiente. Pasajes aéreos y
  paquetes turísticos: sin fuente por ahora.
- Descartada: estacionalidad propia (mismo mes de los dos años anteriores) como candidata en todos los rubros.
  Empeora la mayoría de los rubros desde jul-24 (ropa 1,24 -> 1,71, educación 0,79 -> 1,93 en 16m) aunque el
  nacional de 16 meses bajaba (0,197 -> 0,168) por compensación.

Entre cortes (días 16-21 y 23 a fin de mes), el pronóstico en vivo usa todos los días que van del mes del Mercado
Central y de la hacienda, como ya hacía con SEPA (antes se cortaba en el día 15 o 22 y se ignoraban hasta 6 días).
No cambia el backtest, que se hace con cortes fijos.

## Conceptos clave

- **Peso base**: cuánto pesa cada rubro en la canasta de INDEC (ENGHo 2004/05, llevada a dic-2016).
- **Peso efectivo**: el que pondera la variación de cada mes. Cambia con los precios relativos: si un rubro sube más que el
  resto, pesa más el mes siguiente.
- **Arrastre**: INDEC compara promedios mensuales de precios. Un aumento a mitad de mes impacta una parte ese mes y el
  resto el siguiente.
- **Prueba fuera de muestra**: para decidir si una fuente sirve, cada mes del pasado se predice usando solo lo que
  se sabía antes de ese mes. Así el error medido es el que se hubiera tenido de verdad.
