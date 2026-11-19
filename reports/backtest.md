# Backtest del modelo

*Generado el 19/11/2026.*

Se simula el pronóstico de cada mes usando solo la información disponible en ese momento:
- **Inicio de mes:** solo la proyección estadística por región y división.
- **Mitad de mes:** además, los precios hasta el día 15: góndolas de todo el país (SEPA, desde septiembre de 2024),
  verduras y frutas mayoristas (Mercado Central, desde 2026), hacienda (desde 2017) y combustibles (precio de YPF;
  a mitad de mes solo el cambio del mes anterior). Cada clase usa solo las fuentes que la mejoraron fuera de muestra
  (ver reports/adelantados.md). En todos los momentos, las prepagas siguen su regla de ajuste (IPC de dos meses antes).
- **Día 22:** lo mismo con los precios hasta el día 22 (calibración propia; se usa desde el día 22 hasta fin de mes).
- **Fin de mes:** lo mismo con el mes completo.
- **Víspera:** además, el IPC de la Ciudad de Buenos Aires del mismo mes, que se publica unos días antes que INDEC
  Con 12 meses de historia o más, se usa por rubro: cada división del GBA se corrige hacia la misma división de la
  Ciudad, var = modelo + k × (Ciudad − modelo), con k estimado con los meses anteriores. Antes de eso, se mezcla el
  nivel general (peso estimado con la historia). En los meses en que la Ciudad
  se desvió de INDEC con el mismo signo todos los años (enero y julio) se corrige el IPC CABA por ese desvío típico.

El calendario de regulados y los supermercados online no tienen historia: su aporte se mide en la prueba en
paralelo de los próximos meses. Los meses sin datos de SEPA (abril a junio de 2026) solo usan la hacienda.

## Error contra el dato de INDEC (nacional, variación mensual)

| Período | Momento | Error promedio (pp) | 80% de los meses dentro de (pp) | Error máximo (pp) | Meses |
|---|---|---|---|---|---|
| jul-24 en adelante | Inicio de mes (solo estadística) | 0,48 | ±0,71 | 1,56 | 28 |
| jul-24 en adelante | Mitad de mes (+ precios hasta el día 15) | 0,42 | ±0,63 | 1,36 | 28 |
| jul-24 en adelante | Día 22 (+ precios hasta el día 22) | 0,43 | ±0,63 | 1,36 | 28 |
| jul-24 en adelante | Fin de mes (+ precios del mes completo) | 0,39 | ±0,61 | 1,32 | 28 |
| jul-24 en adelante | IPC CABA solo | 0,36 | ±0,58 | 1,07 | 28 |
| jul-24 en adelante | Víspera (modelo + IPC CABA) | 0,30 | ±0,52 | 0,92 | 28 |
| 2025-2026 | Inicio de mes (solo estadística) | 0,45 | ±0,63 | 1,56 | 22 |
| 2025-2026 | Mitad de mes (+ precios hasta el día 15) | 0,38 | ±0,62 | 1,14 | 22 |
| 2025-2026 | Día 22 (+ precios hasta el día 22) | 0,38 | ±0,61 | 1,13 | 22 |
| 2025-2026 | Fin de mes (+ precios del mes completo) | 0,35 | ±0,56 | 1,02 | 22 |
| 2025-2026 | IPC CABA solo | 0,30 | ±0,52 | 0,93 | 22 |
| 2025-2026 | Víspera (modelo + IPC CABA) | 0,24 | ±0,35 | 0,92 | 22 |
| últimos 16 meses | Inicio de mes (solo estadística) | 0,33 | ±0,45 | 0,65 | 16 |
| últimos 16 meses | Mitad de mes (+ precios hasta el día 15) | 0,24 | ±0,35 | 0,64 | 16 |
| últimos 16 meses | Día 22 (+ precios hasta el día 22) | 0,25 | ±0,33 | 0,63 | 16 |
| últimos 16 meses | Fin de mes (+ precios del mes completo) | 0,20 | ±0,27 | 0,61 | 16 |
| últimos 16 meses | IPC CABA solo | 0,23 | ±0,30 | 0,82 | 16 |
| últimos 16 meses | Víspera (modelo + IPC CABA) | 0,16 | ±0,31 | 0,53 | 16 |

## Detalle mes a mes

| Mes | INDEC | Inicio de mes | Mitad de mes | Día 22 | Fin de mes | IPC CABA | Víspera | Clases con datos propios |
|---|---|---|---|---|---|---|---|---|
| 10/2026 | 2,2 | 1,73 | 1,53 | 1,55 | 1,56 | 1,92 | 1,65 | 120 |
| 09/2026 | 1,9 | 1,47 | 1,54 | 1,40 | 1,40 | 1,84 | 1,60 | 120 |
| 08/2026 | 1,7 | 1,63 | 1,74 | 1,75 | 1,69 | 1,69 | 1,68 | 120 |
| 07/2026 | 2,1 | 1,95 | 1,95 | 1,95 | 1,94 | 2,93 | 2,12 | 78 |
| 06/2026 | 1,9 | 2,26 | 2,17 | 2,17 | 2,03 | 1,81 | 1,82 | 78 |
| 05/2026 | 2,1 | 2,57 | 1,87 | 1,87 | 1,87 | 2,11 | 1,96 | 78 |
| 04/2026 | 2,6 | 3,02 | 2,47 | 2,47 | 2,47 | 2,48 | 2,45 | 78 |
| 03/2026 | 3,4 | 2,98 | 2,76 | 2,75 | 3,46 | 3,00 | 3,33 | 126 |
| 02/2026 | 2,9 | 2,80 | 2,77 | 2,73 | 2,67 | 2,60 | 2,62 | 126 |
| 01/2026 | 2,9 | 2,93 | 2,79 | 2,82 | 2,75 | 3,06 | 2,98 | 126 |
| 12/2025 | 2,8 | 2,20 | 2,82 | 2,83 | 2,88 | 2,66 | 2,78 | 126 |
| 11/2025 | 2,5 | 2,10 | 2,50 | 2,52 | 2,74 | 2,41 | 2,56 | 120 |
| 10/2025 | 2,3 | 1,81 | 1,99 | 2,01 | 2,08 | 2,16 | 2,03 | 120 |
| 09/2025 | 2,1 | 1,69 | 1,74 | 1,76 | 2,06 | 2,21 | 2,04 | 120 |
| 08/2025 | 1,9 | 1,58 | 1,66 | 1,63 | 1,60 | 1,59 | 1,52 | 120 |
| 07/2025 | 1,9 | 1,76 | 1,76 | 1,72 | 1,85 | 2,49 | 1,92 | 126 |
| 06/2025 | 1,6 | 2,39 | 2,02 | 2,00 | 2,08 | 2,15 | 2,13 | 84 |
| 05/2025 | 1,5 | 3,06 | 2,64 | 2,63 | 2,52 | 1,57 | 1,86 | 84 |
| 04/2025 | 2,8 | 3,52 | 3,38 | 3,35 | 3,35 | 2,32 | 2,63 | 84 |
| 03/2025 | 3,7 | 2,56 | 2,72 | 2,72 | 2,73 | 3,17 | 3,04 | 84 |
| 02/2025 | 2,4 | 2,37 | 2,89 | 2,88 | 2,86 | 2,06 | 2,30 | 90 |
| 01/2025 | 2,2 | 2,63 | 3,03 | 3,02 | 3,12 | 3,14 | 3,13 | 90 |
| 12/2024 | 2,7 | 2,32 | 2,96 | 2,96 | 2,89 | 3,33 | 3,20 | 78 |
| 11/2024 | 2,4 | 2,77 | 2,96 | 2,95 | 3,02 | 3,17 | 3,12 | 72 |
| 10/2024 | 2,7 | 3,34 | 3,20 | 3,20 | 3,21 | 3,24 | 3,23 | 78 |
| 09/2024 | 3,5 | 3,62 | 3,45 | 3,45 | 3,49 | 4,01 | 3,85 | 84 |
| 08/2024 | 4,2 | 2,92 | 2,81 | 2,81 | 2,86 | 4,18 | 3,78 | 84 |
| 07/2024 | 4,0 | 3,26 | 3,22 | 3,22 | 3,28 | 5,10 | 4,55 | 78 |
