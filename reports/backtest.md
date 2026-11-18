# Backtest del modelo

*Generado el 18/11/2026.*

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
| jul-24 en adelante | Inicio de mes (solo estadística) | 0,42 | ±0,61 | 1,45 | 28 |
| jul-24 en adelante | Mitad de mes (+ precios hasta el día 15) | 0,37 | ±0,50 | 1,08 | 28 |
| jul-24 en adelante | Día 22 (+ precios hasta el día 22) | 0,36 | ±0,51 | 1,10 | 28 |
| jul-24 en adelante | Fin de mes (+ precios del mes completo) | 0,34 | ±0,56 | 1,02 | 28 |
| jul-24 en adelante | IPC CABA solo | 0,36 | ±0,58 | 1,07 | 28 |
| jul-24 en adelante | Víspera (modelo + IPC CABA) | 0,28 | ±0,49 | 0,88 | 28 |
| 2025-2026 | Inicio de mes (solo estadística) | 0,42 | ±0,57 | 1,45 | 22 |
| 2025-2026 | Mitad de mes (+ precios hasta el día 15) | 0,35 | ±0,42 | 1,07 | 22 |
| 2025-2026 | Día 22 (+ precios hasta el día 22) | 0,34 | ±0,51 | 1,10 | 22 |
| 2025-2026 | Fin de mes (+ precios del mes completo) | 0,32 | ±0,53 | 1,02 | 22 |
| 2025-2026 | IPC CABA solo | 0,30 | ±0,52 | 0,93 | 22 |
| 2025-2026 | Víspera (modelo + IPC CABA) | 0,22 | ±0,32 | 0,88 | 22 |
| últimos 16 meses | Inicio de mes (solo estadística) | 0,30 | ±0,44 | 0,63 | 16 |
| últimos 16 meses | Mitad de mes (+ precios hasta el día 15) | 0,24 | ±0,35 | 0,50 | 16 |
| últimos 16 meses | Día 22 (+ precios hasta el día 22) | 0,20 | ±0,30 | 0,51 | 16 |
| últimos 16 meses | Fin de mes (+ precios del mes completo) | 0,16 | ±0,23 | 0,27 | 16 |
| últimos 16 meses | IPC CABA solo | 0,23 | ±0,30 | 0,82 | 16 |
| últimos 16 meses | Víspera (modelo + IPC CABA) | 0,13 | ±0,22 | 0,33 | 16 |

## Detalle mes a mes

| Mes | INDEC | Inicio de mes | Mitad de mes | Día 22 | Fin de mes | IPC CABA | Víspera | Clases con datos propios |
|---|---|---|---|---|---|---|---|---|
| 10/2026 | 2,2 | 1,79 | 1,75 | 1,85 | 1,90 | 1,92 | 1,84 | 72 |
| 09/2026 | 1,9 | 1,71 | 1,58 | 1,74 | 1,74 | 1,84 | 1,82 | 72 |
| 08/2026 | 1,7 | 1,77 | 1,84 | 1,81 | 1,78 | 1,69 | 1,73 | 72 |
| 07/2026 | 2,1 | 2,00 | 2,00 | 2,14 | 2,10 | 2,93 | 2,20 | 30 |
| 06/2026 | 1,9 | 2,35 | 2,25 | 2,25 | 2,12 | 1,81 | 1,88 | 24 |
| 05/2026 | 2,1 | 2,59 | 1,89 | 1,89 | 1,89 | 2,11 | 1,98 | 24 |
| 04/2026 | 2,6 | 2,95 | 2,39 | 2,39 | 2,40 | 2,48 | 2,36 | 24 |
| 03/2026 | 3,4 | 3,08 | 2,88 | 2,88 | 3,59 | 3,00 | 3,41 | 72 |
| 02/2026 | 2,9 | 2,69 | 2,71 | 2,72 | 2,82 | 2,60 | 2,73 | 72 |
| 01/2026 | 2,9 | 2,77 | 2,75 | 2,79 | 2,66 | 3,06 | 2,90 | 72 |
| 12/2025 | 2,8 | 2,22 | 2,85 | 2,85 | 2,91 | 2,66 | 2,77 | 72 |
| 11/2025 | 2,5 | 2,11 | 2,52 | 2,54 | 2,74 | 2,41 | 2,58 | 72 |
| 10/2025 | 2,3 | 1,86 | 1,99 | 2,04 | 2,11 | 2,16 | 2,07 | 72 |
| 09/2025 | 2,1 | 1,76 | 1,80 | 1,85 | 2,14 | 2,21 | 2,10 | 72 |
| 08/2025 | 1,9 | 1,65 | 1,66 | 1,73 | 1,69 | 1,59 | 1,58 | 72 |
| 07/2025 | 1,9 | 1,89 | 1,62 | 1,75 | 1,89 | 2,49 | 1,94 | 72 |
| 06/2025 | 1,6 | 2,49 | 2,03 | 2,12 | 2,24 | 2,15 | 2,17 | 72 |
| 05/2025 | 1,5 | 2,95 | 2,47 | 2,60 | 2,52 | 1,57 | 1,86 | 72 |
| 04/2025 | 2,8 | 3,37 | 3,09 | 3,27 | 3,32 | 2,32 | 2,62 | 72 |
| 03/2025 | 3,7 | 2,64 | 2,66 | 2,78 | 2,79 | 3,17 | 3,05 | 72 |
| 02/2025 | 2,4 | 2,40 | 2,80 | 2,92 | 2,87 | 2,06 | 2,30 | 72 |
| 01/2025 | 2,2 | 2,62 | 2,80 | 2,88 | 2,96 | 3,14 | 3,09 | 72 |
| 12/2024 | 2,7 | 2,38 | 2,96 | 2,96 | 2,90 | 3,33 | 3,20 | 24 |
| 11/2024 | 2,4 | 2,84 | 2,92 | 2,92 | 3,01 | 3,17 | 3,12 | 24 |
| 10/2024 | 2,7 | 3,39 | 3,21 | 3,21 | 2,98 | 3,24 | 3,16 | 24 |
| 09/2024 | 3,5 | 3,75 | 3,52 | 3,52 | 3,64 | 4,01 | 3,90 | 24 |
| 08/2024 | 4,2 | 3,32 | 3,09 | 3,09 | 3,15 | 4,18 | 3,87 | 24 |
| 07/2024 | 4,0 | 4,04 | 3,79 | 3,79 | 3,74 | 5,10 | 4,69 | 24 |
