# Backtest del modelo

*Generado el 18/11/2026.*

Se simula el pronóstico de cada mes usando solo la información disponible en ese momento:
- **Inicio de mes:** solo la proyección estadística por región y división.
- **Mitad de mes:** además, los precios hasta el día 15: góndolas de todo el país (SEPA, desde septiembre de 2024),
  verduras y frutas mayoristas (Mercado Central, desde 2026), hacienda (desde 2017) y combustibles (precio de YPF;
  a mitad de mes solo el cambio del mes anterior). Cada clase usa solo las fuentes que la mejoraron fuera de muestra
  (ver reports/adelantados.md). En todos los momentos, las prepagas siguen su regla de ajuste (IPC de dos meses antes).
- **Fin de mes:** lo mismo con el mes completo.
- **Víspera:** además, el IPC de la Ciudad de Buenos Aires del mismo mes, que se publica unos días antes que INDEC
  (peso 70% IPC CABA / 30% modelo). En los meses en que la Ciudad
  se desvió de INDEC con el mismo signo todos los años (enero y julio) se corrige el IPC CABA por ese desvío típico.

El calendario de regulados y los supermercados online no tienen historia: su aporte se mide en la prueba en
paralelo de los próximos meses. Los meses sin datos de SEPA (abril a junio de 2026) solo usan la hacienda.

## Error contra el dato de INDEC (nacional, variación mensual)

| Período | Momento | Error promedio (pp) | 80% de los meses dentro de (pp) | Error máximo (pp) | Meses |
|---|---|---|---|---|---|
| jul-24 en adelante | Inicio de mes (solo estadística) | 0,42 | ±0,61 | 1,45 | 28 |
| jul-24 en adelante | Mitad de mes (+ precios hasta el día 15) | 0,37 | ±0,50 | 1,08 | 28 |
| jul-24 en adelante | Fin de mes (+ precios del mes completo) | 0,34 | ±0,56 | 1,02 | 28 |
| jul-24 en adelante | IPC CABA solo | 0,36 | ±0,58 | 1,07 | 28 |
| jul-24 en adelante | Víspera (modelo + IPC CABA) | 0,30 | ±0,49 | 0,88 | 28 |
| 2025-2026 | Inicio de mes (solo estadística) | 0,42 | ±0,57 | 1,45 | 22 |
| 2025-2026 | Mitad de mes (+ precios hasta el día 15) | 0,35 | ±0,42 | 1,07 | 22 |
| 2025-2026 | Fin de mes (+ precios del mes completo) | 0,32 | ±0,53 | 1,02 | 22 |
| 2025-2026 | IPC CABA solo | 0,30 | ±0,52 | 0,93 | 22 |
| 2025-2026 | Víspera (modelo + IPC CABA) | 0,25 | ±0,34 | 0,88 | 22 |
| últimos 16 meses | Inicio de mes (solo estadística) | 0,30 | ±0,44 | 0,62 | 16 |
| últimos 16 meses | Mitad de mes (+ precios hasta el día 15) | 0,24 | ±0,35 | 0,50 | 16 |
| últimos 16 meses | Fin de mes (+ precios del mes completo) | 0,16 | ±0,23 | 0,27 | 16 |
| últimos 16 meses | IPC CABA solo | 0,23 | ±0,30 | 0,82 | 16 |
| últimos 16 meses | Víspera (modelo + IPC CABA) | 0,17 | ±0,26 | 0,39 | 16 |

## Detalle mes a mes

| Mes | INDEC | Inicio de mes | Mitad de mes | Fin de mes | IPC CABA | Víspera | Clases con datos propios |
|---|---|---|---|---|---|---|---|
| 10/2026 | 2,2 | 1,79 | 1,75 | 1,90 | 1,92 | 1,91 | 72 |
| 09/2026 | 1,9 | 1,70 | 1,58 | 1,74 | 1,84 | 1,81 | 72 |
| 08/2026 | 1,7 | 1,79 | 1,84 | 1,78 | 1,69 | 1,72 | 72 |
| 07/2026 | 2,1 | 2,00 | 2,00 | 2,10 | 2,93 | 2,50 | 30 |
| 06/2026 | 1,9 | 2,35 | 2,25 | 2,12 | 1,81 | 1,91 | 24 |
| 05/2026 | 2,1 | 2,59 | 1,89 | 1,89 | 2,11 | 2,04 | 24 |
| 04/2026 | 2,6 | 2,95 | 2,39 | 2,40 | 2,48 | 2,46 | 24 |
| 03/2026 | 3,4 | 3,09 | 2,88 | 3,59 | 3,00 | 3,18 | 72 |
| 02/2026 | 2,9 | 2,70 | 2,71 | 2,82 | 2,60 | 2,67 | 72 |
| 01/2026 | 2,9 | 2,78 | 2,75 | 2,66 | 3,06 | 2,61 | 72 |
| 12/2025 | 2,8 | 2,22 | 2,85 | 2,91 | 2,66 | 2,74 | 72 |
| 11/2025 | 2,5 | 2,07 | 2,52 | 2,74 | 2,41 | 2,51 | 72 |
| 10/2025 | 2,3 | 1,85 | 1,99 | 2,11 | 2,16 | 2,15 | 72 |
| 09/2025 | 2,1 | 1,75 | 1,80 | 2,14 | 2,21 | 2,19 | 72 |
| 08/2025 | 1,9 | 1,65 | 1,66 | 1,69 | 1,59 | 1,62 | 72 |
| 07/2025 | 1,9 | 1,89 | 1,62 | 1,89 | 2,49 | 2,15 | 72 |
| 06/2025 | 1,6 | 2,49 | 2,03 | 2,24 | 2,15 | 2,17 | 72 |
| 05/2025 | 1,5 | 2,95 | 2,47 | 2,52 | 1,57 | 1,86 | 72 |
| 04/2025 | 2,8 | 3,37 | 3,09 | 3,32 | 2,32 | 2,62 | 72 |
| 03/2025 | 3,7 | 2,64 | 2,66 | 2,79 | 3,17 | 3,05 | 72 |
| 02/2025 | 2,4 | 2,40 | 2,80 | 2,87 | 2,06 | 2,30 | 72 |
| 01/2025 | 2,2 | 2,62 | 2,80 | 2,96 | 3,14 | 3,09 | 72 |
| 12/2024 | 2,7 | 2,38 | 2,96 | 2,90 | 3,33 | 3,20 | 24 |
| 11/2024 | 2,4 | 2,84 | 2,92 | 3,01 | 3,17 | 3,12 | 24 |
| 10/2024 | 2,7 | 3,39 | 3,21 | 2,98 | 3,24 | 3,16 | 24 |
| 09/2024 | 3,5 | 3,75 | 3,52 | 3,64 | 4,01 | 3,90 | 24 |
| 08/2024 | 4,2 | 3,32 | 3,09 | 3,15 | 4,18 | 3,87 | 24 |
| 07/2024 | 4,0 | 4,04 | 3,79 | 3,74 | 5,10 | 4,69 | 24 |
