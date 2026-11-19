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
| jul-24 en adelante | Inicio de mes (solo estadística) | 0,37 | ±0,51 | 1,48 | 28 |
| jul-24 en adelante | Mitad de mes (+ precios hasta el día 15) | 0,34 | ±0,53 | 1,10 | 28 |
| jul-24 en adelante | Día 22 (+ precios hasta el día 22) | 0,33 | ±0,52 | 1,09 | 28 |
| jul-24 en adelante | Fin de mes (+ precios del mes completo) | 0,33 | ±0,59 | 0,95 | 28 |
| jul-24 en adelante | IPC CABA solo | 0,36 | ±0,58 | 1,07 | 28 |
| jul-24 en adelante | Víspera (modelo + IPC CABA) | 0,28 | ±0,53 | 0,83 | 28 |
| 2025-2026 | Inicio de mes (solo estadística) | 0,37 | ±0,43 | 1,48 | 22 |
| 2025-2026 | Mitad de mes (+ precios hasta el día 15) | 0,32 | ±0,44 | 1,10 | 22 |
| 2025-2026 | Día 22 (+ precios hasta el día 22) | 0,31 | ±0,46 | 1,09 | 22 |
| 2025-2026 | Fin de mes (+ precios del mes completo) | 0,31 | ±0,42 | 0,95 | 22 |
| 2025-2026 | IPC CABA solo | 0,30 | ±0,52 | 0,93 | 22 |
| 2025-2026 | Víspera (modelo + IPC CABA) | 0,21 | ±0,31 | 0,83 | 22 |
| últimos 16 meses | Inicio de mes (solo estadística) | 0,23 | ±0,38 | 0,43 | 16 |
| últimos 16 meses | Mitad de mes (+ precios hasta el día 15) | 0,21 | ±0,30 | 0,45 | 16 |
| últimos 16 meses | Día 22 (+ precios hasta el día 22) | 0,20 | ±0,29 | 0,49 | 16 |
| últimos 16 meses | Fin de mes (+ precios del mes completo) | 0,20 | ±0,27 | 0,44 | 16 |
| últimos 16 meses | IPC CABA solo | 0,23 | ±0,30 | 0,82 | 16 |
| últimos 16 meses | Víspera (modelo + IPC CABA) | 0,13 | ±0,21 | 0,33 | 16 |

## Detalle mes a mes

| Mes | INDEC | Inicio de mes | Mitad de mes | Día 22 | Fin de mes | IPC CABA | Víspera | Clases con datos propios |
|---|---|---|---|---|---|---|---|---|
| 10/2026 | 2,2 | 1,95 | 2,07 | 2,13 | 2,15 | 1,92 | 2,04 | 156 |
| 09/2026 | 1,9 | 1,81 | 1,85 | 1,91 | 1,94 | 1,84 | 1,94 | 156 |
| 08/2026 | 1,7 | 2,02 | 1,84 | 1,85 | 1,83 | 1,69 | 1,76 | 156 |
| 07/2026 | 2,1 | 2,10 | 2,12 | 2,10 | 2,08 | 2,93 | 2,13 | 102 |
| 06/2026 | 1,9 | 2,32 | 2,19 | 2,17 | 2,01 | 1,81 | 1,83 | 102 |
| 05/2026 | 2,1 | 2,58 | 1,97 | 1,97 | 1,89 | 2,11 | 1,97 | 102 |
| 04/2026 | 2,6 | 2,98 | 2,81 | 2,82 | 2,58 | 2,48 | 2,60 | 102 |
| 03/2026 | 3,4 | 3,23 | 2,94 | 2,90 | 3,64 | 3,00 | 3,56 | 156 |
| 02/2026 | 2,9 | 2,79 | 2,49 | 2,51 | 2,63 | 2,60 | 2,67 | 156 |
| 01/2026 | 2,9 | 2,70 | 2,73 | 2,76 | 2,53 | 3,06 | 2,93 | 156 |
| 12/2025 | 2,8 | 2,47 | 3,06 | 3,08 | 3,10 | 2,66 | 2,90 | 156 |
| 11/2025 | 2,5 | 2,22 | 2,66 | 2,69 | 2,91 | 2,41 | 2,65 | 150 |
| 10/2025 | 2,3 | 2,01 | 2,09 | 2,13 | 2,14 | 2,16 | 2,09 | 150 |
| 09/2025 | 2,1 | 1,95 | 2,04 | 2,06 | 2,40 | 2,21 | 2,28 | 150 |
| 08/2025 | 1,9 | 1,84 | 1,71 | 1,73 | 1,66 | 1,59 | 1,55 | 150 |
| 07/2025 | 1,9 | 1,76 | 1,54 | 1,56 | 1,65 | 2,49 | 1,72 | 144 |
| 06/2025 | 1,6 | 2,18 | 1,73 | 1,72 | 1,90 | 2,15 | 2,07 | 102 |
| 05/2025 | 1,5 | 2,98 | 2,60 | 2,59 | 2,45 | 1,57 | 1,84 | 102 |
| 04/2025 | 2,8 | 3,62 | 3,49 | 3,47 | 3,52 | 2,32 | 2,68 | 108 |
| 03/2025 | 3,7 | 2,66 | 2,77 | 2,77 | 2,80 | 3,17 | 3,06 | 108 |
| 02/2025 | 2,4 | 2,25 | 2,69 | 2,68 | 2,65 | 2,06 | 2,23 | 108 |
| 01/2025 | 2,2 | 2,44 | 2,72 | 2,71 | 2,80 | 3,14 | 3,04 | 108 |
| 12/2024 | 2,7 | 2,44 | 3,00 | 2,99 | 2,92 | 3,33 | 3,21 | 108 |
| 11/2024 | 2,4 | 2,78 | 2,97 | 2,96 | 3,03 | 3,17 | 3,13 | 108 |
| 10/2024 | 2,7 | 3,46 | 3,34 | 3,34 | 3,36 | 3,24 | 3,27 | 108 |
| 09/2024 | 3,5 | 4,19 | 4,01 | 4,00 | 4,05 | 4,01 | 4,02 | 120 |
| 08/2024 | 4,2 | 4,23 | 4,00 | 3,99 | 4,16 | 4,18 | 4,18 | 126 |
| 07/2024 | 4,0 | 3,75 | 3,68 | 3,68 | 3,74 | 5,10 | 4,69 | 126 |
