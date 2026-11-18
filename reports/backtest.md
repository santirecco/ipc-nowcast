# Backtest del modelo

*Generado el 18/11/2026.*

Se simula el pronóstico de cada mes usando solo la información disponible en ese momento:
- **Inicio de mes:** solo la proyección estadística por región y división (sin calendario de regulados ni supermercados,
  que no tienen historia).
- **Víspera:** además, el IPC de la Ciudad de Buenos Aires del mismo mes, que se publica unos días antes que INDEC
  (peso 70% IPC CABA / 30% modelo).

Los componentes nuevos (calendario de regulados y supermercados online) no se pueden simular hacia atrás:
su aporte se va a medir en la prueba en paralelo de los próximos meses.

## Error contra el dato de INDEC (nacional, variación mensual)

| Período | Momento | Error promedio (pp) | 80% de los meses dentro de (pp) | Error máximo (pp) | Meses |
|---|---|---|---|---|---|
| jul-24 en adelante | Inicio de mes (solo modelo) | 0,46 | ±0,68 | 1,48 | 28 |
| jul-24 en adelante | IPC CABA solo | 0,36 | ±0,58 | 1,07 | 28 |
| jul-24 en adelante | Víspera (modelo + IPC CABA) | 0,35 | ±0,62 | 0,97 | 28 |
| 2025-2026 | Inicio de mes (solo modelo) | 0,44 | ±0,64 | 1,48 | 22 |
| 2025-2026 | IPC CABA solo | 0,30 | ±0,52 | 0,93 | 22 |
| 2025-2026 | Víspera (modelo + IPC CABA) | 0,29 | ±0,49 | 0,84 | 22 |
| últimos 16 meses | Inicio de mes (solo modelo) | 0,30 | ±0,43 | 0,66 | 16 |
| últimos 16 meses | IPC CABA solo | 0,23 | ±0,30 | 0,82 | 16 |
| últimos 16 meses | Víspera (modelo + IPC CABA) | 0,22 | ±0,32 | 0,57 | 16 |

## Detalle mes a mes

| Mes | INDEC | Inicio de mes | IPC CABA | Víspera |
|---|---|---|---|---|
| 10/2026 | 2,2 | 1,87 | 1,92 | 1,90 |
| 09/2026 | 1,9 | 1,80 | 1,84 | 1,83 |
| 08/2026 | 1,7 | 1,87 | 1,69 | 1,75 |
| 07/2026 | 2,1 | 2,10 | 2,93 | 2,68 |
| 06/2026 | 1,9 | 2,41 | 1,81 | 1,99 |
| 05/2026 | 2,1 | 2,58 | 2,11 | 2,25 |
| 04/2026 | 2,6 | 2,86 | 2,48 | 2,60 |
| 03/2026 | 3,4 | 3,02 | 3,00 | 3,00 |
| 02/2026 | 2,9 | 2,63 | 2,60 | 2,61 |
| 01/2026 | 2,9 | 2,71 | 3,06 | 2,95 |
| 12/2025 | 2,8 | 2,19 | 2,66 | 2,52 |
| 11/2025 | 2,5 | 2,06 | 2,41 | 2,31 |
| 10/2025 | 2,3 | 1,89 | 2,16 | 2,08 |
| 09/2025 | 2,1 | 1,85 | 2,21 | 2,10 |
| 08/2025 | 1,9 | 1,77 | 1,59 | 1,64 |
| 07/2025 | 1,9 | 2,07 | 2,49 | 2,36 |
| 06/2025 | 1,6 | 2,67 | 2,15 | 2,30 |
| 05/2025 | 1,5 | 2,98 | 1,57 | 1,99 |
| 04/2025 | 2,8 | 3,38 | 2,32 | 2,64 |
| 03/2025 | 3,7 | 2,81 | 3,17 | 3,06 |
| 02/2025 | 2,4 | 2,63 | 2,06 | 2,23 |
| 01/2025 | 2,2 | 2,86 | 3,14 | 3,06 |
| 12/2024 | 2,7 | 2,67 | 3,33 | 3,13 |
| 11/2024 | 2,4 | 3,12 | 3,17 | 3,15 |
| 10/2024 | 2,7 | 3,61 | 3,24 | 3,35 |
| 09/2024 | 3,5 | 3,99 | 4,01 | 4,00 |
| 08/2024 | 4,2 | 3,80 | 4,18 | 4,07 |
| 07/2024 | 4,0 | 4,78 | 5,10 | 5,00 |
