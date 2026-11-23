# Backtest del modelo

*Generado el 23/11/2026.*

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
| jul-24 en adelante | Inicio de mes (solo estadística) | 0,36 | ±0,61 | 1,40 | 28 |
| jul-24 en adelante | Mitad de mes (+ precios hasta el día 15) | 0,34 | ±0,43 | 1,36 | 28 |
| jul-24 en adelante | Día 22 (+ precios hasta el día 22) | 0,32 | ±0,39 | 1,35 | 28 |
| jul-24 en adelante | Fin de mes (+ precios del mes completo) | 0,33 | ±0,44 | 1,17 | 28 |
| jul-24 en adelante | IPC CABA solo | 0,36 | ±0,58 | 1,07 | 28 |
| jul-24 en adelante | Víspera (modelo + IPC CABA) | 0,28 | ±0,51 | 0,82 | 28 |
| 2025-2026 | Inicio de mes (solo estadística) | 0,34 | ±0,56 | 1,40 | 22 |
| 2025-2026 | Mitad de mes (+ precios hasta el día 15) | 0,35 | ±0,43 | 1,36 | 22 |
| 2025-2026 | Día 22 (+ precios hasta el día 22) | 0,33 | ±0,40 | 1,35 | 22 |
| 2025-2026 | Fin de mes (+ precios del mes completo) | 0,34 | ±0,45 | 1,17 | 22 |
| 2025-2026 | IPC CABA solo | 0,30 | ±0,52 | 0,93 | 22 |
| 2025-2026 | Víspera (modelo + IPC CABA) | 0,22 | ±0,33 | 0,82 | 22 |
| últimos 16 meses | Inicio de mes (solo estadística) | 0,20 | ±0,29 | 0,57 | 16 |
| últimos 16 meses | Mitad de mes (+ precios hasta el día 15) | 0,22 | ±0,30 | 0,45 | 16 |
| últimos 16 meses | Día 22 (+ precios hasta el día 22) | 0,19 | ±0,29 | 0,42 | 16 |
| últimos 16 meses | Fin de mes (+ precios del mes completo) | 0,20 | ±0,32 | 0,37 | 16 |
| últimos 16 meses | IPC CABA solo | 0,23 | ±0,30 | 0,82 | 16 |
| últimos 16 meses | Víspera (modelo + IPC CABA) | 0,15 | ±0,23 | 0,34 | 16 |

## Detalle mes a mes

| Mes | INDEC | Inicio de mes | Mitad de mes | Día 22 | Fin de mes | IPC CABA | Víspera | Clases con datos propios |
|---|---|---|---|---|---|---|---|---|
| 10/2026 | 2,2 | 1,95 | 1,89 | 1,95 | 2,05 | 1,92 | 1,97 | 156 |
| 09/2026 | 1,9 | 1,75 | 1,68 | 1,74 | 1,93 | 1,84 | 1,94 | 156 |
| 08/2026 | 1,7 | 2,02 | 1,81 | 1,83 | 1,85 | 1,69 | 1,77 | 156 |
| 07/2026 | 2,1 | 2,01 | 2,08 | 2,07 | 2,20 | 2,93 | 2,18 | 114 |
| 06/2026 | 1,9 | 2,45 | 2,19 | 2,17 | 2,26 | 1,81 | 1,99 | 114 |
| 05/2026 | 2,1 | 2,68 | 2,07 | 2,07 | 2,42 | 2,11 | 2,31 | 114 |
| 04/2026 | 2,6 | 2,75 | 2,89 | 2,90 | 2,76 | 2,48 | 2,72 | 114 |
| 03/2026 | 3,4 | 3,44 | 2,93 | 3,08 | 3,75 | 3,00 | 3,62 | 156 |
| 02/2026 | 2,9 | 2,81 | 2,47 | 2,48 | 2,54 | 2,60 | 2,61 | 156 |
| 01/2026 | 2,9 | 2,80 | 2,64 | 2,68 | 2,66 | 3,06 | 3,00 | 156 |
| 12/2025 | 2,8 | 2,70 | 3,12 | 3,03 | 2,96 | 2,66 | 2,80 | 156 |
| 11/2025 | 2,5 | 2,32 | 2,43 | 2,47 | 2,71 | 2,41 | 2,55 | 150 |
| 10/2025 | 2,3 | 2,05 | 2,12 | 2,16 | 2,17 | 2,16 | 2,11 | 150 |
| 09/2025 | 2,1 | 1,93 | 1,98 | 2,01 | 2,39 | 2,21 | 2,28 | 150 |
| 08/2025 | 1,9 | 1,82 | 1,65 | 1,66 | 1,63 | 1,59 | 1,54 | 150 |
| 07/2025 | 1,9 | 1,88 | 1,71 | 1,72 | 1,91 | 2,49 | 1,89 | 144 |
| 06/2025 | 1,6 | 2,26 | 1,95 | 1,95 | 2,09 | 2,15 | 2,13 | 102 |
| 05/2025 | 1,5 | 2,90 | 2,86 | 2,85 | 2,67 | 1,57 | 1,90 | 102 |
| 04/2025 | 2,8 | 3,65 | 3,72 | 3,70 | 3,71 | 2,32 | 2,73 | 108 |
| 03/2025 | 3,7 | 2,64 | 2,97 | 2,96 | 2,98 | 3,17 | 3,11 | 108 |
| 02/2025 | 2,4 | 2,23 | 2,71 | 2,71 | 2,71 | 2,06 | 2,25 | 108 |
| 01/2025 | 2,2 | 2,42 | 2,65 | 2,64 | 2,78 | 3,14 | 3,03 | 108 |
| 12/2024 | 2,7 | 2,43 | 2,87 | 2,87 | 2,85 | 3,33 | 3,18 | 108 |
| 11/2024 | 2,4 | 2,77 | 2,71 | 2,70 | 2,83 | 3,17 | 3,07 | 108 |
| 10/2024 | 2,7 | 3,46 | 3,23 | 3,23 | 3,24 | 3,24 | 3,24 | 108 |
| 09/2024 | 3,5 | 4,17 | 3,82 | 3,81 | 3,86 | 4,01 | 3,97 | 120 |
| 08/2024 | 4,2 | 4,22 | 4,00 | 4,00 | 4,16 | 4,18 | 4,18 | 126 |
| 07/2024 | 4,0 | 3,73 | 3,79 | 3,78 | 3,83 | 5,10 | 4,72 | 126 |
