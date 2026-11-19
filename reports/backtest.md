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
| jul-24 en adelante | Inicio de mes (solo estadística) | 0,38 | ±0,51 | 1,48 | 28 |
| jul-24 en adelante | Mitad de mes (+ precios hasta el día 15) | 0,37 | ±0,53 | 1,09 | 28 |
| jul-24 en adelante | Día 22 (+ precios hasta el día 22) | 0,36 | ±0,52 | 1,08 | 28 |
| jul-24 en adelante | Fin de mes (+ precios del mes completo) | 0,34 | ±0,56 | 0,95 | 28 |
| jul-24 en adelante | IPC CABA solo | 0,36 | ±0,58 | 1,07 | 28 |
| jul-24 en adelante | Víspera (modelo + IPC CABA) | 0,27 | ±0,52 | 0,83 | 28 |
| 2025-2026 | Inicio de mes (solo estadística) | 0,37 | ±0,43 | 1,48 | 22 |
| 2025-2026 | Mitad de mes (+ precios hasta el día 15) | 0,35 | ±0,50 | 1,09 | 22 |
| 2025-2026 | Día 22 (+ precios hasta el día 22) | 0,34 | ±0,49 | 1,08 | 22 |
| 2025-2026 | Fin de mes (+ precios del mes completo) | 0,31 | ±0,40 | 0,95 | 22 |
| 2025-2026 | IPC CABA solo | 0,30 | ±0,52 | 0,93 | 22 |
| 2025-2026 | Víspera (modelo + IPC CABA) | 0,21 | ±0,32 | 0,83 | 22 |
| últimos 16 meses | Inicio de mes (solo estadística) | 0,24 | ±0,38 | 0,43 | 16 |
| últimos 16 meses | Mitad de mes (+ precios hasta el día 15) | 0,25 | ±0,35 | 0,61 | 16 |
| últimos 16 meses | Día 22 (+ precios hasta el día 22) | 0,24 | ±0,34 | 0,63 | 16 |
| últimos 16 meses | Fin de mes (+ precios del mes completo) | 0,20 | ±0,31 | 0,41 | 16 |
| últimos 16 meses | IPC CABA solo | 0,23 | ±0,30 | 0,82 | 16 |
| últimos 16 meses | Víspera (modelo + IPC CABA) | 0,12 | ±0,20 | 0,34 | 16 |

## Detalle mes a mes

| Mes | INDEC | Inicio de mes | Mitad de mes | Día 22 | Fin de mes | IPC CABA | Víspera | Clases con datos propios |
|---|---|---|---|---|---|---|---|---|
| 10/2026 | 2,2 | 1,95 | 2,00 | 2,06 | 2,14 | 1,92 | 2,03 | 144 |
| 09/2026 | 1,9 | 1,65 | 1,71 | 1,76 | 1,85 | 1,84 | 1,89 | 144 |
| 08/2026 | 1,7 | 2,01 | 1,88 | 1,91 | 1,84 | 1,69 | 1,75 | 144 |
| 07/2026 | 2,1 | 2,11 | 2,11 | 2,10 | 2,08 | 2,93 | 2,12 | 90 |
| 06/2026 | 1,9 | 2,32 | 2,24 | 2,23 | 2,09 | 1,81 | 1,88 | 90 |
| 05/2026 | 2,1 | 2,58 | 1,94 | 1,94 | 1,94 | 2,11 | 2,00 | 90 |
| 04/2026 | 2,6 | 2,98 | 2,73 | 2,73 | 2,58 | 2,48 | 2,60 | 90 |
| 03/2026 | 3,4 | 3,23 | 2,77 | 2,75 | 3,45 | 3,00 | 3,40 | 144 |
| 02/2026 | 2,9 | 2,79 | 2,54 | 2,56 | 2,66 | 2,60 | 2,67 | 144 |
| 01/2026 | 2,9 | 2,71 | 2,62 | 2,65 | 2,48 | 3,06 | 2,74 | 144 |
| 12/2025 | 2,8 | 2,46 | 3,17 | 3,17 | 3,17 | 2,66 | 2,91 | 144 |
| 11/2025 | 2,5 | 2,22 | 2,65 | 2,68 | 2,84 | 2,41 | 2,57 | 138 |
| 10/2025 | 2,3 | 2,00 | 2,06 | 2,08 | 2,09 | 2,16 | 2,05 | 138 |
| 09/2025 | 2,1 | 1,94 | 2,01 | 2,05 | 2,38 | 2,21 | 2,25 | 138 |
| 08/2025 | 1,9 | 1,84 | 1,69 | 1,71 | 1,64 | 1,59 | 1,53 | 138 |
| 07/2025 | 1,9 | 1,76 | 1,43 | 1,45 | 1,62 | 2,49 | 1,70 | 138 |
| 06/2025 | 1,6 | 2,18 | 1,71 | 1,71 | 1,89 | 2,15 | 2,07 | 90 |
| 05/2025 | 1,5 | 2,98 | 2,59 | 2,58 | 2,45 | 1,57 | 1,83 | 90 |
| 04/2025 | 2,8 | 3,62 | 3,47 | 3,46 | 3,50 | 2,32 | 2,67 | 96 |
| 03/2025 | 3,7 | 2,66 | 2,76 | 2,76 | 2,79 | 3,17 | 3,05 | 96 |
| 02/2025 | 2,4 | 2,25 | 2,68 | 2,68 | 2,64 | 2,06 | 2,23 | 96 |
| 01/2025 | 2,2 | 2,45 | 2,72 | 2,71 | 2,80 | 3,14 | 3,04 | 96 |
| 12/2024 | 2,7 | 2,45 | 2,99 | 2,99 | 2,92 | 3,33 | 3,21 | 96 |
| 11/2024 | 2,4 | 2,79 | 2,97 | 2,96 | 3,03 | 3,17 | 3,13 | 96 |
| 10/2024 | 2,7 | 3,46 | 3,34 | 3,34 | 3,35 | 3,24 | 3,27 | 96 |
| 09/2024 | 3,5 | 4,09 | 3,96 | 3,95 | 4,00 | 4,01 | 4,01 | 102 |
| 08/2024 | 4,2 | 4,02 | 3,92 | 3,91 | 3,96 | 4,18 | 4,12 | 108 |
| 07/2024 | 4,0 | 3,62 | 3,58 | 3,58 | 3,64 | 5,10 | 4,66 | 108 |
