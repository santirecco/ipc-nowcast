# Backtest del modelo

*Generado el 18/11/2026.*

Se simula el pronóstico de cada mes usando solo la información disponible en ese momento:
- **Inicio de mes:** solo la proyección estadística por región y división.
- **Mitad de mes:** además, los alimentos con los precios hasta el día 15: góndolas de todo el país (SEPA, desde
  septiembre de 2024), verduras y frutas mayoristas (Mercado Central, desde 2026) y hacienda (desde 2017). Cada clase
  usa solo las fuentes que la mejoraron fuera de muestra (ver reports/adelantados.md).
- **Fin de mes:** lo mismo con el mes completo.
- **Víspera:** además, el IPC de la Ciudad de Buenos Aires del mismo mes, que se publica unos días antes que INDEC
  (peso 70% IPC CABA / 30% modelo). En los meses en que la Ciudad
  se desvió de INDEC con el mismo signo todos los años (enero y julio) se corrige el IPC CABA por ese desvío típico.

El calendario de regulados y los supermercados online no tienen historia: su aporte se mide en la prueba en
paralelo de los próximos meses. Los meses sin datos de SEPA (abril a junio de 2026) solo usan la hacienda.

## Error contra el dato de INDEC (nacional, variación mensual)

| Período | Momento | Error promedio (pp) | 80% de los meses dentro de (pp) | Error máximo (pp) | Meses |
|---|---|---|---|---|---|
| jul-24 en adelante | Inicio de mes (solo estadística) | 0,46 | ±0,68 | 1,48 | 28 |
| jul-24 en adelante | Mitad de mes (+ precios hasta el día 15) | 0,41 | ±0,63 | 1,00 | 28 |
| jul-24 en adelante | Fin de mes (+ precios del mes completo) | 0,41 | ±0,69 | 1,14 | 28 |
| jul-24 en adelante | IPC CABA solo | 0,36 | ±0,58 | 1,07 | 28 |
| jul-24 en adelante | Víspera (modelo + IPC CABA) | 0,34 | ±0,59 | 0,94 | 28 |
| 2025-2026 | Inicio de mes (solo estadística) | 0,44 | ±0,64 | 1,48 | 22 |
| 2025-2026 | Mitad de mes (+ precios hasta el día 15) | 0,37 | ±0,61 | 1,00 | 22 |
| 2025-2026 | Fin de mes (+ precios del mes completo) | 0,36 | ±0,61 | 1,14 | 22 |
| 2025-2026 | IPC CABA solo | 0,30 | ±0,52 | 0,93 | 22 |
| 2025-2026 | Víspera (modelo + IPC CABA) | 0,27 | ±0,43 | 0,94 | 22 |
| últimos 16 meses | Inicio de mes (solo estadística) | 0,30 | ±0,43 | 0,66 | 16 |
| últimos 16 meses | Mitad de mes (+ precios hasta el día 15) | 0,24 | ±0,37 | 0,57 | 16 |
| últimos 16 meses | Fin de mes (+ precios del mes completo) | 0,20 | ±0,28 | 0,59 | 16 |
| últimos 16 meses | IPC CABA solo | 0,23 | ±0,30 | 0,82 | 16 |
| últimos 16 meses | Víspera (modelo + IPC CABA) | 0,19 | ±0,25 | 0,45 | 16 |

## Detalle mes a mes

| Mes | INDEC | Inicio de mes | Mitad de mes | Fin de mes | IPC CABA | Víspera | Clases con datos propios |
|---|---|---|---|---|---|---|---|
| 10/2026 | 2,2 | 1,87 | 1,81 | 1,93 | 1,92 | 1,92 | 48 |
| 09/2026 | 1,9 | 1,80 | 1,69 | 1,88 | 1,84 | 1,85 | 48 |
| 08/2026 | 1,7 | 1,87 | 1,96 | 1,93 | 1,69 | 1,76 | 48 |
| 07/2026 | 2,1 | 2,10 | 2,12 | 2,26 | 2,93 | 2,55 | 12 |
| 06/2026 | 1,9 | 2,41 | 2,35 | 2,30 | 1,81 | 1,96 | 6 |
| 05/2026 | 2,1 | 2,58 | 1,95 | 2,02 | 2,11 | 2,08 | 6 |
| 04/2026 | 2,6 | 2,86 | 2,16 | 2,26 | 2,48 | 2,42 | 6 |
| 03/2026 | 3,4 | 3,02 | 2,81 | 2,79 | 3,00 | 2,94 | 42 |
| 02/2026 | 2,9 | 2,63 | 2,68 | 2,76 | 2,60 | 2,65 | 42 |
| 01/2026 | 2,9 | 2,71 | 2,66 | 2,75 | 3,06 | 2,63 | 42 |
| 12/2025 | 2,8 | 2,19 | 2,80 | 2,77 | 2,66 | 2,70 | 42 |
| 11/2025 | 2,5 | 2,06 | 2,51 | 2,59 | 2,41 | 2,47 | 42 |
| 10/2025 | 2,3 | 1,89 | 2,00 | 2,06 | 2,16 | 2,13 | 42 |
| 09/2025 | 2,1 | 1,85 | 1,90 | 1,97 | 2,21 | 2,14 | 42 |
| 08/2025 | 1,9 | 1,77 | 1,75 | 1,75 | 1,59 | 1,64 | 42 |
| 07/2025 | 1,9 | 2,07 | 1,81 | 1,84 | 2,49 | 2,13 | 42 |
| 06/2025 | 1,6 | 2,67 | 2,24 | 2,36 | 2,15 | 2,21 | 42 |
| 05/2025 | 1,5 | 2,98 | 2,50 | 2,64 | 1,57 | 1,89 | 42 |
| 04/2025 | 2,8 | 3,38 | 3,11 | 3,14 | 2,32 | 2,56 | 42 |
| 03/2025 | 3,7 | 2,81 | 2,84 | 2,87 | 3,17 | 3,08 | 42 |
| 02/2025 | 2,4 | 2,63 | 3,03 | 3,02 | 2,06 | 2,34 | 42 |
| 01/2025 | 2,2 | 2,86 | 3,04 | 3,19 | 3,14 | 3,15 | 42 |
| 12/2024 | 2,7 | 2,67 | 3,25 | 3,19 | 3,33 | 3,29 | 6 |
| 11/2024 | 2,4 | 3,12 | 3,23 | 3,32 | 3,17 | 3,21 | 6 |
| 10/2024 | 2,7 | 3,61 | 3,41 | 3,42 | 3,24 | 3,29 | 6 |
| 09/2024 | 3,5 | 3,99 | 3,76 | 3,80 | 4,01 | 3,95 | 6 |
| 08/2024 | 4,2 | 3,80 | 3,58 | 3,62 | 4,18 | 4,02 | 6 |
| 07/2024 | 4,0 | 4,78 | 4,55 | 4,61 | 5,10 | 4,95 | 6 |
