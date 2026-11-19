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
| Pan y cereales | arr | 14 | 0,68 | 0,70 | no |
| Pan y cereales | fx | 34 | 2,17 | 2,35 | no |
| Pan y cereales | SEPA | 18 | 0,73 | 0,53 | **sí** |
| Pan y cereales | sepa+fx | 18 | 0,73 | 0,53 | sí, si falta la anterior |
| Carnes y derivados | arr | 14 | 1,82 | 1,71 | sí, si falta la anterior |
| Carnes y derivados | mayorista | 34 | 2,94 | 2,46 | sí, si falta la anterior |
| Carnes y derivados | may+may2 | 34 | 2,94 | 2,47 | sí, si falta la anterior |
| Carnes y derivados | maya | 34 | 2,94 | 2,55 | sí, si falta la anterior |
| Carnes y derivados | SEPA | 18 | 1,90 | 1,90 | no |
| Carnes y derivados | SEPA + mayorista | 18 | 1,90 | 1,93 | no |
| Carnes y derivados | sepa_carne | 18 | 1,90 | 1,95 | no |
| Carnes y derivados | sepa_carne+may | 18 | 1,90 | 1,92 | no |
| Carnes y derivados | sepa_carne+maya | 18 | 1,90 | 1,60 | **sí** |
| Leche, lácteos y huevos | arr | 14 | 1,15 | 1,17 | no |
| Leche, lácteos y huevos | SEPA | 18 | 1,18 | 0,65 | **sí** |
| Leche, lácteos y huevos | sepa+fx | 18 | 1,18 | 0,65 | sí, si falta la anterior |
| Aceites, grasas y manteca | arr | 14 | 0,98 | 1,00 | no |
| Aceites, grasas y manteca | fx | 34 | 2,60 | 2,61 | no |
| Aceites, grasas y manteca | SEPA | 18 | 0,99 | 1,03 | no |
| Aceites, grasas y manteca | sepa+fx | 18 | 0,99 | 1,14 | no |
| Frutas | arr | 14 | 2,63 | 2,70 | no |
| Frutas | mayorista | 4 | 4,07 | 4,17 | no |
| Frutas | SEPA | 18 | 2,82 | 2,85 | no |
| Frutas | sepaf | 18 | 2,82 | 2,50 | **sí** |
| Verduras, tubérculos y legumbres | arr | 14 | 5,71 | 6,13 | no |
| Verduras, tubérculos y legumbres | mayorista | 4 | 4,76 | 3,28 | no |
| Verduras, tubérculos y legumbres | SEPA | 18 | 6,83 | 6,56 | sí, si falta la anterior |
| Verduras, tubérculos y legumbres | sepaf | 18 | 6,83 | 5,42 | **sí** |
| Azúcar, dulces y golosinas | arr | 14 | 0,75 | 0,70 | sí, si falta la anterior |
| Azúcar, dulces y golosinas | SEPA | 18 | 0,79 | 0,72 | **sí** |
| Azúcar, dulces y golosinas | sepa+fx | 18 | 0,79 | 0,77 | no |
| Café, té, yerba y cacao | arr | 14 | 1,04 | 1,03 | no |
| Café, té, yerba y cacao | fx | 34 | 2,84 | 3,05 | no |
| Café, té, yerba y cacao | SEPA | 18 | 1,10 | 0,78 | **sí** |
| Café, té, yerba y cacao | sepa+fx | 18 | 1,10 | 0,86 | sí, si falta la anterior |
| Aguas, gaseosas y jugos | arr | 14 | 0,76 | 0,77 | no |
| Aguas, gaseosas y jugos | SEPA | 18 | 0,78 | 0,72 | **sí** |
| Aguas, gaseosas y jugos | sepa+fx | 18 | 0,78 | 0,72 | sí, si falta la anterior |
| Bebidas alcohólicas | SEPA | 18 | 0,90 | 0,67 | **sí** |
| Tabaco | ipc | 34 | 2,18 | 1,82 | **sí** |
| Ropa | fx | 34 | 2,22 | 2,49 | no |
| Ropa | ipc | 34 | 2,22 | 2,34 | no |
| Ropa | ipcl | 34 | 2,22 | 2,28 | no |
| Ropa | sal | 34 | 2,22 | 2,35 | no |
| Calzado | fx | 34 | 2,39 | 2,70 | no |
| Calzado | ipc | 34 | 2,39 | 2,31 | no |
| Calzado | ipcl | 34 | 2,39 | 2,51 | no |
| Calzado | sal | 34 | 2,39 | 2,65 | no |
| Alquiler de la vivienda | icl | 34 | 2,63 | 2,37 | sí, si falta la anterior |
| Alquiler de la vivienda | icl+ipc | 34 | 2,63 | 2,29 | **sí** |
| Alquiler de la vivienda | ipc | 34 | 2,63 | 2,31 | sí, si falta la anterior |
| Alquiler de la vivienda | ipcl | 34 | 2,63 | 2,38 | sí, si falta la anterior |
| Alquiler de la vivienda | ipcl+sal | 34 | 2,63 | 2,22 | sí, si falta la anterior |
| Alquiler de la vivienda | sal | 34 | 2,63 | 2,21 | sí, si falta la anterior |
| Electricidad, gas y otros combustibles | ipc | 34 | 6,58 | 4,81 | **sí** |
| Electricidad, gas y otros combustibles | ipc2 | 34 | 6,58 | 5,15 | sí, si falta la anterior |
| Equipamiento del hogar | fx | 34 | 2,13 | 2,37 | no |
| Equipamiento del hogar | sal | 34 | 2,13 | 2,39 | no |
| Limpieza y mantenimiento del hogar | ipc | 34 | 2,18 | 1,54 | **sí** |
| Limpieza y mantenimiento del hogar | SEPA | 18 | 0,76 | 0,78 | no |
| Medicamentos | ipc | 34 | 2,05 | 1,63 | sí, si falta la anterior |
| Medicamentos | SEPA | 18 | 0,92 | 0,47 | **sí** |
| Compra de vehículos | autos | 17 | 1,63 | 0,82 | **sí** |
| Compra de vehículos | fx | 34 | 2,84 | 3,18 | no |
| Combustibles | nafta | 29 | 2,10 | 1,59 | **sí** |
| Combustibles | nafta+fx | 29 | 2,10 | 1,59 | sí, si falta la anterior |
| Combustibles | naftal | 29 | 2,10 | 1,59 | sí, si falta la anterior |
| Transporte público | ipc | 34 | 4,80 | 4,67 | sí, si falta la anterior |
| Transporte público | ipc2 | 34 | 4,80 | 4,70 | **sí** |
| Telefonía e internet | fx | 34 | 2,61 | 2,10 | sí, si falta la anterior |
| Telefonía e internet | ipc | 34 | 2,61 | 1,36 | **sí** |
| Telefonía e internet | ipc2 | 34 | 2,61 | 1,83 | sí, si falta la anterior |
| Telefonía e internet | ipcl | 34 | 2,61 | 2,15 | sí, si falta la anterior |
| Servicios recreativos y culturales | fx | 34 | 2,87 | 2,85 | sí, si falta la anterior |
| Servicios recreativos y culturales | ipc | 34 | 2,87 | 2,36 | **sí** |
| Servicios recreativos y culturales | ipcl | 34 | 2,87 | 2,70 | sí, si falta la anterior |
| Servicios recreativos y culturales | sal | 34 | 2,87 | 2,71 | sí, si falta la anterior |
| Diarios, libros y papelería | fx | 34 | 1,98 | 2,28 | no |
| Diarios, libros y papelería | ipc | 34 | 1,98 | 1,64 | **sí** |
| Diarios, libros y papelería | ipcl | 34 | 1,98 | 2,04 | no |
| Educación | ipc | 34 | 3,65 | 3,65 | no |
| Educación | ipcl | 34 | 3,65 | 3,65 | no |
| Educación | sal | 34 | 3,65 | 3,70 | no |
| Restaurantes y comidas fuera del hogar | alim | 18 | 1,01 | 0,91 | sí, si falta la anterior |
| Restaurantes y comidas fuera del hogar | alim1 | 34 | 1,92 | 1,48 | **sí** |
| Restaurantes y comidas fuera del hogar | alim1+sal | 34 | 1,92 | 1,44 | sí, si falta la anterior |
| Restaurantes y comidas fuera del hogar | ipc | 34 | 1,92 | 1,49 | sí, si falta la anterior |
| Restaurantes y comidas fuera del hogar | ipc+sal | 34 | 1,92 | 1,50 | sí, si falta la anterior |
| Restaurantes y comidas fuera del hogar | ipcl | 34 | 1,92 | 2,00 | no |
| Restaurantes y comidas fuera del hogar | sal | 34 | 1,92 | 1,93 | no |
| Cuidado personal | ipc | 34 | 2,55 | 1,89 | **sí** |
| Cuidado personal | ipcl | 34 | 2,55 | 2,68 | no |
| Cuidado personal | sal | 34 | 2,55 | 2,55 | no |
| Cuidado personal | SEPA | 18 | 0,70 | 0,71 | no |

### Mes completo

| Clase | Fuentes | Meses evaluados | Error solo estadística (pp) | Error con la fuente (pp) | ¿Se usa? |
|---|---|---|---|---|---|
| Pan y cereales | arr | 14 | 0,68 | 0,70 | no |
| Pan y cereales | fx | 34 | 2,17 | 2,30 | no |
| Pan y cereales | SEPA | 18 | 0,73 | 0,49 | **sí** |
| Pan y cereales | sepa+fx | 18 | 0,73 | 0,49 | sí, si falta la anterior |
| Pan y cereales | sepai | 18 | 0,73 | 0,56 | sí, si falta la anterior |
| Carnes y derivados | arr | 14 | 1,82 | 1,71 | sí, si falta la anterior |
| Carnes y derivados | mayorista | 34 | 2,94 | 2,50 | sí, si falta la anterior |
| Carnes y derivados | may+may2 | 34 | 2,94 | 2,51 | sí, si falta la anterior |
| Carnes y derivados | maya | 34 | 2,94 | 2,56 | sí, si falta la anterior |
| Carnes y derivados | SEPA | 18 | 1,90 | 1,91 | no |
| Carnes y derivados | SEPA + mayorista | 18 | 1,90 | 1,84 | sí, si falta la anterior |
| Carnes y derivados | sepa_carne | 18 | 1,90 | 1,96 | no |
| Carnes y derivados | sepa_carne+may | 18 | 1,90 | 1,79 | sí, si falta la anterior |
| Carnes y derivados | sepa_carne+maya | 18 | 1,90 | 1,56 | **sí** |
| Leche, lácteos y huevos | arr | 14 | 1,15 | 1,17 | no |
| Leche, lácteos y huevos | SEPA | 18 | 1,18 | 0,75 | **sí** |
| Leche, lácteos y huevos | sepa+fx | 18 | 1,18 | 0,75 | sí, si falta la anterior |
| Leche, lácteos y huevos | sepai | 18 | 1,18 | 0,87 | sí, si falta la anterior |
| Aceites, grasas y manteca | arr | 14 | 0,98 | 1,00 | no |
| Aceites, grasas y manteca | fx | 34 | 2,60 | 2,68 | no |
| Aceites, grasas y manteca | SEPA | 18 | 0,99 | 1,02 | no |
| Aceites, grasas y manteca | sepa+fx | 18 | 0,99 | 0,99 | no |
| Aceites, grasas y manteca | sepai | 18 | 0,99 | 0,76 | **sí** |
| Frutas | arr | 14 | 2,63 | 2,70 | no |
| Frutas | mayorista | 4 | 4,07 | 4,10 | no |
| Frutas | SEPA | 18 | 2,82 | 2,82 | sí, si falta la anterior |
| Frutas | sepaf | 18 | 2,82 | 2,40 | **sí** |
| Verduras, tubérculos y legumbres | arr | 14 | 5,71 | 6,13 | no |
| Verduras, tubérculos y legumbres | mayorista | 4 | 4,76 | 2,74 | no |
| Verduras, tubérculos y legumbres | SEPA | 18 | 6,83 | 6,51 | sí, si falta la anterior |
| Verduras, tubérculos y legumbres | sepaf | 18 | 6,83 | 4,90 | **sí** |
| Azúcar, dulces y golosinas | arr | 14 | 0,75 | 0,70 | sí, si falta la anterior |
| Azúcar, dulces y golosinas | SEPA | 18 | 0,79 | 0,65 | **sí** |
| Azúcar, dulces y golosinas | sepa+fx | 18 | 0,79 | 0,70 | sí, si falta la anterior |
| Azúcar, dulces y golosinas | sepai | 18 | 0,79 | 0,77 | sí, si falta la anterior |
| Café, té, yerba y cacao | arr | 14 | 1,04 | 1,03 | no |
| Café, té, yerba y cacao | fx | 34 | 2,84 | 3,07 | no |
| Café, té, yerba y cacao | SEPA | 18 | 1,10 | 0,70 | **sí** |
| Café, té, yerba y cacao | sepa+fx | 18 | 1,10 | 0,74 | sí, si falta la anterior |
| Café, té, yerba y cacao | sepai | 18 | 1,10 | 0,85 | sí, si falta la anterior |
| Aguas, gaseosas y jugos | arr | 14 | 0,76 | 0,77 | no |
| Aguas, gaseosas y jugos | SEPA | 18 | 0,78 | 0,67 | sí, si falta la anterior |
| Aguas, gaseosas y jugos | sepa+fx | 18 | 0,78 | 0,68 | sí, si falta la anterior |
| Aguas, gaseosas y jugos | sepai | 18 | 0,78 | 0,67 | **sí** |
| Bebidas alcohólicas | SEPA | 18 | 0,90 | 0,66 | **sí** |
| Tabaco | ipc | 34 | 2,18 | 1,82 | **sí** |
| Ropa | fx | 34 | 2,22 | 2,48 | no |
| Ropa | ipc | 34 | 2,22 | 2,34 | no |
| Ropa | ipcl | 34 | 2,22 | 2,28 | no |
| Ropa | sal | 34 | 2,22 | 2,35 | no |
| Calzado | fx | 34 | 2,39 | 2,68 | no |
| Calzado | ipc | 34 | 2,39 | 2,31 | no |
| Calzado | ipcl | 34 | 2,39 | 2,51 | no |
| Calzado | sal | 34 | 2,39 | 2,65 | no |
| Alquiler de la vivienda | icl | 34 | 2,63 | 2,37 | sí, si falta la anterior |
| Alquiler de la vivienda | icl+ipc | 34 | 2,63 | 2,29 | **sí** |
| Alquiler de la vivienda | ipc | 34 | 2,63 | 2,31 | sí, si falta la anterior |
| Alquiler de la vivienda | ipcl | 34 | 2,63 | 2,38 | sí, si falta la anterior |
| Alquiler de la vivienda | ipcl+sal | 34 | 2,63 | 2,22 | sí, si falta la anterior |
| Alquiler de la vivienda | sal | 34 | 2,63 | 2,21 | sí, si falta la anterior |
| Electricidad, gas y otros combustibles | ipc | 34 | 6,58 | 4,81 | **sí** |
| Electricidad, gas y otros combustibles | ipc2 | 34 | 6,58 | 5,15 | sí, si falta la anterior |
| Equipamiento del hogar | fx | 34 | 2,13 | 2,32 | no |
| Equipamiento del hogar | sal | 34 | 2,13 | 2,39 | no |
| Limpieza y mantenimiento del hogar | ipc | 34 | 2,18 | 1,54 | sí, si falta la anterior |
| Limpieza y mantenimiento del hogar | SEPA | 18 | 0,76 | 0,72 | **sí** |
| Medicamentos | ipc | 34 | 2,05 | 1,63 | sí, si falta la anterior |
| Medicamentos | SEPA | 18 | 0,92 | 0,52 | **sí** |
| Compra de vehículos | autos | 17 | 1,63 | 0,82 | **sí** |
| Compra de vehículos | fx | 34 | 2,84 | 3,13 | no |
| Combustibles | nafta | 29 | 2,10 | 1,48 | sí, si falta la anterior |
| Combustibles | nafta+fx | 29 | 2,10 | 1,48 | sí, si falta la anterior |
| Combustibles | naftal | 29 | 2,10 | 1,59 | **sí** |
| Transporte público | ipc | 34 | 4,80 | 4,67 | sí, si falta la anterior |
| Transporte público | ipc2 | 34 | 4,80 | 4,70 | **sí** |
| Telefonía e internet | fx | 34 | 2,61 | 2,10 | sí, si falta la anterior |
| Telefonía e internet | ipc | 34 | 2,61 | 1,36 | **sí** |
| Telefonía e internet | ipc2 | 34 | 2,61 | 1,83 | sí, si falta la anterior |
| Telefonía e internet | ipcl | 34 | 2,61 | 2,15 | sí, si falta la anterior |
| Servicios recreativos y culturales | fx | 34 | 2,87 | 2,86 | sí, si falta la anterior |
| Servicios recreativos y culturales | ipc | 34 | 2,87 | 2,36 | **sí** |
| Servicios recreativos y culturales | ipcl | 34 | 2,87 | 2,70 | sí, si falta la anterior |
| Servicios recreativos y culturales | sal | 34 | 2,87 | 2,71 | sí, si falta la anterior |
| Diarios, libros y papelería | fx | 34 | 1,98 | 2,26 | no |
| Diarios, libros y papelería | ipc | 34 | 1,98 | 1,64 | **sí** |
| Diarios, libros y papelería | ipcl | 34 | 1,98 | 2,04 | no |
| Educación | ipc | 34 | 3,65 | 3,65 | no |
| Educación | ipcl | 34 | 3,65 | 3,65 | no |
| Educación | sal | 34 | 3,65 | 3,70 | no |
| Restaurantes y comidas fuera del hogar | alim | 18 | 1,01 | 0,91 | sí, si falta la anterior |
| Restaurantes y comidas fuera del hogar | alim1 | 34 | 1,92 | 1,48 | **sí** |
| Restaurantes y comidas fuera del hogar | alim1+sal | 34 | 1,92 | 1,44 | sí, si falta la anterior |
| Restaurantes y comidas fuera del hogar | ipc | 34 | 1,92 | 1,49 | sí, si falta la anterior |
| Restaurantes y comidas fuera del hogar | ipc+sal | 34 | 1,92 | 1,50 | sí, si falta la anterior |
| Restaurantes y comidas fuera del hogar | ipcl | 34 | 1,92 | 2,00 | no |
| Restaurantes y comidas fuera del hogar | sal | 34 | 1,92 | 1,93 | no |
| Cuidado personal | ipc | 34 | 2,55 | 1,89 | **sí** |
| Cuidado personal | ipcl | 34 | 2,55 | 2,68 | no |
| Cuidado personal | sal | 34 | 2,55 | 2,55 | no |
| Cuidado personal | SEPA | 18 | 0,70 | 0,69 | no |

