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
| jul-24 en adelante | Inicio de mes (solo estadística) | 0,45 | ±0,61 | 1,51 | 28 |
| jul-24 en adelante | Mitad de mes (+ precios hasta el día 15) | 0,38 | ±0,65 | 1,03 | 28 |
| jul-24 en adelante | Fin de mes (+ precios del mes completo) | 0,35 | ±0,64 | 0,94 | 28 |
| jul-24 en adelante | IPC CABA solo | 0,36 | ±0,58 | 1,07 | 28 |
| jul-24 en adelante | Víspera (modelo + IPC CABA) | 0,32 | ±0,54 | 0,90 | 28 |
| 2025-2026 | Inicio de mes (solo estadística) | 0,44 | ±0,56 | 1,51 | 22 |
| 2025-2026 | Mitad de mes (+ precios hasta el día 15) | 0,35 | ±0,56 | 1,03 | 22 |
| 2025-2026 | Fin de mes (+ precios del mes completo) | 0,33 | ±0,50 | 0,94 | 22 |
| 2025-2026 | IPC CABA solo | 0,30 | ±0,52 | 0,93 | 22 |
| 2025-2026 | Víspera (modelo + IPC CABA) | 0,26 | ±0,33 | 0,90 | 22 |
| últimos 16 meses | Inicio de mes (solo estadística) | 0,30 | ±0,46 | 0,65 | 16 |
| últimos 16 meses | Mitad de mes (+ precios hasta el día 15) | 0,23 | ±0,32 | 0,55 | 16 |
| últimos 16 meses | Fin de mes (+ precios del mes completo) | 0,18 | ±0,26 | 0,32 | 16 |
| últimos 16 meses | IPC CABA solo | 0,23 | ±0,30 | 0,82 | 16 |
| últimos 16 meses | Víspera (modelo + IPC CABA) | 0,18 | ±0,25 | 0,41 | 16 |

## Detalle mes a mes

| Mes | INDEC | Inicio de mes | Mitad de mes | Fin de mes | IPC CABA | Víspera | Clases con datos propios |
|---|---|---|---|---|---|---|---|
| 10/2026 | 2,2 | 1,84 | 1,79 | 1,92 | 1,92 | 1,92 | 54 |
| 09/2026 | 1,9 | 1,78 | 1,65 | 1,85 | 1,84 | 1,84 | 54 |
| 08/2026 | 1,7 | 1,84 | 1,90 | 1,84 | 1,69 | 1,74 | 54 |
| 07/2026 | 2,1 | 2,08 | 2,08 | 2,17 | 2,93 | 2,52 | 18 |
| 06/2026 | 1,9 | 2,41 | 2,31 | 2,18 | 1,81 | 1,92 | 12 |
| 05/2026 | 2,1 | 2,61 | 1,91 | 1,91 | 2,11 | 2,05 | 12 |
| 04/2026 | 2,6 | 2,88 | 2,32 | 2,33 | 2,48 | 2,44 | 12 |
| 03/2026 | 3,4 | 3,04 | 2,83 | 3,53 | 3,00 | 3,16 | 48 |
| 02/2026 | 2,9 | 2,65 | 2,67 | 2,75 | 2,60 | 2,64 | 48 |
| 01/2026 | 2,9 | 2,72 | 2,70 | 2,56 | 3,06 | 2,58 | 48 |
| 12/2025 | 2,8 | 2,20 | 2,83 | 2,91 | 2,66 | 2,74 | 48 |
| 11/2025 | 2,5 | 2,06 | 2,51 | 2,73 | 2,41 | 2,51 | 48 |
| 10/2025 | 2,3 | 1,88 | 2,02 | 2,07 | 2,16 | 2,13 | 48 |
| 09/2025 | 2,1 | 1,84 | 1,89 | 2,20 | 2,21 | 2,20 | 48 |
| 08/2025 | 1,9 | 1,74 | 1,74 | 1,72 | 1,59 | 1,63 | 48 |
| 07/2025 | 1,9 | 2,03 | 1,76 | 1,93 | 2,49 | 2,16 | 48 |
| 06/2025 | 1,6 | 2,67 | 2,21 | 2,32 | 2,15 | 2,20 | 48 |
| 05/2025 | 1,5 | 3,01 | 2,53 | 2,44 | 1,57 | 1,83 | 48 |
| 04/2025 | 2,8 | 3,35 | 3,07 | 3,10 | 2,32 | 2,55 | 48 |
| 03/2025 | 3,7 | 2,75 | 2,78 | 2,79 | 3,17 | 3,05 | 48 |
| 02/2025 | 2,4 | 2,56 | 2,96 | 2,95 | 2,06 | 2,32 | 48 |
| 01/2025 | 2,2 | 2,76 | 2,94 | 3,05 | 3,14 | 3,11 | 48 |
| 12/2024 | 2,7 | 2,57 | 3,14 | 3,09 | 3,33 | 3,26 | 12 |
| 11/2024 | 2,4 | 3,05 | 3,13 | 3,22 | 3,17 | 3,18 | 12 |
| 10/2024 | 2,7 | 3,56 | 3,38 | 3,15 | 3,24 | 3,21 | 12 |
| 09/2024 | 3,5 | 3,90 | 3,68 | 3,80 | 4,01 | 3,95 | 12 |
| 08/2024 | 4,2 | 3,57 | 3,34 | 3,41 | 4,18 | 3,95 | 12 |
| 07/2024 | 4,0 | 4,36 | 4,11 | 4,06 | 5,10 | 4,79 | 12 |
