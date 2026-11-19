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
| jul-24 en adelante | Inicio de mes (solo estadística) | 0,57 | ±0,68 | 2,35 | 28 |
| jul-24 en adelante | Mitad de mes (+ precios hasta el día 15) | 0,51 | ±0,66 | 2,45 | 28 |
| jul-24 en adelante | Día 22 (+ precios hasta el día 22) | 0,51 | ±0,66 | 2,45 | 28 |
| jul-24 en adelante | Fin de mes (+ precios del mes completo) | 0,48 | ±0,66 | 2,41 | 28 |
| jul-24 en adelante | IPC CABA solo | 0,36 | ±0,58 | 1,07 | 28 |
| jul-24 en adelante | Víspera (modelo + IPC CABA) | 0,30 | ±0,51 | 0,88 | 28 |
| 2025-2026 | Inicio de mes (solo estadística) | 0,46 | ±0,63 | 1,57 | 22 |
| 2025-2026 | Mitad de mes (+ precios hasta el día 15) | 0,39 | ±0,64 | 1,15 | 22 |
| 2025-2026 | Día 22 (+ precios hasta el día 22) | 0,39 | ±0,65 | 1,14 | 22 |
| 2025-2026 | Fin de mes (+ precios del mes completo) | 0,36 | ±0,61 | 1,11 | 22 |
| 2025-2026 | IPC CABA solo | 0,30 | ±0,52 | 0,93 | 22 |
| 2025-2026 | Víspera (modelo + IPC CABA) | 0,26 | ±0,39 | 0,88 | 22 |
| últimos 16 meses | Inicio de mes (solo estadística) | 0,34 | ±0,51 | 0,64 | 16 |
| últimos 16 meses | Mitad de mes (+ precios hasta el día 15) | 0,26 | ±0,36 | 0,71 | 16 |
| últimos 16 meses | Día 22 (+ precios hasta el día 22) | 0,27 | ±0,36 | 0,69 | 16 |
| últimos 16 meses | Fin de mes (+ precios del mes completo) | 0,22 | ±0,32 | 0,68 | 16 |
| últimos 16 meses | IPC CABA solo | 0,23 | ±0,30 | 0,82 | 16 |
| últimos 16 meses | Víspera (modelo + IPC CABA) | 0,18 | ±0,30 | 0,57 | 16 |

## Detalle mes a mes

| Mes | INDEC | Inicio de mes | Mitad de mes | Día 22 | Fin de mes | IPC CABA | Víspera | Clases con datos propios |
|---|---|---|---|---|---|---|---|---|
| 10/2026 | 2,2 | 1,66 | 1,47 | 1,48 | 1,49 | 1,92 | 1,60 | 138 |
| 09/2026 | 1,9 | 1,38 | 1,45 | 1,31 | 1,30 | 1,84 | 1,53 | 138 |
| 08/2026 | 1,7 | 1,50 | 1,61 | 1,63 | 1,56 | 1,69 | 1,61 | 138 |
| 07/2026 | 2,1 | 1,81 | 1,81 | 1,81 | 1,80 | 2,93 | 2,01 | 96 |
| 06/2026 | 1,9 | 2,15 | 2,05 | 2,05 | 1,92 | 1,81 | 1,76 | 96 |
| 05/2026 | 2,1 | 2,49 | 1,79 | 1,79 | 1,79 | 2,11 | 1,95 | 96 |
| 04/2026 | 2,6 | 2,95 | 2,39 | 2,39 | 2,40 | 2,48 | 2,42 | 96 |
| 03/2026 | 3,4 | 2,95 | 2,73 | 2,72 | 3,43 | 3,00 | 3,33 | 144 |
| 02/2026 | 2,9 | 2,80 | 2,77 | 2,73 | 2,67 | 2,60 | 2,62 | 144 |
| 01/2026 | 2,9 | 2,92 | 2,78 | 2,81 | 2,74 | 3,06 | 2,97 | 144 |
| 12/2025 | 2,8 | 2,20 | 2,82 | 2,84 | 2,88 | 2,66 | 2,77 | 144 |
| 11/2025 | 2,5 | 2,11 | 2,50 | 2,53 | 2,74 | 2,41 | 2,55 | 138 |
| 10/2025 | 2,3 | 1,82 | 2,01 | 2,03 | 2,09 | 2,16 | 2,04 | 138 |
| 09/2025 | 2,1 | 1,69 | 1,74 | 1,77 | 2,07 | 2,21 | 2,06 | 138 |
| 08/2025 | 1,9 | 1,58 | 1,66 | 1,63 | 1,60 | 1,59 | 1,53 | 138 |
| 07/2025 | 1,9 | 1,78 | 1,78 | 1,75 | 1,88 | 2,49 | 1,91 | 144 |
| 06/2025 | 1,6 | 2,43 | 2,06 | 2,04 | 2,13 | 2,15 | 2,14 | 102 |
| 05/2025 | 1,5 | 3,07 | 2,66 | 2,65 | 2,54 | 1,57 | 1,86 | 102 |
| 04/2025 | 2,8 | 3,49 | 3,35 | 3,32 | 3,32 | 2,32 | 2,62 | 102 |
| 03/2025 | 3,7 | 2,44 | 2,60 | 2,60 | 2,61 | 3,17 | 3,00 | 102 |
| 02/2025 | 2,4 | 2,22 | 2,74 | 2,73 | 2,70 | 2,06 | 2,25 | 108 |
| 01/2025 | 2,2 | 2,48 | 2,88 | 2,87 | 2,97 | 3,14 | 3,09 | 108 |
| 12/2024 | 2,7 | 2,15 | 2,80 | 2,79 | 2,73 | 3,33 | 3,15 | 96 |
| 11/2024 | 2,4 | 2,65 | 2,84 | 2,83 | 2,91 | 3,17 | 3,09 | 90 |
| 10/2024 | 2,7 | 3,15 | 3,01 | 3,00 | 3,02 | 3,24 | 3,17 | 96 |
| 09/2024 | 3,5 | 3,15 | 2,98 | 2,98 | 3,02 | 4,01 | 3,71 | 102 |
| 08/2024 | 4,2 | 1,83 | 1,72 | 1,72 | 1,76 | 4,18 | 3,46 | 102 |
| 07/2024 | 4,0 | 2,12 | 2,08 | 2,08 | 2,14 | 5,10 | 4,21 | 96 |
