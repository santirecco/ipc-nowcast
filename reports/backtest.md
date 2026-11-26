# Backtest del modelo

*Generado el 26/11/2026.*

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
| jul-24 en adelante | Inicio de mes (solo estadística) | 0,41 | ±0,70 | 1,25 | 28 |
| jul-24 en adelante | Mitad de mes (+ precios hasta el día 15) | 0,36 | ±0,58 | 1,06 | 28 |
| jul-24 en adelante | Día 22 (+ precios hasta el día 22) | 0,35 | ±0,58 | 1,06 | 28 |
| jul-24 en adelante | Fin de mes (+ precios del mes completo) | 0,35 | ±0,70 | 1,12 | 28 |
| jul-24 en adelante | IPC CABA solo | 0,36 | ±0,58 | 1,07 | 28 |
| jul-24 en adelante | Víspera (modelo + IPC CABA) | 0,30 | ±0,56 | 0,91 | 28 |
| 2025-2026 | Inicio de mes (solo estadística) | 0,36 | ±0,47 | 1,25 | 22 |
| 2025-2026 | Mitad de mes (+ precios hasta el día 15) | 0,31 | ±0,57 | 1,06 | 22 |
| 2025-2026 | Día 22 (+ precios hasta el día 22) | 0,30 | ±0,53 | 1,06 | 22 |
| 2025-2026 | Fin de mes (+ precios del mes completo) | 0,30 | ±0,57 | 1,12 | 22 |
| 2025-2026 | IPC CABA solo | 0,30 | ±0,52 | 0,93 | 22 |
| 2025-2026 | Víspera (modelo + IPC CABA) | 0,23 | ±0,40 | 0,88 | 22 |
| últimos 16 meses | Inicio de mes (solo estadística) | 0,24 | ±0,32 | 0,48 | 16 |
| últimos 16 meses | Mitad de mes (+ precios hasta el día 15) | 0,22 | ±0,34 | 0,57 | 16 |
| últimos 16 meses | Día 22 (+ precios hasta el día 22) | 0,19 | ±0,32 | 0,56 | 16 |
| últimos 16 meses | Fin de mes (+ precios del mes completo) | 0,18 | ±0,33 | 0,58 | 16 |
| últimos 16 meses | IPC CABA solo | 0,23 | ±0,30 | 0,82 | 16 |
| últimos 16 meses | Víspera (modelo + IPC CABA) | 0,15 | ±0,19 | 0,52 | 16 |

## Detalle mes a mes

| Mes | INDEC | Inicio de mes | Mitad de mes | Día 22 | Fin de mes | IPC CABA | Víspera | Clases con datos propios |
|---|---|---|---|---|---|---|---|---|
| 10/2026 | 2,2 | 1,94 | 1,95 | 2,01 | 2,12 | 1,92 | 2,04 | 174 |
| 09/2026 | 1,9 | 1,83 | 1,79 | 1,84 | 2,01 | 1,84 | 1,95 | 174 |
| 08/2026 | 1,7 | 1,90 | 1,70 | 1,73 | 1,76 | 1,69 | 1,72 | 174 |
| 07/2026 | 2,1 | 1,85 | 2,01 | 2,01 | 2,16 | 2,93 | 2,22 | 180 |
| 06/2026 | 1,9 | 2,33 | 2,28 | 2,29 | 2,30 | 1,81 | 2,07 | 180 |
| 05/2026 | 2,1 | 2,63 | 2,05 | 2,05 | 2,33 | 2,11 | 2,28 | 180 |
| 04/2026 | 2,6 | 2,43 | 2,57 | 2,57 | 2,74 | 2,48 | 2,64 | 180 |
| 03/2026 | 3,4 | 3,11 | 2,81 | 2,97 | 2,87 | 3,00 | 2,93 | 180 |
| 02/2026 | 2,9 | 2,50 | 2,33 | 2,33 | 2,31 | 2,60 | 2,38 | 180 |
| 01/2026 | 2,9 | 2,61 | 2,58 | 2,62 | 2,87 | 3,06 | 2,96 | 180 |
| 12/2025 | 2,8 | 2,52 | 2,91 | 2,82 | 2,85 | 2,66 | 2,74 | 180 |
| 11/2025 | 2,5 | 2,39 | 2,56 | 2,59 | 2,63 | 2,41 | 2,48 | 180 |
| 10/2025 | 2,3 | 2,07 | 2,16 | 2,19 | 2,29 | 2,16 | 2,24 | 180 |
| 09/2025 | 2,1 | 1,98 | 1,99 | 2,05 | 2,20 | 2,21 | 2,13 | 180 |
| 08/2025 | 1,9 | 1,68 | 1,54 | 1,56 | 1,55 | 1,59 | 1,47 | 180 |
| 07/2025 | 1,9 | 1,85 | 1,66 | 1,68 | 1,77 | 2,49 | 1,86 | 180 |
| 06/2025 | 1,6 | 1,84 | 1,63 | 1,63 | 1,70 | 2,15 | 2,01 | 180 |
| 05/2025 | 1,5 | 2,75 | 2,56 | 2,56 | 2,63 | 1,57 | 1,89 | 180 |
| 04/2025 | 2,8 | 3,54 | 3,57 | 3,57 | 3,56 | 2,32 | 2,69 | 180 |
| 03/2025 | 3,7 | 2,81 | 2,95 | 2,95 | 2,98 | 3,17 | 3,11 | 180 |
| 02/2025 | 2,4 | 2,27 | 2,63 | 2,63 | 2,63 | 2,06 | 2,23 | 180 |
| 01/2025 | 2,2 | 2,88 | 2,79 | 2,79 | 2,97 | 3,14 | 3,09 | 174 |
| 12/2024 | 2,7 | 2,61 | 3,08 | 3,08 | 3,07 | 3,33 | 3,25 | 174 |
| 11/2024 | 2,4 | 3,15 | 3,07 | 3,07 | 3,20 | 3,17 | 3,18 | 168 |
| 10/2024 | 2,7 | 3,84 | 3,47 | 3,47 | 3,49 | 3,24 | 3,31 | 162 |
| 09/2024 | 3,5 | 4,50 | 4,04 | 4,04 | 4,09 | 4,01 | 4,03 | 168 |
| 08/2024 | 4,2 | 4,15 | 3,86 | 3,86 | 4,01 | 4,18 | 4,13 | 168 |
| 07/2024 | 4,0 | 4,62 | 4,53 | 4,53 | 4,58 | 5,10 | 4,94 | 168 |
