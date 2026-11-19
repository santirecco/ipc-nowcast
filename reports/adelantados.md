# Indicadores adelantados de alimentos

*Generado el 19/11/2026.*

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
| Pan y cereales | arr | 14 | 0,91 | 0,93 | no |
| Pan y cereales | fx | 34 | 2,06 | 2,32 | no |
| Pan y cereales | SEPA | 18 | 0,84 | 0,54 | sí, si falta la anterior |
| Pan y cereales | sepa+fx | 18 | 0,84 | 0,53 | **sí** |
| Carnes y derivados | arr | 14 | 1,67 | 1,63 | **sí** |
| Carnes y derivados | mayorista | 34 | 3,01 | 2,57 | sí, si falta la anterior |
| Carnes y derivados | SEPA | 18 | 1,86 | 1,86 | no |
| Carnes y derivados | SEPA + mayorista | 18 | 1,86 | 1,75 | sí, si falta la anterior |
| Carnes y derivados | sepa_carne | 18 | 1,86 | 1,93 | no |
| Carnes y derivados | sepa_carne+may | 18 | 1,86 | 1,76 | sí, si falta la anterior |
| Leche, lácteos y huevos | arr | 14 | 1,28 | 1,30 | no |
| Leche, lácteos y huevos | SEPA | 18 | 1,21 | 0,65 | **sí** |
| Leche, lácteos y huevos | sepa+fx | 18 | 1,21 | 0,68 | sí, si falta la anterior |
| Aceites, grasas y manteca | arr | 14 | 0,99 | 1,01 | no |
| Aceites, grasas y manteca | fx | 34 | 2,50 | 2,51 | no |
| Aceites, grasas y manteca | SEPA | 18 | 1,05 | 1,06 | no |
| Aceites, grasas y manteca | sepa+fx | 18 | 1,05 | 1,13 | no |
| Frutas | arr | 14 | 2,80 | 2,83 | no |
| Frutas | mayorista | 4 | 4,17 | 4,20 | no |
| Frutas | SEPA | 18 | 2,92 | 2,92 | no |
| Frutas | sepaf | 18 | 2,92 | 2,55 | **sí** |
| Verduras, tubérculos y legumbres | arr | 14 | 5,73 | 6,16 | no |
| Verduras, tubérculos y legumbres | mayorista | 4 | 4,71 | 3,25 | no |
| Verduras, tubérculos y legumbres | SEPA | 18 | 6,78 | 6,62 | sí, si falta la anterior |
| Verduras, tubérculos y legumbres | sepaf | 18 | 6,78 | 5,42 | **sí** |
| Azúcar, dulces y golosinas | arr | 14 | 0,89 | 0,83 | sí, si falta la anterior |
| Azúcar, dulces y golosinas | SEPA | 18 | 0,88 | 0,72 | **sí** |
| Azúcar, dulces y golosinas | sepa+fx | 18 | 0,88 | 0,80 | sí, si falta la anterior |
| Café, té, yerba y cacao | arr | 14 | 1,05 | 1,06 | no |
| Café, té, yerba y cacao | fx | 34 | 2,64 | 2,84 | no |
| Café, té, yerba y cacao | SEPA | 18 | 1,08 | 0,77 | **sí** |
| Café, té, yerba y cacao | sepa+fx | 18 | 1,08 | 0,82 | sí, si falta la anterior |
| Aguas, gaseosas y jugos | arr | 14 | 0,76 | 0,77 | no |
| Aguas, gaseosas y jugos | SEPA | 18 | 0,79 | 0,73 | sí, si falta la anterior |
| Aguas, gaseosas y jugos | sepa+fx | 18 | 0,79 | 0,71 | **sí** |
| Bebidas alcohólicas | SEPA | 18 | 0,99 | 0,67 | **sí** |
| Tabaco | ipc | 34 | 2,16 | 1,85 | **sí** |
| Ropa | fx | 34 | 1,68 | 1,82 | no |
| Ropa | ipc | 34 | 1,68 | 1,92 | no |
| Calzado | ipc | 34 | 2,35 | 2,20 | **sí** |
| Alquiler de la vivienda | icl | 34 | 3,29 | 2,39 | sí, si falta la anterior |
| Alquiler de la vivienda | icl+ipc | 34 | 3,29 | 2,38 | **sí** |
| Alquiler de la vivienda | ipc | 34 | 3,29 | 3,23 | sí, si falta la anterior |
| Alquiler de la vivienda | sal | 34 | 3,29 | 2,40 | sí, si falta la anterior |
| Electricidad, gas y otros combustibles | ipc | 34 | 5,92 | 4,69 | **sí** |
| Electricidad, gas y otros combustibles | ipc2 | 34 | 5,92 | 5,09 | sí, si falta la anterior |
| Equipamiento del hogar | fx | 34 | 2,13 | 2,37 | no |
| Equipamiento del hogar | sal | 34 | 2,13 | 2,39 | no |
| Limpieza y mantenimiento del hogar | ipc | 34 | 2,02 | 1,55 | **sí** |
| Limpieza y mantenimiento del hogar | SEPA | 18 | 0,71 | 0,70 | no |
| Medicamentos | ipc | 34 | 2,05 | 1,81 | sí, si falta la anterior |
| Medicamentos | SEPA | 18 | 0,98 | 0,44 | **sí** |
| Compra de vehículos | autos | 17 | 1,35 | 0,81 | **sí** |
| Compra de vehículos | fx | 34 | 2,54 | 2,87 | no |
| Combustibles | nafta | 29 | 1,97 | 1,82 | **sí** |
| Combustibles | nafta+fx | 29 | 1,97 | 1,82 | sí, si falta la anterior |
| Transporte público | ipc | 34 | 4,75 | 4,62 | **sí** |
| Transporte público | ipc2 | 34 | 4,75 | 4,68 | sí, si falta la anterior |
| Telefonía e internet | ipc | 34 | 1,46 | 1,36 | **sí** |
| Servicios recreativos y culturales | ipc | 34 | 2,93 | 2,37 | **sí** |
| Servicios recreativos y culturales | sal | 34 | 2,93 | 2,71 | sí, si falta la anterior |
| Diarios, libros y papelería | ipc | 34 | 1,68 | 1,60 | **sí** |
| Educación | ipc | 34 | 3,65 | 3,65 | no |
| Educación | sal | 34 | 3,65 | 3,70 | no |
| Restaurantes y comidas fuera del hogar | ipc | 34 | 1,70 | 1,70 | no |
| Restaurantes y comidas fuera del hogar | ipc+sal | 34 | 1,70 | 1,58 | **sí** |
| Restaurantes y comidas fuera del hogar | sal | 34 | 1,70 | 1,71 | no |
| Cuidado personal | ipc | 34 | 2,44 | 1,92 | **sí** |
| Cuidado personal | sal | 34 | 2,44 | 2,44 | no |
| Cuidado personal | SEPA | 18 | 0,66 | 0,67 | no |

### Mes completo

| Clase | Fuentes | Meses evaluados | Error solo estadística (pp) | Error con la fuente (pp) | ¿Se usa? |
|---|---|---|---|---|---|
| Pan y cereales | arr | 14 | 0,91 | 0,93 | no |
| Pan y cereales | fx | 34 | 2,06 | 2,20 | no |
| Pan y cereales | SEPA | 18 | 0,84 | 0,49 | **sí** |
| Pan y cereales | sepa+fx | 18 | 0,84 | 0,49 | sí, si falta la anterior |
| Pan y cereales | sepai | 18 | 0,84 | 0,59 | sí, si falta la anterior |
| Carnes y derivados | arr | 14 | 1,67 | 1,63 | sí, si falta la anterior |
| Carnes y derivados | mayorista | 34 | 3,01 | 2,52 | sí, si falta la anterior |
| Carnes y derivados | SEPA | 18 | 1,86 | 1,92 | no |
| Carnes y derivados | SEPA + mayorista | 18 | 1,86 | 1,69 | **sí** |
| Carnes y derivados | sepa_carne | 18 | 1,86 | 1,97 | no |
| Carnes y derivados | sepa_carne+may | 18 | 1,86 | 1,67 | sí, si falta la anterior |
| Leche, lácteos y huevos | arr | 14 | 1,28 | 1,30 | no |
| Leche, lácteos y huevos | SEPA | 18 | 1,21 | 0,74 | **sí** |
| Leche, lácteos y huevos | sepa+fx | 18 | 1,21 | 0,75 | sí, si falta la anterior |
| Leche, lácteos y huevos | sepai | 18 | 1,21 | 0,86 | sí, si falta la anterior |
| Aceites, grasas y manteca | arr | 14 | 0,99 | 1,01 | no |
| Aceites, grasas y manteca | fx | 34 | 2,50 | 2,48 | no |
| Aceites, grasas y manteca | SEPA | 18 | 1,05 | 1,06 | no |
| Aceites, grasas y manteca | sepa+fx | 18 | 1,05 | 0,97 | sí, si falta la anterior |
| Aceites, grasas y manteca | sepai | 18 | 1,05 | 0,74 | **sí** |
| Frutas | arr | 14 | 2,80 | 2,83 | no |
| Frutas | mayorista | 4 | 4,17 | 4,13 | no |
| Frutas | SEPA | 18 | 2,92 | 2,87 | sí, si falta la anterior |
| Frutas | sepaf | 18 | 2,92 | 2,42 | **sí** |
| Verduras, tubérculos y legumbres | arr | 14 | 5,73 | 6,16 | no |
| Verduras, tubérculos y legumbres | mayorista | 4 | 4,71 | 2,68 | no |
| Verduras, tubérculos y legumbres | SEPA | 18 | 6,78 | 6,57 | sí, si falta la anterior |
| Verduras, tubérculos y legumbres | sepaf | 18 | 6,78 | 4,89 | **sí** |
| Azúcar, dulces y golosinas | arr | 14 | 0,89 | 0,83 | sí, si falta la anterior |
| Azúcar, dulces y golosinas | SEPA | 18 | 0,88 | 0,64 | **sí** |
| Azúcar, dulces y golosinas | sepa+fx | 18 | 0,88 | 0,72 | sí, si falta la anterior |
| Azúcar, dulces y golosinas | sepai | 18 | 0,88 | 0,81 | sí, si falta la anterior |
| Café, té, yerba y cacao | arr | 14 | 1,05 | 1,06 | no |
| Café, té, yerba y cacao | fx | 34 | 2,64 | 2,81 | no |
| Café, té, yerba y cacao | SEPA | 18 | 1,08 | 0,70 | **sí** |
| Café, té, yerba y cacao | sepa+fx | 18 | 1,08 | 0,72 | sí, si falta la anterior |
| Café, té, yerba y cacao | sepai | 18 | 1,08 | 0,83 | sí, si falta la anterior |
| Aguas, gaseosas y jugos | arr | 14 | 0,76 | 0,77 | no |
| Aguas, gaseosas y jugos | SEPA | 18 | 0,79 | 0,67 | sí, si falta la anterior |
| Aguas, gaseosas y jugos | sepa+fx | 18 | 0,79 | 0,67 | sí, si falta la anterior |
| Aguas, gaseosas y jugos | sepai | 18 | 0,79 | 0,66 | **sí** |
| Bebidas alcohólicas | SEPA | 18 | 0,99 | 0,66 | **sí** |
| Tabaco | ipc | 34 | 2,16 | 1,85 | **sí** |
| Ropa | fx | 34 | 1,68 | 1,79 | no |
| Ropa | ipc | 34 | 1,68 | 1,92 | no |
| Calzado | ipc | 34 | 2,35 | 2,20 | **sí** |
| Alquiler de la vivienda | icl | 34 | 3,29 | 2,39 | sí, si falta la anterior |
| Alquiler de la vivienda | icl+ipc | 34 | 3,29 | 2,38 | **sí** |
| Alquiler de la vivienda | ipc | 34 | 3,29 | 3,23 | sí, si falta la anterior |
| Alquiler de la vivienda | sal | 34 | 3,29 | 2,40 | sí, si falta la anterior |
| Electricidad, gas y otros combustibles | ipc | 34 | 5,92 | 4,69 | **sí** |
| Electricidad, gas y otros combustibles | ipc2 | 34 | 5,92 | 5,09 | sí, si falta la anterior |
| Equipamiento del hogar | fx | 34 | 2,13 | 2,32 | no |
| Equipamiento del hogar | sal | 34 | 2,13 | 2,39 | no |
| Limpieza y mantenimiento del hogar | ipc | 34 | 2,02 | 1,55 | sí, si falta la anterior |
| Limpieza y mantenimiento del hogar | SEPA | 18 | 0,71 | 0,68 | **sí** |
| Medicamentos | ipc | 34 | 2,05 | 1,81 | sí, si falta la anterior |
| Medicamentos | SEPA | 18 | 0,98 | 0,50 | **sí** |
| Compra de vehículos | autos | 17 | 1,35 | 0,81 | **sí** |
| Compra de vehículos | fx | 34 | 2,54 | 2,83 | no |
| Combustibles | nafta | 29 | 1,97 | 1,47 | **sí** |
| Combustibles | nafta+fx | 29 | 1,97 | 1,47 | sí, si falta la anterior |
| Transporte público | ipc | 34 | 4,75 | 4,62 | **sí** |
| Transporte público | ipc2 | 34 | 4,75 | 4,68 | sí, si falta la anterior |
| Telefonía e internet | ipc | 34 | 1,46 | 1,36 | **sí** |
| Servicios recreativos y culturales | ipc | 34 | 2,93 | 2,37 | **sí** |
| Servicios recreativos y culturales | sal | 34 | 2,93 | 2,71 | sí, si falta la anterior |
| Diarios, libros y papelería | ipc | 34 | 1,68 | 1,60 | **sí** |
| Educación | ipc | 34 | 3,65 | 3,65 | no |
| Educación | sal | 34 | 3,65 | 3,70 | no |
| Restaurantes y comidas fuera del hogar | ipc | 34 | 1,70 | 1,70 | no |
| Restaurantes y comidas fuera del hogar | ipc+sal | 34 | 1,70 | 1,58 | **sí** |
| Restaurantes y comidas fuera del hogar | sal | 34 | 1,70 | 1,71 | no |
| Cuidado personal | ipc | 34 | 2,44 | 1,92 | **sí** |
| Cuidado personal | sal | 34 | 2,44 | 2,44 | no |
| Cuidado personal | SEPA | 18 | 0,66 | 0,66 | no |

