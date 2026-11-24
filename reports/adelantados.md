# Indicadores adelantados de alimentos

*Generado el 24/11/2026.*

Para cada clase de alimentos se mide si los precios de góndola de todo el país (SEPA), los precios mayoristas
de verduras y frutas (Mercado Central) y el precio de la hacienda (carne) anticipan el dato de INDEC mejor que la
proyección estadística sola. La prueba es **fuera de muestra**: cada mes se predice con coeficientes estimados
solo con los meses anteriores. El error es el promedio, en puntos porcentuales, de la variación mensual de la
clase en las seis regiones. Una fuente se usa en una clase solo si baja el error al menos 0,02 pp.
Si hay varias que sirven, se usa la mejor (comparadas en los mismos meses) y las otras quedan de respaldo para los
meses en que falta algún dato (por ejemplo, SEPA no tiene abril a junio de 2026).

### Mitad de mes (datos hasta el día 15)

| Clase | Fuentes | Meses evaluados | Error solo estadística (pp) | Error con la fuente (pp) | ¿Se usa? |
|---|---|---|---|---|---|
| Pan y cereales | arr | 14 | 0,68 | 0,70 | no |
| Pan y cereales | fx | 34 | 2,17 | 2,35 | no |
| Pan y cereales | propio | 34 | 2,17 | 1,49 | **sí** |
| Pan y cereales | SEPA | 17 | 0,70 | 0,53 | sí, si falta la anterior |
| Pan y cereales | sepa+fx | 17 | 0,70 | 0,53 | sí, si falta la anterior |
| Pan y cereales | sepa+propio | 17 | 0,70 | 0,49 | sí, si falta la anterior |
| Carnes y derivados | arr | 14 | 1,82 | 1,77 | sí, si falta la anterior |
| Carnes y derivados | arrm | 34 | 2,94 | 2,70 | sí, si falta la anterior |
| Carnes y derivados | hacr | 34 | 2,94 | 1,68 | sí, si falta la anterior |
| Carnes y derivados | mayorista | 34 | 2,94 | 2,46 | sí, si falta la anterior |
| Carnes y derivados | may+may2 | 34 | 2,94 | 2,47 | sí, si falta la anterior |
| Carnes y derivados | maya | 34 | 2,94 | 2,55 | sí, si falta la anterior |
| Carnes y derivados | maya+arrm | 34 | 2,94 | 2,52 | sí, si falta la anterior |
| Carnes y derivados | propio | 34 | 2,94 | 2,64 | sí, si falta la anterior |
| Carnes y derivados | SEPA | 17 | 1,92 | 1,92 | no |
| Carnes y derivados | SEPA + mayorista | 17 | 1,92 | 1,87 | sí, si falta la anterior |
| Carnes y derivados | sepa+propio | 17 | 1,92 | 1,71 | sí, si falta la anterior |
| Carnes y derivados | sepa_carne | 18 | 1,90 | 1,95 | no |
| Carnes y derivados | sepa_carne+hacr | 18 | 1,90 | 1,22 | **sí** |
| Carnes y derivados | sepa_carne+hacr+arrm | 18 | 1,90 | 1,15 | sí, si falta la anterior |
| Carnes y derivados | sepa_carne+may | 18 | 1,90 | 1,92 | no |
| Carnes y derivados | sepa_carne+maya | 18 | 1,90 | 1,60 | sí, si falta la anterior |
| Carnes y derivados | sepa_carne+maya+arrm | 18 | 1,90 | 1,28 | sí, si falta la anterior |
| Leche, lácteos y huevos | arr | 14 | 1,15 | 1,17 | no |
| Leche, lácteos y huevos | propio | 34 | 1,96 | 1,52 | sí, si falta la anterior |
| Leche, lácteos y huevos | SEPA | 17 | 1,16 | 0,68 | **sí** |
| Leche, lácteos y huevos | sepa+fx | 17 | 1,16 | 0,68 | sí, si falta la anterior |
| Leche, lácteos y huevos | sepa+propio | 17 | 1,16 | 0,69 | sí, si falta la anterior |
| Aceites, grasas y manteca | arr | 14 | 0,98 | 1,00 | no |
| Aceites, grasas y manteca | fx | 34 | 2,60 | 2,61 | no |
| Aceites, grasas y manteca | propio | 34 | 2,60 | 2,10 | **sí** |
| Aceites, grasas y manteca | SEPA | 17 | 1,02 | 1,03 | no |
| Aceites, grasas y manteca | sepa+fx | 17 | 1,02 | 1,18 | no |
| Aceites, grasas y manteca | sepa+propio | 17 | 1,02 | 0,99 | sí, si falta la anterior |
| Frutas | arr | 14 | 2,63 | 2,70 | no |
| Frutas | arrm | 19 | 2,66 | 2,53 | sí, si falta la anterior |
| Frutas | mayorista | 6 | 3,57 | 3,36 | sí, si falta la anterior |
| Frutas | may+arrm | 6 | 3,57 | 3,24 | sí, si falta la anterior |
| Frutas | propio | 34 | 3,52 | 3,39 | sí, si falta la anterior |
| Frutas | SEPA | 17 | 2,81 | 2,89 | no |
| Frutas | sepa+propio | 17 | 2,81 | 2,83 | no |
| Frutas | sepaf | 18 | 2,82 | 2,54 | sí, si falta la anterior |
| Frutas | sepaf+arrm | 14 | 2,85 | 2,51 | **sí** |
| Frutas | sepaf+may | 2 | 4,16 | 3,41 | no |
| Frutas | sepaf+may+arrm | 2 | 4,16 | 2,92 | no |
| Verduras, tubérculos y legumbres | arr | 14 | 5,71 | 6,14 | no |
| Verduras, tubérculos y legumbres | arrm | 21 | 6,45 | 5,33 | **sí** |
| Verduras, tubérculos y legumbres | mayorista | 6 | 5,69 | 4,14 | sí, si falta la anterior |
| Verduras, tubérculos y legumbres | may+arrm | 6 | 5,69 | 3,92 | sí, si falta la anterior |
| Verduras, tubérculos y legumbres | propio | 34 | 6,84 | 6,51 | sí, si falta la anterior |
| Verduras, tubérculos y legumbres | SEPA | 17 | 6,73 | 6,56 | sí, si falta la anterior |
| Verduras, tubérculos y legumbres | sepa+propio | 17 | 6,73 | 7,30 | no |
| Verduras, tubérculos y legumbres | sepaf | 18 | 6,83 | 5,48 | sí, si falta la anterior |
| Verduras, tubérculos y legumbres | sepaf+arrm | 15 | 5,79 | 5,97 | no |
| Verduras, tubérculos y legumbres | sepaf+may | 2 | 5,91 | 4,79 | no |
| Verduras, tubérculos y legumbres | sepaf+may+arrm | 2 | 5,91 | 14,11 | no |
| Azúcar, dulces y golosinas | arr | 14 | 0,75 | 0,70 | sí, si falta la anterior |
| Azúcar, dulces y golosinas | propio | 34 | 2,31 | 1,80 | sí, si falta la anterior |
| Azúcar, dulces y golosinas | SEPA | 17 | 0,78 | 0,73 | sí, si falta la anterior |
| Azúcar, dulces y golosinas | sepa+fx | 17 | 0,78 | 0,78 | no |
| Azúcar, dulces y golosinas | sepa+propio | 17 | 0,78 | 0,72 | **sí** |
| Café, té, yerba y cacao | arr | 14 | 1,04 | 1,04 | no |
| Café, té, yerba y cacao | fx | 34 | 2,84 | 3,05 | no |
| Café, té, yerba y cacao | propio | 34 | 2,84 | 2,06 | sí, si falta la anterior |
| Café, té, yerba y cacao | SEPA | 17 | 1,03 | 0,81 | sí, si falta la anterior |
| Café, té, yerba y cacao | sepa+fx | 17 | 1,03 | 0,87 | sí, si falta la anterior |
| Café, té, yerba y cacao | sepa+propio | 17 | 1,03 | 0,80 | **sí** |
| Aguas, gaseosas y jugos | arr | 14 | 0,76 | 0,77 | no |
| Aguas, gaseosas y jugos | propio | 34 | 2,19 | 1,83 | sí, si falta la anterior |
| Aguas, gaseosas y jugos | SEPA | 17 | 0,77 | 0,76 | no |
| Aguas, gaseosas y jugos | sepa+fx | 17 | 0,77 | 0,76 | no |
| Aguas, gaseosas y jugos | sepa+propio | 17 | 0,77 | 0,70 | **sí** |
| Bebidas alcohólicas | propio | 34 | 2,10 | 1,59 | sí, si falta la anterior |
| Bebidas alcohólicas | SEPA | 17 | 0,89 | 0,64 | sí, si falta la anterior |
| Bebidas alcohólicas | sepa+propio | 17 | 0,89 | 0,63 | **sí** |
| Tabaco | cal | 24 | 1,67 | 0,72 | sí, si falta la anterior |
| Tabaco | cal+propio | 24 | 1,67 | 0,71 | **sí** |
| Tabaco | ipc | 34 | 2,18 | 1,82 | sí, si falta la anterior |
| Tabaco | propio | 34 | 2,18 | 2,30 | no |
| Ropa | fx | 34 | 2,22 | 2,49 | no |
| Ropa | ipc | 34 | 2,22 | 2,34 | no |
| Ropa | ipcl | 34 | 2,22 | 2,28 | no |
| Ropa | propio | 34 | 2,22 | 1,90 | **sí** |
| Ropa | sal | 34 | 2,22 | 2,35 | no |
| Calzado | fx | 34 | 2,39 | 2,70 | no |
| Calzado | ipc | 34 | 2,39 | 2,31 | sí, si falta la anterior |
| Calzado | ipcl | 34 | 2,39 | 2,51 | no |
| Calzado | propio | 34 | 2,39 | 2,06 | **sí** |
| Calzado | sal | 34 | 2,39 | 2,65 | no |
| Alquiler de la vivienda | icl | 34 | 2,63 | 2,37 | sí, si falta la anterior |
| Alquiler de la vivienda | icl+ipc | 34 | 2,63 | 2,29 | sí, si falta la anterior |
| Alquiler de la vivienda | ipc | 34 | 2,63 | 2,31 | sí, si falta la anterior |
| Alquiler de la vivienda | ipcl | 34 | 2,63 | 2,38 | sí, si falta la anterior |
| Alquiler de la vivienda | ipcl+sal | 34 | 2,63 | 2,22 | sí, si falta la anterior |
| Alquiler de la vivienda | propio | 34 | 2,63 | 2,53 | sí, si falta la anterior |
| Alquiler de la vivienda | sal | 34 | 2,63 | 2,21 | **sí** |
| Electricidad, gas y otros combustibles | ipc | 34 | 6,58 | 4,81 | **sí** |
| Electricidad, gas y otros combustibles | ipc2 | 34 | 6,58 | 5,15 | sí, si falta la anterior |
| Electricidad, gas y otros combustibles | propio | 34 | 6,58 | 6,45 | sí, si falta la anterior |
| Equipamiento del hogar | fx | 34 | 2,13 | 2,37 | no |
| Equipamiento del hogar | propio | 34 | 2,13 | 1,63 | **sí** |
| Equipamiento del hogar | sal | 34 | 2,13 | 2,39 | no |
| Limpieza y mantenimiento del hogar | ipc | 34 | 2,18 | 1,54 | sí, si falta la anterior |
| Limpieza y mantenimiento del hogar | propio | 34 | 2,18 | 2,24 | no |
| Limpieza y mantenimiento del hogar | SEPA | 17 | 0,78 | 0,80 | no |
| Limpieza y mantenimiento del hogar | sepa+propio | 17 | 0,78 | 0,73 | **sí** |
| Muebles, textiles y artefactos del hogar | fx | 34 | 1,94 | 2,73 | no |
| Muebles, textiles y artefactos del hogar | ipc | 34 | 1,94 | 2,15 | no |
| Muebles, textiles y artefactos del hogar | propio | 34 | 1,94 | 1,93 | no |
| Muebles, textiles y artefactos del hogar | sal | 34 | 1,94 | 2,14 | no |
| Medicamentos | ipc | 34 | 2,05 | 1,63 | sí, si falta la anterior |
| Medicamentos | propio | 34 | 2,05 | 1,79 | sí, si falta la anterior |
| Medicamentos | SEPA | 17 | 0,89 | 0,53 | sí, si falta la anterior |
| Medicamentos | sepa+propio | 17 | 0,89 | 0,47 | **sí** |
| Prepagas | ipc | 34 | 3,08 | 2,15 | **sí** |
| Prepagas | ipc2 | 34 | 3,08 | 2,51 | sí, si falta la anterior |
| Prepagas | ipcl | 34 | 3,08 | 2,50 | sí, si falta la anterior |
| Prepagas | propio | 34 | 3,08 | 3,02 | sí, si falta la anterior |
| Otros gastos de salud | ipc | 34 | 2,59 | 2,70 | no |
| Otros gastos de salud | ipcl | 34 | 2,59 | 2,66 | no |
| Otros gastos de salud | propio | 34 | 2,59 | 2,72 | no |
| Otros gastos de salud | sal | 34 | 2,59 | 2,70 | no |
| Compra de vehículos | autos | 17 | 1,63 | 0,82 | **sí** |
| Compra de vehículos | fx | 34 | 2,84 | 3,18 | no |
| Compra de vehículos | propio | 34 | 2,84 | 2,60 | sí, si falta la anterior |
| Combustibles | nafta | 29 | 2,10 | 1,59 | **sí** |
| Combustibles | nafta+fx | 29 | 2,10 | 1,59 | sí, si falta la anterior |
| Combustibles | naftal | 29 | 2,10 | 1,59 | sí, si falta la anterior |
| Transporte público | ipc | 34 | 4,80 | 4,67 | **sí** |
| Transporte público | ipc2 | 34 | 4,80 | 4,70 | sí, si falta la anterior |
| Transporte público | propio | 34 | 4,80 | 5,00 | no |
| Telefonía e internet | fx | 34 | 2,61 | 2,10 | sí, si falta la anterior |
| Telefonía e internet | ipc | 34 | 2,61 | 1,36 | **sí** |
| Telefonía e internet | ipc2 | 34 | 2,61 | 1,83 | sí, si falta la anterior |
| Telefonía e internet | ipcl | 34 | 2,61 | 2,15 | sí, si falta la anterior |
| Telefonía e internet | propio | 34 | 2,61 | 2,27 | sí, si falta la anterior |
| Servicios recreativos y culturales | fx | 34 | 2,87 | 2,85 | no |
| Servicios recreativos y culturales | ipc | 34 | 2,87 | 2,36 | **sí** |
| Servicios recreativos y culturales | ipcl | 34 | 2,87 | 2,70 | sí, si falta la anterior |
| Servicios recreativos y culturales | propio | 34 | 2,87 | 2,74 | sí, si falta la anterior |
| Servicios recreativos y culturales | sal | 34 | 2,87 | 2,71 | sí, si falta la anterior |
| Diarios, libros y papelería | fx | 34 | 1,98 | 2,28 | no |
| Diarios, libros y papelería | ipc | 34 | 1,98 | 1,64 | **sí** |
| Diarios, libros y papelería | ipcl | 34 | 1,98 | 2,04 | no |
| Diarios, libros y papelería | propio | 34 | 1,98 | 1,81 | sí, si falta la anterior |
| Equipos, juguetes y turismo | fx | 34 | 8,80 | 8,66 | **sí** |
| Equipos, juguetes y turismo | ipc | 34 | 8,80 | 8,87 | no |
| Equipos, juguetes y turismo | ipcl | 34 | 8,80 | 8,99 | no |
| Equipos, juguetes y turismo | propio | 34 | 8,80 | 8,94 | no |
| Equipos, juguetes y turismo | sal | 34 | 8,80 | 8,87 | no |
| Educación | ipc | 34 | 3,65 | 3,65 | no |
| Educación | ipcl | 34 | 3,65 | 3,65 | no |
| Educación | propio | 34 | 3,65 | 3,66 | no |
| Educación | sal | 34 | 3,65 | 3,70 | no |
| Restaurantes y comidas fuera del hogar | alim | 17 | 1,04 | 0,88 | sí, si falta la anterior |
| Restaurantes y comidas fuera del hogar | alim1 | 34 | 1,92 | 1,48 | **sí** |
| Restaurantes y comidas fuera del hogar | alim1+sal | 34 | 1,92 | 1,44 | sí, si falta la anterior |
| Restaurantes y comidas fuera del hogar | ipc | 34 | 1,92 | 1,49 | sí, si falta la anterior |
| Restaurantes y comidas fuera del hogar | ipc+sal | 34 | 1,92 | 1,50 | sí, si falta la anterior |
| Restaurantes y comidas fuera del hogar | ipcl | 34 | 1,92 | 2,00 | no |
| Restaurantes y comidas fuera del hogar | propio | 34 | 1,92 | 1,62 | sí, si falta la anterior |
| Restaurantes y comidas fuera del hogar | sal | 34 | 1,92 | 1,93 | no |
| Cuidado personal | ipc | 34 | 2,55 | 1,89 | **sí** |
| Cuidado personal | ipcl | 34 | 2,55 | 2,68 | no |
| Cuidado personal | propio | 34 | 2,55 | 2,97 | no |
| Cuidado personal | sal | 34 | 2,55 | 2,55 | no |
| Cuidado personal | SEPA | 17 | 0,65 | 0,74 | no |
| Cuidado personal | sepa+propio | 17 | 0,65 | 0,70 | no |
| Otros bienes y servicios | fx | 34 | 2,78 | 2,70 | sí, si falta la anterior |
| Otros bienes y servicios | ipc | 34 | 2,78 | 2,03 | **sí** |
| Otros bienes y servicios | propio | 34 | 2,78 | 2,66 | sí, si falta la anterior |
| Otros bienes y servicios | sal | 34 | 2,78 | 2,69 | sí, si falta la anterior |

### Mes completo

| Clase | Fuentes | Meses evaluados | Error solo estadística (pp) | Error con la fuente (pp) | ¿Se usa? |
|---|---|---|---|---|---|
| Pan y cereales | arr | 14 | 0,68 | 0,70 | no |
| Pan y cereales | fx | 34 | 2,17 | 2,30 | no |
| Pan y cereales | propio | 34 | 2,17 | 1,49 | **sí** |
| Pan y cereales | SEPA | 17 | 0,70 | 0,49 | sí, si falta la anterior |
| Pan y cereales | sepa+fx | 17 | 0,70 | 0,49 | sí, si falta la anterior |
| Pan y cereales | sepa+propio | 17 | 0,70 | 0,48 | sí, si falta la anterior |
| Pan y cereales | sepai | 18 | 0,73 | 0,56 | sí, si falta la anterior |
| Pan y cereales | sepai+propio | 18 | 0,73 | 0,51 | sí, si falta la anterior |
| Carnes y derivados | arr | 14 | 1,82 | 1,77 | sí, si falta la anterior |
| Carnes y derivados | arrm | 34 | 2,94 | 2,70 | sí, si falta la anterior |
| Carnes y derivados | hacr | 34 | 2,94 | 1,94 | sí, si falta la anterior |
| Carnes y derivados | mayorista | 34 | 2,94 | 2,50 | sí, si falta la anterior |
| Carnes y derivados | may+may2 | 34 | 2,94 | 2,51 | sí, si falta la anterior |
| Carnes y derivados | maya | 34 | 2,94 | 2,56 | sí, si falta la anterior |
| Carnes y derivados | maya+arrm | 34 | 2,94 | 2,46 | sí, si falta la anterior |
| Carnes y derivados | propio | 34 | 2,94 | 2,64 | sí, si falta la anterior |
| Carnes y derivados | SEPA | 17 | 1,92 | 1,94 | no |
| Carnes y derivados | SEPA + mayorista | 17 | 1,92 | 1,75 | sí, si falta la anterior |
| Carnes y derivados | sepa+propio | 17 | 1,92 | 1,73 | sí, si falta la anterior |
| Carnes y derivados | sepa_carne | 18 | 1,90 | 1,96 | no |
| Carnes y derivados | sepa_carne+hacr | 18 | 1,90 | 1,27 | sí, si falta la anterior |
| Carnes y derivados | sepa_carne+hacr+arrm | 18 | 1,90 | 1,13 | **sí** |
| Carnes y derivados | sepa_carne+may | 18 | 1,90 | 1,80 | sí, si falta la anterior |
| Carnes y derivados | sepa_carne+maya | 18 | 1,90 | 1,58 | sí, si falta la anterior |
| Carnes y derivados | sepa_carne+maya+arrm | 18 | 1,90 | 1,23 | sí, si falta la anterior |
| Leche, lácteos y huevos | arr | 14 | 1,15 | 1,17 | no |
| Leche, lácteos y huevos | propio | 34 | 1,96 | 1,52 | sí, si falta la anterior |
| Leche, lácteos y huevos | SEPA | 17 | 1,16 | 0,73 | sí, si falta la anterior |
| Leche, lácteos y huevos | sepa+fx | 17 | 1,16 | 0,73 | sí, si falta la anterior |
| Leche, lácteos y huevos | sepa+propio | 17 | 1,16 | 0,70 | **sí** |
| Leche, lácteos y huevos | sepai | 18 | 1,18 | 0,84 | sí, si falta la anterior |
| Leche, lácteos y huevos | sepai+propio | 18 | 1,18 | 0,76 | sí, si falta la anterior |
| Aceites, grasas y manteca | arr | 14 | 0,98 | 1,00 | no |
| Aceites, grasas y manteca | fx | 34 | 2,60 | 2,68 | no |
| Aceites, grasas y manteca | propio | 34 | 2,60 | 2,10 | sí, si falta la anterior |
| Aceites, grasas y manteca | SEPA | 17 | 1,02 | 1,02 | no |
| Aceites, grasas y manteca | sepa+fx | 17 | 1,02 | 1,01 | no |
| Aceites, grasas y manteca | sepa+propio | 17 | 1,02 | 0,97 | sí, si falta la anterior |
| Aceites, grasas y manteca | sepai | 18 | 0,99 | 0,77 | **sí** |
| Aceites, grasas y manteca | sepai+propio | 18 | 0,99 | 0,79 | sí, si falta la anterior |
| Frutas | arr | 14 | 2,63 | 2,70 | no |
| Frutas | arrm | 19 | 2,66 | 2,53 | sí, si falta la anterior |
| Frutas | mayorista | 23 | 2,76 | 2,69 | sí, si falta la anterior |
| Frutas | may+arrm | 19 | 2,66 | 2,52 | sí, si falta la anterior |
| Frutas | propio | 34 | 3,52 | 3,39 | sí, si falta la anterior |
| Frutas | SEPA | 17 | 2,81 | 2,86 | no |
| Frutas | sepa+propio | 17 | 2,81 | 2,81 | no |
| Frutas | sepaf | 18 | 2,82 | 2,45 | sí, si falta la anterior |
| Frutas | sepaf+arrm | 14 | 2,85 | 2,48 | **sí** |
| Frutas | sepaf+may | 18 | 2,82 | 2,43 | sí, si falta la anterior |
| Frutas | sepaf+may+arrm | 14 | 2,85 | 2,53 | sí, si falta la anterior |
| Verduras, tubérculos y legumbres | arr | 14 | 5,71 | 6,14 | no |
| Verduras, tubérculos y legumbres | arrm | 21 | 6,45 | 5,33 | sí, si falta la anterior |
| Verduras, tubérculos y legumbres | mayorista | 21 | 6,45 | 5,05 | sí, si falta la anterior |
| Verduras, tubérculos y legumbres | may+arrm | 18 | 5,85 | 5,10 | sí, si falta la anterior |
| Verduras, tubérculos y legumbres | propio | 34 | 6,84 | 6,51 | sí, si falta la anterior |
| Verduras, tubérculos y legumbres | SEPA | 17 | 6,73 | 6,48 | sí, si falta la anterior |
| Verduras, tubérculos y legumbres | sepa+propio | 17 | 6,73 | 7,23 | no |
| Verduras, tubérculos y legumbres | sepaf | 18 | 6,83 | 4,99 | sí, si falta la anterior |
| Verduras, tubérculos y legumbres | sepaf+arrm | 15 | 5,79 | 5,83 | no |
| Verduras, tubérculos y legumbres | sepaf+may | 17 | 6,73 | 4,43 | **sí** |
| Verduras, tubérculos y legumbres | sepaf+may+arrm | 14 | 6,02 | 4,07 | sí, si falta la anterior |
| Azúcar, dulces y golosinas | arr | 14 | 0,75 | 0,70 | sí, si falta la anterior |
| Azúcar, dulces y golosinas | propio | 34 | 2,31 | 1,80 | sí, si falta la anterior |
| Azúcar, dulces y golosinas | SEPA | 17 | 0,78 | 0,65 | sí, si falta la anterior |
| Azúcar, dulces y golosinas | sepa+fx | 17 | 0,78 | 0,71 | sí, si falta la anterior |
| Azúcar, dulces y golosinas | sepa+propio | 17 | 0,78 | 0,65 | **sí** |
| Azúcar, dulces y golosinas | sepai | 18 | 0,79 | 0,77 | sí, si falta la anterior |
| Azúcar, dulces y golosinas | sepai+propio | 18 | 0,79 | 0,75 | sí, si falta la anterior |
| Café, té, yerba y cacao | arr | 14 | 1,04 | 1,04 | no |
| Café, té, yerba y cacao | fx | 34 | 2,84 | 3,07 | no |
| Café, té, yerba y cacao | propio | 34 | 2,84 | 2,06 | sí, si falta la anterior |
| Café, té, yerba y cacao | SEPA | 17 | 1,03 | 0,77 | sí, si falta la anterior |
| Café, té, yerba y cacao | sepa+fx | 17 | 1,03 | 0,80 | sí, si falta la anterior |
| Café, té, yerba y cacao | sepa+propio | 17 | 1,03 | 0,76 | **sí** |
| Café, té, yerba y cacao | sepai | 18 | 1,10 | 0,84 | sí, si falta la anterior |
| Café, té, yerba y cacao | sepai+propio | 18 | 1,10 | 0,76 | sí, si falta la anterior |
| Aguas, gaseosas y jugos | arr | 14 | 0,76 | 0,77 | no |
| Aguas, gaseosas y jugos | propio | 34 | 2,19 | 1,83 | sí, si falta la anterior |
| Aguas, gaseosas y jugos | SEPA | 17 | 0,77 | 0,72 | sí, si falta la anterior |
| Aguas, gaseosas y jugos | sepa+fx | 17 | 0,77 | 0,72 | sí, si falta la anterior |
| Aguas, gaseosas y jugos | sepa+propio | 17 | 0,77 | 0,68 | sí, si falta la anterior |
| Aguas, gaseosas y jugos | sepai | 18 | 0,78 | 0,67 | sí, si falta la anterior |
| Aguas, gaseosas y jugos | sepai+propio | 18 | 0,78 | 0,65 | **sí** |
| Bebidas alcohólicas | propio | 34 | 2,10 | 1,59 | sí, si falta la anterior |
| Bebidas alcohólicas | SEPA | 17 | 0,89 | 0,65 | sí, si falta la anterior |
| Bebidas alcohólicas | sepa+propio | 17 | 0,89 | 0,62 | **sí** |
| Tabaco | cal | 24 | 1,67 | 0,61 | **sí** |
| Tabaco | cal+propio | 24 | 1,67 | 0,63 | sí, si falta la anterior |
| Tabaco | ipc | 34 | 2,18 | 1,82 | sí, si falta la anterior |
| Tabaco | propio | 34 | 2,18 | 2,30 | no |
| Ropa | fx | 34 | 2,22 | 2,48 | no |
| Ropa | ipc | 34 | 2,22 | 2,34 | no |
| Ropa | ipcl | 34 | 2,22 | 2,28 | no |
| Ropa | propio | 34 | 2,22 | 1,90 | **sí** |
| Ropa | sal | 34 | 2,22 | 2,35 | no |
| Calzado | fx | 34 | 2,39 | 2,68 | no |
| Calzado | ipc | 34 | 2,39 | 2,31 | sí, si falta la anterior |
| Calzado | ipcl | 34 | 2,39 | 2,51 | no |
| Calzado | propio | 34 | 2,39 | 2,06 | **sí** |
| Calzado | sal | 34 | 2,39 | 2,65 | no |
| Alquiler de la vivienda | icl | 34 | 2,63 | 2,37 | sí, si falta la anterior |
| Alquiler de la vivienda | icl+ipc | 34 | 2,63 | 2,29 | sí, si falta la anterior |
| Alquiler de la vivienda | ipc | 34 | 2,63 | 2,31 | sí, si falta la anterior |
| Alquiler de la vivienda | ipcl | 34 | 2,63 | 2,38 | sí, si falta la anterior |
| Alquiler de la vivienda | ipcl+sal | 34 | 2,63 | 2,22 | sí, si falta la anterior |
| Alquiler de la vivienda | propio | 34 | 2,63 | 2,53 | sí, si falta la anterior |
| Alquiler de la vivienda | sal | 34 | 2,63 | 2,21 | **sí** |
| Electricidad, gas y otros combustibles | ipc | 34 | 6,58 | 4,81 | **sí** |
| Electricidad, gas y otros combustibles | ipc2 | 34 | 6,58 | 5,15 | sí, si falta la anterior |
| Electricidad, gas y otros combustibles | propio | 34 | 6,58 | 6,45 | sí, si falta la anterior |
| Equipamiento del hogar | fx | 34 | 2,13 | 2,32 | no |
| Equipamiento del hogar | propio | 34 | 2,13 | 1,63 | **sí** |
| Equipamiento del hogar | sal | 34 | 2,13 | 2,39 | no |
| Limpieza y mantenimiento del hogar | ipc | 34 | 2,18 | 1,54 | sí, si falta la anterior |
| Limpieza y mantenimiento del hogar | propio | 34 | 2,18 | 2,24 | no |
| Limpieza y mantenimiento del hogar | SEPA | 17 | 0,78 | 0,77 | no |
| Limpieza y mantenimiento del hogar | sepa+propio | 17 | 0,78 | 0,74 | **sí** |
| Muebles, textiles y artefactos del hogar | fx | 34 | 1,94 | 2,65 | no |
| Muebles, textiles y artefactos del hogar | ipc | 34 | 1,94 | 2,15 | no |
| Muebles, textiles y artefactos del hogar | propio | 34 | 1,94 | 1,93 | no |
| Muebles, textiles y artefactos del hogar | sal | 34 | 1,94 | 2,14 | no |
| Medicamentos | ipc | 34 | 2,05 | 1,63 | sí, si falta la anterior |
| Medicamentos | propio | 34 | 2,05 | 1,79 | sí, si falta la anterior |
| Medicamentos | SEPA | 17 | 0,89 | 0,58 | sí, si falta la anterior |
| Medicamentos | sepa+propio | 17 | 0,89 | 0,50 | **sí** |
| Prepagas | ipc | 34 | 3,08 | 2,15 | **sí** |
| Prepagas | ipc2 | 34 | 3,08 | 2,51 | sí, si falta la anterior |
| Prepagas | ipcl | 34 | 3,08 | 2,50 | sí, si falta la anterior |
| Prepagas | propio | 34 | 3,08 | 3,02 | sí, si falta la anterior |
| Otros gastos de salud | ipc | 34 | 2,59 | 2,70 | no |
| Otros gastos de salud | ipcl | 34 | 2,59 | 2,66 | no |
| Otros gastos de salud | propio | 34 | 2,59 | 2,72 | no |
| Otros gastos de salud | sal | 34 | 2,59 | 2,70 | no |
| Compra de vehículos | autos | 17 | 1,63 | 0,82 | **sí** |
| Compra de vehículos | fx | 34 | 2,84 | 3,13 | no |
| Compra de vehículos | propio | 34 | 2,84 | 2,60 | sí, si falta la anterior |
| Combustibles | nafta | 29 | 2,10 | 1,59 | **sí** |
| Combustibles | nafta+fx | 29 | 2,10 | 1,59 | sí, si falta la anterior |
| Combustibles | naftal | 29 | 2,10 | 1,59 | sí, si falta la anterior |
| Transporte público | ipc | 34 | 4,80 | 4,67 | **sí** |
| Transporte público | ipc2 | 34 | 4,80 | 4,70 | sí, si falta la anterior |
| Transporte público | propio | 34 | 4,80 | 5,00 | no |
| Telefonía e internet | fx | 34 | 2,61 | 2,10 | sí, si falta la anterior |
| Telefonía e internet | ipc | 34 | 2,61 | 1,36 | **sí** |
| Telefonía e internet | ipc2 | 34 | 2,61 | 1,83 | sí, si falta la anterior |
| Telefonía e internet | ipcl | 34 | 2,61 | 2,15 | sí, si falta la anterior |
| Telefonía e internet | propio | 34 | 2,61 | 2,27 | sí, si falta la anterior |
| Servicios recreativos y culturales | fx | 34 | 2,87 | 2,86 | no |
| Servicios recreativos y culturales | ipc | 34 | 2,87 | 2,36 | **sí** |
| Servicios recreativos y culturales | ipcl | 34 | 2,87 | 2,70 | sí, si falta la anterior |
| Servicios recreativos y culturales | propio | 34 | 2,87 | 2,74 | sí, si falta la anterior |
| Servicios recreativos y culturales | sal | 34 | 2,87 | 2,71 | sí, si falta la anterior |
| Diarios, libros y papelería | fx | 34 | 1,98 | 2,26 | no |
| Diarios, libros y papelería | ipc | 34 | 1,98 | 1,64 | **sí** |
| Diarios, libros y papelería | ipcl | 34 | 1,98 | 2,04 | no |
| Diarios, libros y papelería | propio | 34 | 1,98 | 1,81 | sí, si falta la anterior |
| Equipos, juguetes y turismo | fx | 34 | 8,80 | 8,70 | **sí** |
| Equipos, juguetes y turismo | ipc | 34 | 8,80 | 8,87 | no |
| Equipos, juguetes y turismo | ipcl | 34 | 8,80 | 8,99 | no |
| Equipos, juguetes y turismo | propio | 34 | 8,80 | 8,94 | no |
| Equipos, juguetes y turismo | sal | 34 | 8,80 | 8,87 | no |
| Educación | ipc | 34 | 3,65 | 3,65 | no |
| Educación | ipcl | 34 | 3,65 | 3,65 | no |
| Educación | propio | 34 | 3,65 | 3,66 | no |
| Educación | sal | 34 | 3,65 | 3,70 | no |
| Restaurantes y comidas fuera del hogar | alim | 17 | 1,04 | 0,88 | sí, si falta la anterior |
| Restaurantes y comidas fuera del hogar | alim1 | 34 | 1,92 | 1,48 | **sí** |
| Restaurantes y comidas fuera del hogar | alim1+sal | 34 | 1,92 | 1,44 | sí, si falta la anterior |
| Restaurantes y comidas fuera del hogar | ipc | 34 | 1,92 | 1,49 | sí, si falta la anterior |
| Restaurantes y comidas fuera del hogar | ipc+sal | 34 | 1,92 | 1,50 | sí, si falta la anterior |
| Restaurantes y comidas fuera del hogar | ipcl | 34 | 1,92 | 2,00 | no |
| Restaurantes y comidas fuera del hogar | propio | 34 | 1,92 | 1,62 | sí, si falta la anterior |
| Restaurantes y comidas fuera del hogar | sal | 34 | 1,92 | 1,93 | no |
| Cuidado personal | ipc | 34 | 2,55 | 1,89 | **sí** |
| Cuidado personal | ipcl | 34 | 2,55 | 2,68 | no |
| Cuidado personal | propio | 34 | 2,55 | 2,97 | no |
| Cuidado personal | sal | 34 | 2,55 | 2,55 | no |
| Cuidado personal | SEPA | 17 | 0,65 | 0,70 | no |
| Cuidado personal | sepa+propio | 17 | 0,65 | 0,67 | no |
| Otros bienes y servicios | fx | 34 | 2,78 | 2,70 | sí, si falta la anterior |
| Otros bienes y servicios | ipc | 34 | 2,78 | 2,03 | **sí** |
| Otros bienes y servicios | propio | 34 | 2,78 | 2,66 | sí, si falta la anterior |
| Otros bienes y servicios | sal | 34 | 2,78 | 2,69 | sí, si falta la anterior |

