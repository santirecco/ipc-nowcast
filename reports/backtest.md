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
| jul-24 en adelante | Inicio de mes (solo estadística) | 0,48 | ±0,67 | 1,54 | 28 |
| jul-24 en adelante | Mitad de mes (+ precios hasta el día 15) | 0,41 | ±0,53 | 1,51 | 28 |
| jul-24 en adelante | Fin de mes (+ precios del mes completo) | 0,37 | ±0,46 | 1,44 | 28 |
| jul-24 en adelante | IPC CABA solo | 0,36 | ±0,58 | 1,07 | 28 |
| jul-24 en adelante | Víspera (modelo + IPC CABA) | 0,29 | ±0,44 | 0,85 | 28 |
| 2025-2026 | Inicio de mes (solo estadística) | 0,45 | ±0,58 | 1,54 | 22 |
| 2025-2026 | Mitad de mes (+ precios hasta el día 15) | 0,36 | ±0,48 | 1,17 | 22 |
| 2025-2026 | Fin de mes (+ precios del mes completo) | 0,32 | ±0,40 | 1,16 | 22 |
| 2025-2026 | IPC CABA solo | 0,30 | ±0,52 | 0,93 | 22 |
| 2025-2026 | Víspera (modelo + IPC CABA) | 0,25 | ±0,33 | 0,85 | 22 |
| últimos 16 meses | Inicio de mes (solo estadística) | 0,33 | ±0,46 | 0,59 | 16 |
| últimos 16 meses | Mitad de mes (+ precios hasta el día 15) | 0,26 | ±0,41 | 0,55 | 16 |
| últimos 16 meses | Fin de mes (+ precios del mes completo) | 0,18 | ±0,28 | 0,35 | 16 |
| últimos 16 meses | IPC CABA solo | 0,23 | ±0,30 | 0,82 | 16 |
| últimos 16 meses | Víspera (modelo + IPC CABA) | 0,16 | ±0,25 | 0,36 | 16 |

## Detalle mes a mes

| Mes | INDEC | Inicio de mes | Mitad de mes | Fin de mes | IPC CABA | Víspera | Clases con datos propios |
|---|---|---|---|---|---|---|---|
| 10/2026 | 2,2 | 1,73 | 1,69 | 1,82 | 1,92 | 1,89 | 114 |
| 09/2026 | 1,9 | 1,59 | 1,46 | 1,66 | 1,84 | 1,78 | 114 |
| 08/2026 | 1,7 | 1,74 | 1,81 | 1,75 | 1,69 | 1,71 | 114 |
| 07/2026 | 2,1 | 1,92 | 1,92 | 2,02 | 2,93 | 2,48 | 78 |
| 06/2026 | 1,9 | 2,29 | 2,19 | 2,06 | 1,81 | 1,89 | 72 |
| 05/2026 | 2,1 | 2,61 | 1,91 | 1,91 | 2,11 | 2,05 | 72 |
| 04/2026 | 2,6 | 3,08 | 2,53 | 2,54 | 2,48 | 2,50 | 72 |
| 03/2026 | 3,4 | 3,04 | 2,83 | 3,53 | 3,00 | 3,16 | 108 |
| 02/2026 | 2,9 | 2,80 | 2,81 | 2,89 | 2,60 | 2,69 | 108 |
| 01/2026 | 2,9 | 2,90 | 2,87 | 2,73 | 3,06 | 2,63 | 108 |
| 12/2025 | 2,8 | 2,26 | 2,89 | 2,98 | 2,66 | 2,76 | 108 |
| 11/2025 | 2,5 | 2,08 | 2,52 | 2,75 | 2,41 | 2,51 | 108 |
| 10/2025 | 2,3 | 1,79 | 1,94 | 1,99 | 2,16 | 2,11 | 108 |
| 09/2025 | 2,1 | 1,68 | 1,73 | 2,03 | 2,21 | 2,16 | 108 |
| 08/2025 | 1,9 | 1,58 | 1,58 | 1,55 | 1,59 | 1,58 | 108 |
| 07/2025 | 1,9 | 1,76 | 1,49 | 1,66 | 2,49 | 2,08 | 108 |
| 06/2025 | 1,6 | 2,39 | 1,92 | 2,04 | 2,15 | 2,11 | 108 |
| 05/2025 | 1,5 | 3,04 | 2,56 | 2,47 | 1,57 | 1,84 | 108 |
| 04/2025 | 2,8 | 3,49 | 3,20 | 3,23 | 2,32 | 2,59 | 108 |
| 03/2025 | 3,7 | 2,54 | 2,56 | 2,57 | 3,17 | 2,99 | 108 |
| 02/2025 | 2,4 | 2,35 | 2,75 | 2,73 | 2,06 | 2,26 | 108 |
| 01/2025 | 2,2 | 2,61 | 2,79 | 2,89 | 3,14 | 3,07 | 108 |
| 12/2024 | 2,7 | 2,29 | 2,86 | 2,81 | 3,33 | 3,17 | 72 |
| 11/2024 | 2,4 | 2,74 | 2,82 | 2,90 | 3,17 | 3,09 | 72 |
| 10/2024 | 2,7 | 3,32 | 3,14 | 2,91 | 3,24 | 3,14 | 72 |
| 09/2024 | 3,5 | 3,62 | 3,39 | 3,51 | 4,01 | 3,86 | 72 |
| 08/2024 | 4,2 | 2,90 | 2,67 | 2,73 | 4,18 | 3,75 | 72 |
| 07/2024 | 4,0 | 3,23 | 2,98 | 2,93 | 5,10 | 4,45 | 72 |
