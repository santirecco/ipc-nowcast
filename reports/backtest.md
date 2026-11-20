# Backtest del modelo

*Generado el 20/11/2026.*

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
| jul-24 en adelante | Inicio de mes (solo estadística) | 0,38 | ±0,49 | 1,46 | 28 |
| jul-24 en adelante | Mitad de mes (+ precios hasta el día 15) | 0,34 | ±0,51 | 1,08 | 28 |
| jul-24 en adelante | Día 22 (+ precios hasta el día 22) | 0,33 | ±0,52 | 1,07 | 28 |
| jul-24 en adelante | Fin de mes (+ precios del mes completo) | 0,33 | ±0,57 | 0,95 | 28 |
| jul-24 en adelante | IPC CABA solo | 0,36 | ±0,58 | 1,07 | 28 |
| jul-24 en adelante | Víspera (modelo + IPC CABA) | 0,28 | ±0,53 | 0,82 | 28 |
| 2025-2026 | Inicio de mes (solo estadística) | 0,37 | ±0,41 | 1,46 | 22 |
| 2025-2026 | Mitad de mes (+ precios hasta el día 15) | 0,32 | ±0,48 | 1,08 | 22 |
| 2025-2026 | Día 22 (+ precios hasta el día 22) | 0,31 | ±0,47 | 1,07 | 22 |
| 2025-2026 | Fin de mes (+ precios del mes completo) | 0,31 | ±0,44 | 0,95 | 22 |
| 2025-2026 | IPC CABA solo | 0,30 | ±0,52 | 0,93 | 22 |
| 2025-2026 | Víspera (modelo + IPC CABA) | 0,22 | ±0,31 | 0,82 | 22 |
| últimos 16 meses | Inicio de mes (solo estadística) | 0,24 | ±0,36 | 0,41 | 16 |
| últimos 16 meses | Mitad de mes (+ precios hasta el día 15) | 0,22 | ±0,28 | 0,48 | 16 |
| últimos 16 meses | Día 22 (+ precios hasta el día 22) | 0,20 | ±0,26 | 0,52 | 16 |
| últimos 16 meses | Fin de mes (+ precios del mes completo) | 0,20 | ±0,33 | 0,46 | 16 |
| últimos 16 meses | IPC CABA solo | 0,23 | ±0,30 | 0,82 | 16 |
| últimos 16 meses | Víspera (modelo + IPC CABA) | 0,15 | ±0,22 | 0,31 | 16 |

## Detalle mes a mes

| Mes | INDEC | Inicio de mes | Mitad de mes | Día 22 | Fin de mes | IPC CABA | Víspera | Clases con datos propios |
|---|---|---|---|---|---|---|---|---|
| 10/2026 | 2,2 | 1,93 | 2,05 | 2,11 | 2,20 | 1,92 | 2,06 | 156 |
| 09/2026 | 1,9 | 1,78 | 1,83 | 1,89 | 2,07 | 1,84 | 2,03 | 156 |
| 08/2026 | 1,7 | 2,00 | 1,82 | 1,83 | 1,84 | 1,69 | 1,76 | 156 |
| 07/2026 | 2,1 | 2,08 | 2,10 | 2,08 | 2,21 | 2,93 | 2,20 | 114 |
| 06/2026 | 1,9 | 2,29 | 2,16 | 2,15 | 2,22 | 1,81 | 1,96 | 114 |
| 05/2026 | 2,1 | 2,54 | 1,93 | 1,93 | 2,24 | 2,11 | 2,19 | 114 |
| 04/2026 | 2,6 | 2,94 | 2,77 | 2,77 | 2,59 | 2,48 | 2,60 | 114 |
| 03/2026 | 3,4 | 3,20 | 2,90 | 2,86 | 3,56 | 3,00 | 3,50 | 156 |
| 02/2026 | 2,9 | 2,75 | 2,44 | 2,47 | 2,54 | 2,60 | 2,61 | 156 |
| 01/2026 | 2,9 | 2,66 | 2,69 | 2,73 | 2,69 | 3,06 | 3,02 | 156 |
| 12/2025 | 2,8 | 2,44 | 3,03 | 3,05 | 2,92 | 2,66 | 2,78 | 156 |
| 11/2025 | 2,5 | 2,19 | 2,63 | 2,66 | 2,94 | 2,41 | 2,68 | 150 |
| 10/2025 | 2,3 | 1,99 | 2,07 | 2,11 | 2,14 | 2,16 | 2,09 | 150 |
| 09/2025 | 2,1 | 1,93 | 2,02 | 2,04 | 2,43 | 2,21 | 2,30 | 150 |
| 08/2025 | 1,9 | 1,82 | 1,70 | 1,71 | 1,68 | 1,59 | 1,56 | 150 |
| 07/2025 | 1,9 | 1,74 | 1,52 | 1,53 | 1,63 | 2,49 | 1,71 | 144 |
| 06/2025 | 1,6 | 2,17 | 1,71 | 1,70 | 1,88 | 2,15 | 2,07 | 102 |
| 05/2025 | 1,5 | 2,96 | 2,58 | 2,57 | 2,43 | 1,57 | 1,83 | 102 |
| 04/2025 | 2,8 | 3,59 | 3,46 | 3,44 | 3,49 | 2,32 | 2,67 | 108 |
| 03/2025 | 3,7 | 2,64 | 2,75 | 2,75 | 2,78 | 3,17 | 3,05 | 108 |
| 02/2025 | 2,4 | 2,23 | 2,67 | 2,66 | 2,63 | 2,06 | 2,23 | 108 |
| 01/2025 | 2,2 | 2,42 | 2,71 | 2,70 | 2,79 | 3,14 | 3,03 | 108 |
| 12/2024 | 2,7 | 2,43 | 2,99 | 2,98 | 2,91 | 3,33 | 3,20 | 108 |
| 11/2024 | 2,4 | 2,77 | 2,97 | 2,96 | 3,03 | 3,17 | 3,13 | 108 |
| 10/2024 | 2,7 | 3,46 | 3,35 | 3,34 | 3,36 | 3,24 | 3,28 | 108 |
| 09/2024 | 3,5 | 4,17 | 3,99 | 3,99 | 4,03 | 4,01 | 4,02 | 120 |
| 08/2024 | 4,2 | 4,22 | 4,00 | 3,99 | 4,16 | 4,18 | 4,18 | 126 |
| 07/2024 | 4,0 | 3,73 | 3,68 | 3,67 | 3,74 | 5,10 | 4,69 | 126 |
