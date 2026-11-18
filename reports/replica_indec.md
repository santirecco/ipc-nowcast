# Réplica del IPC de INDEC

*Generado automáticamente el 18/11/2026 con datos hasta octubre 2026.*

## Resultado

Con los pesos calibrados, el modelo reproduce **toda la serie oficial desde dic-2016** con error prácticamente nulo:
el nacional reconstruido desde las 72 celdas región × división difiere del publicado en
**0,0000%** como máximo en nivel, y en
**0** de
118 meses la variación mensual redondeada daría una décima distinta.

Control del último mes: variación nacional reconstruida **2,17%** vs publicada **2,2%**.

Hallazgos sobre cómo agrega INDEC:
- El IPC de cada región es un Laspeyres de sus 12 divisiones (también de Bienes/Servicios y de Estacional/Núcleo/Regulados).
- El nacional es un Laspeyres de los 6 niveles regionales: los pesos regionales **se mueven con los precios relativos**
  (no son fijos sobre las variaciones mensuales).
- Cada división nacional tiene sus propios pesos regionales, distintos del producto peso región × peso división.
- Los pesos publicados (1 decimal) difieren de los exactos en hasta 0,05 pp; por eso calibramos.

## Peso de cada división en el índice nacional

El peso efectivo es el que realmente pondera la variación del mes: el peso base ajustado por cuánto subió cada rubro
respecto del resto desde dic-2016.

| División | Peso dic-16 % | Peso oct-26 % | Cambio pp |
|---|---|---|---|
| Alimentos y bebidas no alcohólicas | 26,94 | 28,78 | 1,84 |
| Transporte | 10,99 | 11,57 | 0,58 |
| Restaurantes y hoteles | 8,99 | 11,02 | 2,03 |
| Vivienda, agua, electricidad, gas y otros combustibles | 9,41 | 10,69 | 1,28 |
| Salud | 8,01 | 9,06 | 1,05 |
| Prendas de vestir y calzado | 9,89 | 6,57 | -3,32 |
| Recreación y cultura | 7,25 | 6,56 | -0,70 |
| Equipamiento y mantenimiento del hogar | 6,36 | 5,06 | -1,30 |
| Bienes y servicios varios | 3,52 | 3,42 | -0,10 |
| Comunicación | 2,82 | 2,64 | -0,18 |
| Bebidas alcohólicas y tabaco | 3,48 | 2,40 | -1,08 |
| Educación | 2,32 | 2,23 | -0,08 |

## Peso de cada región en el índice nacional

| Región | Base calibrada % | Efectivo oct-26 % |
|---|---|---|
| GBA | 45,20 | 45,23 |
| Pampeana | 33,83 | 33,69 |
| Noreste | 4,52 | 4,56 |
| Noroeste | 6,80 | 6,87 |
| Cuyo | 5,14 | 5,17 |
| Patagonia | 4,51 | 4,48 |

## Peso de cada división dentro de su región (oct-26, %)

| División | GBA | Pampeana | Noreste | Noroeste | Cuyo | Patagonia |
|---|---|---|---|---|---|---|
| Alimentos y bebidas no alcohólicas | 25,26 | 30,84 | 36,88 | 35,69 | 30,35 | 28,15 |
| Bebidas alcohólicas y tabaco | 2,28 | 2,63 | 2,49 | 2,03 | 2,33 | 2,48 |
| Prendas de vestir y calzado | 5,77 | 6,94 | 6,96 | 7,77 | 7,17 | 8,80 |
| Vivienda, agua, electricidad, gas y otros combustibles | 10,96 | 9,49 | 13,36 | 10,52 | 11,21 | 13,98 |
| Equipamiento y mantenimiento del hogar | 4,98 | 5,11 | 5,74 | 4,72 | 4,95 | 5,40 |
| Salud | 9,53 | 9,67 | 6,12 | 7,27 | 8,75 | 5,81 |
| Transporte | 11,76 | 11,21 | 10,46 | 8,75 | 13,67 | 15,29 |
| Comunicación | 2,73 | 2,65 | 2,58 | 2,45 | 2,13 | 2,58 |
| Recreación y cultura | 6,95 | 6,69 | 5,18 | 5,14 | 5,63 | 6,16 |
| Educación | 3,03 | 1,37 | 1,25 | 2,43 | 1,77 | 1,92 |
| Restaurantes y hoteles | 13,19 | 10,00 | 5,86 | 10,10 | 8,56 | 6,27 |
| Bienes y servicios varios | 3,55 | 3,37 | 3,12 | 3,12 | 3,49 | 3,17 |

## Precisión de cada réplica

| Réplica | Error máx. en nivel (%) | Error máx. en variación mensual (pp) | Meses con otra décima |
|---|---|---|---|
| GBA: general desde divisiones | 0,0000 | 0,0000 | 0,0000 |
| GBA: general desde categorías | 0,0001 | 0,0001 | 0,0000 |
| Pampeana: general desde divisiones | 0,0001 | 0,0001 | 0,0000 |
| Pampeana: general desde categorías | 0,0001 | 0,0001 | 0,0000 |
| Noreste: general desde divisiones | 0,0000 | 0,0001 | 0,0000 |
| Noreste: general desde categorías | 0,0001 | 0,0001 | 0,0000 |
| Noroeste: general desde divisiones | 0,0000 | 0,0001 | 0,0000 |
| Noroeste: general desde categorías | 0,0001 | 0,0001 | 0,0000 |
| Cuyo: general desde divisiones | 0,0001 | 0,0001 | 0,0000 |
| Cuyo: general desde categorías | 0,0001 | 0,0001 | 0,0000 |
| Patagonia: general desde divisiones | 0,0369 | 0,0377 | 0,0000 |
| Patagonia: general desde categorías | 0,0213 | 0,0216 | 0,0000 |
| Nacional: general desde regiones | 0,0017 | 0,0017 | 0,0000 |
| Nacional: división 01 desde regiones | 0,0001 | 0,0001 | 0,0000 |
| Nacional: división 02 desde regiones | 0,0000 | 0,0001 | 0,0000 |
| Nacional: división 03 desde regiones | 0,0001 | 0,0001 | 0,0000 |
| Nacional: división 04 desde regiones | 0,0001 | 0,0001 | 0,0000 |
| Nacional: división 05 desde regiones | 0,0001 | 0,0001 | 0,0000 |
| Nacional: división 06 desde regiones | 0,0001 | 0,0001 | 0,0000 |
| Nacional: división 07 desde regiones | 0,0001 | 0,0001 | 0,0000 |
| Nacional: división 08 desde regiones | 0,0000 | 0,0001 | 0,0000 |
| Nacional: división 09 desde regiones | 0,0001 | 0,0001 | 0,0000 |
| Nacional: división 10 desde regiones | 0,0001 | 0,0001 | 0,0000 |
| Nacional: división 11 desde regiones | 0,0001 | 0,0001 | 0,0000 |
| Nacional: división 12 desde regiones | 0,0001 | 0,0001 | 0,0000 |
| Nacional: general desde 72 celdas región x división | 0,0000 | 0,0001 | 0,0000 |

## Archivos

- `config/ponderaciones_calibradas.yaml`: pesos exactos.
- `data/processed/pesos_efectivos.csv`: peso de cada región × división, mes a mes.
- `data/processed/incidencias.csv`: aporte de cada región × división a la variación nacional, mes a mes.
