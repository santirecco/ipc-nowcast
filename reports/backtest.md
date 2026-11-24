# Backtest del modelo

*Generado el 24/11/2026.*

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
| jul-24 en adelante | Inicio de mes (solo estadística) | 0,41 | ±0,68 | 1,27 | 28 |
| jul-24 en adelante | Mitad de mes (+ precios hasta el día 15) | 0,37 | ±0,60 | 1,08 | 28 |
| jul-24 en adelante | Día 22 (+ precios hasta el día 22) | 0,35 | ±0,57 | 1,08 | 28 |
| jul-24 en adelante | Fin de mes (+ precios del mes completo) | 0,36 | ±0,69 | 1,15 | 28 |
| jul-24 en adelante | IPC CABA solo | 0,36 | ±0,58 | 1,07 | 28 |
| jul-24 en adelante | Víspera (modelo + IPC CABA) | 0,31 | ±0,56 | 0,91 | 28 |
| 2025-2026 | Inicio de mes (solo estadística) | 0,36 | ±0,47 | 1,27 | 22 |
| 2025-2026 | Mitad de mes (+ precios hasta el día 15) | 0,33 | ±0,57 | 1,08 | 22 |
| 2025-2026 | Día 22 (+ precios hasta el día 22) | 0,31 | ±0,53 | 1,08 | 22 |
| 2025-2026 | Fin de mes (+ precios del mes completo) | 0,31 | ±0,56 | 1,15 | 22 |
| 2025-2026 | IPC CABA solo | 0,30 | ±0,52 | 0,93 | 22 |
| 2025-2026 | Víspera (modelo + IPC CABA) | 0,23 | ±0,42 | 0,88 | 22 |
| últimos 16 meses | Inicio de mes (solo estadística) | 0,25 | ±0,34 | 0,48 | 16 |
| últimos 16 meses | Mitad de mes (+ precios hasta el día 15) | 0,23 | ±0,38 | 0,63 | 16 |
| últimos 16 meses | Día 22 (+ precios hasta el día 22) | 0,21 | ±0,36 | 0,54 | 16 |
| últimos 16 meses | Fin de mes (+ precios del mes completo) | 0,19 | ±0,37 | 0,56 | 16 |
| últimos 16 meses | IPC CABA solo | 0,23 | ±0,30 | 0,82 | 16 |
| últimos 16 meses | Víspera (modelo + IPC CABA) | 0,16 | ±0,25 | 0,50 | 16 |

## Detalle mes a mes

| Mes | INDEC | Inicio de mes | Mitad de mes | Día 22 | Fin de mes | IPC CABA | Víspera | Clases con datos propios |
|---|---|---|---|---|---|---|---|---|
| 10/2026 | 2,2 | 1,84 | 1,83 | 1,89 | 1,99 | 1,92 | 1,92 | 174 |
| 09/2026 | 1,9 | 1,83 | 1,78 | 1,83 | 2,00 | 1,84 | 1,95 | 174 |
| 08/2026 | 1,7 | 1,89 | 1,66 | 1,70 | 1,73 | 1,69 | 1,69 | 174 |
| 07/2026 | 2,1 | 1,85 | 1,97 | 1,96 | 2,11 | 2,93 | 2,18 | 180 |
| 06/2026 | 1,9 | 2,34 | 2,27 | 2,28 | 2,29 | 1,81 | 2,07 | 180 |
| 05/2026 | 2,1 | 2,63 | 2,08 | 2,07 | 2,36 | 2,11 | 2,29 | 180 |
| 04/2026 | 2,6 | 2,54 | 2,68 | 2,68 | 2,85 | 2,48 | 2,75 | 180 |
| 03/2026 | 3,4 | 3,11 | 2,76 | 2,91 | 2,82 | 3,00 | 2,92 | 180 |
| 02/2026 | 2,9 | 2,50 | 2,35 | 2,36 | 2,34 | 2,60 | 2,39 | 180 |
| 01/2026 | 2,9 | 2,60 | 2,54 | 2,58 | 2,83 | 3,06 | 2,93 | 180 |
| 12/2025 | 2,8 | 2,51 | 2,90 | 2,81 | 2,83 | 2,66 | 2,72 | 180 |
| 11/2025 | 2,5 | 2,36 | 2,51 | 2,54 | 2,58 | 2,41 | 2,44 | 180 |
| 10/2025 | 2,3 | 2,05 | 2,15 | 2,18 | 2,27 | 2,16 | 2,22 | 180 |
| 09/2025 | 2,1 | 1,95 | 1,96 | 2,01 | 2,16 | 2,21 | 2,10 | 180 |
| 08/2025 | 1,9 | 1,68 | 1,50 | 1,52 | 1,51 | 1,59 | 1,45 | 180 |
| 07/2025 | 1,9 | 1,89 | 1,70 | 1,72 | 1,80 | 2,49 | 1,89 | 180 |
| 06/2025 | 1,6 | 1,87 | 1,64 | 1,64 | 1,71 | 2,15 | 2,02 | 180 |
| 05/2025 | 1,5 | 2,77 | 2,58 | 2,58 | 2,65 | 1,57 | 1,89 | 180 |
| 04/2025 | 2,8 | 3,55 | 3,58 | 3,58 | 3,57 | 2,32 | 2,69 | 180 |
| 03/2025 | 3,7 | 2,82 | 2,96 | 2,96 | 2,99 | 3,17 | 3,11 | 180 |
| 02/2025 | 2,4 | 2,26 | 2,63 | 2,63 | 2,62 | 2,06 | 2,23 | 180 |
| 01/2025 | 2,2 | 2,87 | 2,78 | 2,78 | 2,97 | 3,14 | 3,09 | 174 |
| 12/2024 | 2,7 | 2,60 | 3,06 | 3,06 | 3,05 | 3,33 | 3,25 | 174 |
| 11/2024 | 2,4 | 3,12 | 3,04 | 3,04 | 3,17 | 3,17 | 3,17 | 168 |
| 10/2024 | 2,7 | 3,79 | 3,43 | 3,43 | 3,44 | 3,24 | 3,30 | 162 |
| 09/2024 | 3,5 | 4,50 | 4,04 | 4,04 | 4,09 | 4,01 | 4,03 | 168 |
| 08/2024 | 4,2 | 4,15 | 3,86 | 3,86 | 4,01 | 4,18 | 4,13 | 168 |
| 07/2024 | 4,0 | 4,62 | 4,53 | 4,53 | 4,58 | 5,10 | 4,94 | 168 |
