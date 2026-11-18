# ipc-nowcast

Predictor del IPC de INDEC: replica exactamente cómo INDEC arma el índice y, con precios que se
juntan todos los días (supermercados, tarifas, combustibles, etc.), anticipa el dato del mes antes de que se publique.

## Estado

| Fase | Qué es | Estado |
|---|---|---|
| 0 | Infraestructura (este repo + tareas automáticas) | ✅ |
| 1 | Réplica exacta de INDEC y pesos efectivos mes a mes | ✅ ver [`reports/replica_indec.md`](reports/replica_indec.md) |
| 2 | Mapa de la canasta: pesos de grupos y clases por región; clasificación de productos de supermercado | ✅ |
| 3 | Alimentos: SEPA/Precios Claros, supermercados, Mercado Central, carne | 🟡 supermercados online recolectando a diario desde 18/11/2026 |
| 4 | Regulados: calendario mensual en `config/regulados/` (luz, gas, transporte, prepagas) | 🟡 noviembre cargado; falta combustibles |
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
tests/         Controles automáticos (por ejemplo: que la réplica de INDEC siga siendo exacta)
.github/       Tareas automáticas que corre GitHub (descargas diarias/mensuales)
```

## Pasos que se corren

```bash
pip install -r requirements.txt
python scripts/actualizar_indec.py   # 1. baja las series oficiales de INDEC
python scripts/replicar_indec.py     # 2. replica el índice y calcula pesos efectivos
python scripts/scrapear_supermercados.py  # 3. precios del día de 5 supermercados online
python scripts/actualizar_ipcba.py        # 4. IPC de la Ciudad de Buenos Aires
python scripts/backtest.py                # 5. error histórico del modelo
python scripts/nowcast.py                 # 6. pronóstico del mes en curso
pytest                               # controles
```

Las tareas de `.github/workflows/` hacen esto solas y guardan los resultados en el repo.

## Tareas manuales (≈15 min por semana)

- **Calendario de regulados**: revisar/cargar `config/regulados/AAAA-MM.yaml` con los aumentos del mes
  (luz, gas, agua, transporte, prepagas, combustibles, cigarrillos, colegios). Cada ítem lleva su fuente.
- **REM**: cargar la mediana del REM del BCRA en `config/externos.yaml` cuando se publica (referencia).

## Conceptos clave

- **Peso base**: cuánto pesa cada rubro en la canasta de INDEC (ENGHo 2004/05, llevada a dic-2016).
- **Peso efectivo**: el que pondera la variación de cada mes. Cambia con los precios relativos: si un rubro sube más que el
  resto, pesa más el mes siguiente.
- **Arrastre**: INDEC compara promedios mensuales de precios. Un aumento a mitad de mes impacta una parte ese mes y el
  resto el siguiente.
