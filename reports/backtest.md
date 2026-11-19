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
| jul-24 en adelante | Inicio de mes (solo estadística) | 0,41 | ±0,63 | 1,51 | 28 |
| jul-24 en adelante | Mitad de mes (+ precios hasta el día 15) | 0,39 | ±0,58 | 1,12 | 28 |
| jul-24 en adelante | Día 22 (+ precios hasta el día 22) | 0,38 | ±0,57 | 1,11 | 28 |
| jul-24 en adelante | Fin de mes (+ precios del mes completo) | 0,36 | ±0,59 | 0,99 | 28 |
| jul-24 en adelante | IPC CABA solo | 0,36 | ±0,58 | 1,07 | 28 |
| jul-24 en adelante | Víspera (modelo + IPC CABA) | 0,27 | ±0,52 | 0,82 | 28 |
| 2025-2026 | Inicio de mes (solo estadística) | 0,38 | ±0,46 | 1,51 | 22 |
| 2025-2026 | Mitad de mes (+ precios hasta el día 15) | 0,35 | ±0,48 | 1,12 | 22 |
| 2025-2026 | Día 22 (+ precios hasta el día 22) | 0,34 | ±0,47 | 1,11 | 22 |
| 2025-2026 | Fin de mes (+ precios del mes completo) | 0,31 | ±0,40 | 0,99 | 22 |
| 2025-2026 | IPC CABA solo | 0,30 | ±0,52 | 0,93 | 22 |
| 2025-2026 | Víspera (modelo + IPC CABA) | 0,21 | ±0,33 | 0,82 | 22 |
| últimos 16 meses | Inicio de mes (solo estadística) | 0,24 | ±0,40 | 0,47 | 16 |
| últimos 16 meses | Mitad de mes (+ precios hasta el día 15) | 0,25 | ±0,32 | 0,63 | 16 |
| últimos 16 meses | Día 22 (+ precios hasta el día 22) | 0,24 | ±0,31 | 0,64 | 16 |
| últimos 16 meses | Fin de mes (+ precios del mes completo) | 0,20 | ±0,31 | 0,41 | 16 |
| últimos 16 meses | IPC CABA solo | 0,23 | ±0,30 | 0,82 | 16 |
| últimos 16 meses | Víspera (modelo + IPC CABA) | 0,13 | ±0,18 | 0,36 | 16 |

## Detalle mes a mes

| Mes | INDEC | Inicio de mes | Mitad de mes | Día 22 | Fin de mes | IPC CABA | Víspera | Clases con datos propios |
|---|---|---|---|---|---|---|---|---|
| 10/2026 | 2,2 | 1,94 | 1,99 | 2,05 | 2,13 | 1,92 | 2,03 | 144 |
| 09/2026 | 1,9 | 1,65 | 1,70 | 1,75 | 1,84 | 1,84 | 1,89 | 144 |
| 08/2026 | 1,7 | 2,01 | 1,88 | 1,90 | 1,83 | 1,69 | 1,75 | 144 |
| 07/2026 | 2,1 | 2,12 | 2,12 | 2,11 | 2,08 | 2,93 | 2,12 | 90 |
| 06/2026 | 1,9 | 2,28 | 2,21 | 2,20 | 2,05 | 1,81 | 1,86 | 90 |
| 05/2026 | 2,1 | 2,62 | 1,98 | 1,98 | 1,98 | 2,11 | 2,04 | 90 |
| 04/2026 | 2,6 | 2,99 | 2,74 | 2,74 | 2,59 | 2,48 | 2,61 | 90 |
| 03/2026 | 3,4 | 3,21 | 2,75 | 2,74 | 3,44 | 3,00 | 3,40 | 144 |
| 02/2026 | 2,9 | 2,71 | 2,45 | 2,47 | 2,58 | 2,60 | 2,61 | 144 |
| 01/2026 | 2,9 | 2,70 | 2,62 | 2,64 | 2,47 | 3,06 | 2,73 | 144 |
| 12/2025 | 2,8 | 2,45 | 3,16 | 3,15 | 3,16 | 2,66 | 2,90 | 144 |
| 11/2025 | 2,5 | 2,23 | 2,66 | 2,69 | 2,85 | 2,41 | 2,58 | 138 |
| 10/2025 | 2,3 | 2,02 | 2,08 | 2,10 | 2,11 | 2,16 | 2,07 | 138 |
| 09/2025 | 2,1 | 1,95 | 2,01 | 2,05 | 2,39 | 2,21 | 2,26 | 138 |
| 08/2025 | 1,9 | 1,82 | 1,67 | 1,69 | 1,62 | 1,59 | 1,52 | 138 |
| 07/2025 | 1,9 | 1,82 | 1,49 | 1,51 | 1,68 | 2,49 | 1,73 | 138 |
| 06/2025 | 1,6 | 2,26 | 1,79 | 1,78 | 1,96 | 2,15 | 2,09 | 90 |
| 05/2025 | 1,5 | 3,01 | 2,62 | 2,61 | 2,48 | 1,57 | 1,84 | 90 |
| 04/2025 | 2,8 | 3,53 | 3,39 | 3,37 | 3,41 | 2,32 | 2,64 | 96 |
| 03/2025 | 3,7 | 2,61 | 2,71 | 2,71 | 2,74 | 3,17 | 3,04 | 96 |
| 02/2025 | 2,4 | 2,25 | 2,68 | 2,67 | 2,64 | 2,06 | 2,23 | 96 |
| 01/2025 | 2,2 | 2,43 | 2,70 | 2,70 | 2,78 | 3,14 | 3,03 | 96 |
| 12/2024 | 2,7 | 2,46 | 3,01 | 3,00 | 2,93 | 3,33 | 3,21 | 96 |
| 11/2024 | 2,4 | 2,79 | 2,97 | 2,96 | 3,03 | 3,17 | 3,13 | 96 |
| 10/2024 | 2,7 | 3,43 | 3,32 | 3,31 | 3,33 | 3,24 | 3,27 | 96 |
| 09/2024 | 3,5 | 4,10 | 3,96 | 3,96 | 4,00 | 4,01 | 4,01 | 102 |
| 08/2024 | 4,2 | 3,76 | 3,66 | 3,65 | 3,70 | 4,18 | 4,04 | 102 |
| 07/2024 | 4,0 | 3,29 | 3,25 | 3,25 | 3,31 | 5,10 | 4,56 | 102 |
