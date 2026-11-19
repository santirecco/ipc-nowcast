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
| Pan y cereales | fx | 94 | 1,90 | 1,84 | sí, si falta la anterior |
| Pan y cereales | SEPA | 18 | 0,73 | 0,53 | **sí** |
| Pan y cereales | sepa+fx | 18 | 0,73 | 0,53 | sí, si falta la anterior |
| Carnes y derivados | arr | 14 | 1,82 | 1,71 | **sí** |
| Carnes y derivados | mayorista | 94 | 3,45 | 2,46 | sí, si falta la anterior |
| Carnes y derivados | may+may2 | 94 | 3,45 | 2,48 | sí, si falta la anterior |
| Carnes y derivados | SEPA | 18 | 1,90 | 1,90 | no |
| Carnes y derivados | SEPA + mayorista | 18 | 1,90 | 1,93 | no |
| Carnes y derivados | sepa_carne | 18 | 1,90 | 1,95 | no |
| Carnes y derivados | sepa_carne+may | 18 | 1,90 | 1,92 | no |
| Leche, lácteos y huevos | arr | 14 | 1,15 | 1,17 | no |
| Leche, lácteos y huevos | SEPA | 18 | 1,18 | 0,65 | **sí** |
| Leche, lácteos y huevos | sepa+fx | 18 | 1,18 | 0,65 | sí, si falta la anterior |
| Aceites, grasas y manteca | arr | 14 | 0,98 | 1,00 | no |
| Aceites, grasas y manteca | fx | 94 | 2,67 | 2,70 | no |
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
| Café, té, yerba y cacao | fx | 94 | 2,38 | 2,44 | no |
| Café, té, yerba y cacao | SEPA | 18 | 1,10 | 0,78 | **sí** |
| Café, té, yerba y cacao | sepa+fx | 18 | 1,10 | 0,86 | sí, si falta la anterior |
| Aguas, gaseosas y jugos | arr | 14 | 0,76 | 0,77 | no |
| Aguas, gaseosas y jugos | SEPA | 18 | 0,78 | 0,72 | sí, si falta la anterior |
| Aguas, gaseosas y jugos | sepa+fx | 18 | 0,78 | 0,72 | **sí** |
| Bebidas alcohólicas | SEPA | 18 | 0,90 | 0,67 | **sí** |
| Tabaco | ipc | 94 | 2,44 | 2,17 | **sí** |
| Ropa | fx | 92 | 2,23 | 2,29 | no |
| Ropa | ipc | 92 | 2,23 | 2,17 | **sí** |
| Ropa | ipcl | 92 | 2,23 | 2,29 | no |
| Ropa | sal | 92 | 2,23 | 2,31 | no |
| Calzado | fx | 92 | 2,50 | 2,49 | no |
| Calzado | ipc | 92 | 2,50 | 2,29 | **sí** |
| Calzado | ipcl | 92 | 2,50 | 2,54 | no |
| Calzado | sal | 92 | 2,50 | 2,58 | no |
| Alquiler de la vivienda | icl | 60 | 2,36 | 2,18 | sí, si falta la anterior |
| Alquiler de la vivienda | icl+ipc | 60 | 2,36 | 2,17 | sí, si falta la anterior |
| Alquiler de la vivienda | ipc | 94 | 1,84 | 1,68 | sí, si falta la anterior |
| Alquiler de la vivienda | ipcl | 94 | 1,84 | 1,71 | sí, si falta la anterior |
| Alquiler de la vivienda | ipcl+sal | 94 | 1,84 | 1,65 | sí, si falta la anterior |
| Alquiler de la vivienda | sal | 94 | 1,84 | 1,65 | **sí** |
| Electricidad, gas y otros combustibles | ipc | 94 | 4,26 | 3,86 | **sí** |
| Electricidad, gas y otros combustibles | ipc2 | 94 | 4,26 | 4,25 | no |
| Equipamiento del hogar | fx | 94 | 1,90 | 1,82 | **sí** |
| Equipamiento del hogar | sal | 94 | 1,90 | 2,00 | no |
| Limpieza y mantenimiento del hogar | ipc | 94 | 1,91 | 1,58 | **sí** |
| Limpieza y mantenimiento del hogar | SEPA | 18 | 0,76 | 0,78 | no |
| Medicamentos | ipc | 94 | 2,19 | 2,13 | sí, si falta la anterior |
| Medicamentos | SEPA | 18 | 0,92 | 0,47 | **sí** |
| Compra de vehículos | autos | 17 | 1,63 | 0,82 | **sí** |
| Compra de vehículos | fx | 94 | 2,51 | 2,45 | sí, si falta la anterior |
| Combustibles | nafta | 29 | 2,10 | 1,59 | **sí** |
| Combustibles | nafta+fx | 29 | 2,10 | 1,59 | sí, si falta la anterior |
| Transporte público | ipc | 94 | 3,63 | 3,49 | **sí** |
| Transporte público | ipc2 | 94 | 3,63 | 3,62 | no |
| Telefonía e internet | fx | 94 | 2,78 | 2,53 | sí, si falta la anterior |
| Telefonía e internet | ipc | 94 | 2,78 | 2,34 | **sí** |
| Telefonía e internet | ipc2 | 94 | 2,78 | 2,56 | sí, si falta la anterior |
| Telefonía e internet | ipcl | 94 | 2,78 | 2,66 | sí, si falta la anterior |
| Servicios recreativos y culturales | fx | 94 | 2,62 | 2,61 | no |
| Servicios recreativos y culturales | ipc | 94 | 2,62 | 2,31 | **sí** |
| Servicios recreativos y culturales | ipcl | 94 | 2,62 | 2,43 | sí, si falta la anterior |
| Servicios recreativos y culturales | sal | 94 | 2,62 | 2,49 | sí, si falta la anterior |
| Diarios, libros y papelería | fx | 94 | 1,92 | 1,90 | no |
| Diarios, libros y papelería | ipc | 94 | 1,92 | 1,75 | **sí** |
| Diarios, libros y papelería | ipcl | 94 | 1,92 | 1,93 | no |
| Educación | ipc | 94 | 3,06 | 3,46 | no |
| Educación | ipcl | 94 | 3,06 | 3,42 | no |
| Educación | sal | 94 | 3,06 | 3,56 | no |
| Restaurantes y comidas fuera del hogar | alim | 18 | 1,01 | 0,91 | sí, si falta la anterior |
| Restaurantes y comidas fuera del hogar | alim1 | 89 | 1,77 | 1,54 | **sí** |
| Restaurantes y comidas fuera del hogar | alim1+sal | 89 | 1,77 | 1,53 | sí, si falta la anterior |
| Restaurantes y comidas fuera del hogar | ipc | 89 | 1,77 | 1,57 | sí, si falta la anterior |
| Restaurantes y comidas fuera del hogar | ipc+sal | 89 | 1,77 | 1,59 | sí, si falta la anterior |
| Restaurantes y comidas fuera del hogar | ipcl | 89 | 1,77 | 1,80 | no |
| Restaurantes y comidas fuera del hogar | sal | 89 | 1,77 | 1,78 | no |
| Cuidado personal | ipc | 94 | 2,08 | 1,69 | **sí** |
| Cuidado personal | ipcl | 94 | 2,08 | 2,03 | sí, si falta la anterior |
| Cuidado personal | sal | 94 | 2,08 | 2,05 | sí, si falta la anterior |
| Cuidado personal | SEPA | 18 | 0,70 | 0,71 | no |

### Mes completo

| Clase | Fuentes | Meses evaluados | Error solo estadística (pp) | Error con la fuente (pp) | ¿Se usa? |
|---|---|---|---|---|---|
| Pan y cereales | arr | 14 | 0,68 | 0,70 | no |
| Pan y cereales | fx | 94 | 1,90 | 1,79 | sí, si falta la anterior |
| Pan y cereales | SEPA | 18 | 0,73 | 0,49 | **sí** |
| Pan y cereales | sepa+fx | 18 | 0,73 | 0,49 | sí, si falta la anterior |
| Pan y cereales | sepai | 18 | 0,73 | 0,56 | sí, si falta la anterior |
| Carnes y derivados | arr | 14 | 1,82 | 1,71 | sí, si falta la anterior |
| Carnes y derivados | mayorista | 94 | 3,45 | 2,56 | sí, si falta la anterior |
| Carnes y derivados | may+may2 | 94 | 3,45 | 2,59 | sí, si falta la anterior |
| Carnes y derivados | SEPA | 18 | 1,90 | 1,91 | no |
| Carnes y derivados | SEPA + mayorista | 18 | 1,90 | 1,84 | sí, si falta la anterior |
| Carnes y derivados | sepa_carne | 18 | 1,90 | 1,96 | no |
| Carnes y derivados | sepa_carne+may | 18 | 1,90 | 1,79 | **sí** |
| Leche, lácteos y huevos | arr | 14 | 1,15 | 1,17 | no |
| Leche, lácteos y huevos | SEPA | 18 | 1,18 | 0,75 | **sí** |
| Leche, lácteos y huevos | sepa+fx | 18 | 1,18 | 0,75 | sí, si falta la anterior |
| Leche, lácteos y huevos | sepai | 18 | 1,18 | 0,87 | sí, si falta la anterior |
| Aceites, grasas y manteca | arr | 14 | 0,98 | 1,00 | no |
| Aceites, grasas y manteca | fx | 94 | 2,67 | 2,73 | no |
| Aceites, grasas y manteca | SEPA | 18 | 0,99 | 1,02 | no |
| Aceites, grasas y manteca | sepa+fx | 18 | 0,99 | 0,99 | no |
| Aceites, grasas y manteca | sepai | 18 | 0,99 | 0,76 | **sí** |
| Frutas | arr | 14 | 2,63 | 2,70 | no |
| Frutas | mayorista | 4 | 4,07 | 4,10 | no |
| Frutas | SEPA | 18 | 2,82 | 2,82 | no |
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
| Café, té, yerba y cacao | fx | 94 | 2,38 | 2,43 | no |
| Café, té, yerba y cacao | SEPA | 18 | 1,10 | 0,70 | **sí** |
| Café, té, yerba y cacao | sepa+fx | 18 | 1,10 | 0,74 | sí, si falta la anterior |
| Café, té, yerba y cacao | sepai | 18 | 1,10 | 0,85 | sí, si falta la anterior |
| Aguas, gaseosas y jugos | arr | 14 | 0,76 | 0,77 | no |
| Aguas, gaseosas y jugos | SEPA | 18 | 0,78 | 0,67 | sí, si falta la anterior |
| Aguas, gaseosas y jugos | sepa+fx | 18 | 0,78 | 0,68 | sí, si falta la anterior |
| Aguas, gaseosas y jugos | sepai | 18 | 0,78 | 0,67 | **sí** |
| Bebidas alcohólicas | SEPA | 18 | 0,90 | 0,66 | **sí** |
| Tabaco | ipc | 94 | 2,44 | 2,17 | **sí** |
| Ropa | fx | 92 | 2,23 | 2,30 | no |
| Ropa | ipc | 92 | 2,23 | 2,17 | **sí** |
| Ropa | ipcl | 92 | 2,23 | 2,29 | no |
| Ropa | sal | 92 | 2,23 | 2,31 | no |
| Calzado | fx | 92 | 2,50 | 2,47 | sí, si falta la anterior |
| Calzado | ipc | 92 | 2,50 | 2,29 | **sí** |
| Calzado | ipcl | 92 | 2,50 | 2,54 | no |
| Calzado | sal | 92 | 2,50 | 2,58 | no |
| Alquiler de la vivienda | icl | 60 | 2,36 | 2,18 | sí, si falta la anterior |
| Alquiler de la vivienda | icl+ipc | 60 | 2,36 | 2,17 | sí, si falta la anterior |
| Alquiler de la vivienda | ipc | 94 | 1,84 | 1,68 | sí, si falta la anterior |
| Alquiler de la vivienda | ipcl | 94 | 1,84 | 1,71 | sí, si falta la anterior |
| Alquiler de la vivienda | ipcl+sal | 94 | 1,84 | 1,65 | sí, si falta la anterior |
| Alquiler de la vivienda | sal | 94 | 1,84 | 1,65 | **sí** |
| Electricidad, gas y otros combustibles | ipc | 94 | 4,26 | 3,86 | **sí** |
| Electricidad, gas y otros combustibles | ipc2 | 94 | 4,26 | 4,25 | no |
| Equipamiento del hogar | fx | 94 | 1,90 | 1,75 | **sí** |
| Equipamiento del hogar | sal | 94 | 1,90 | 2,00 | no |
| Limpieza y mantenimiento del hogar | ipc | 94 | 1,91 | 1,58 | sí, si falta la anterior |
| Limpieza y mantenimiento del hogar | SEPA | 18 | 0,76 | 0,72 | **sí** |
| Medicamentos | ipc | 94 | 2,19 | 2,13 | sí, si falta la anterior |
| Medicamentos | SEPA | 18 | 0,92 | 0,52 | **sí** |
| Compra de vehículos | autos | 17 | 1,63 | 0,82 | **sí** |
| Compra de vehículos | fx | 94 | 2,51 | 2,43 | sí, si falta la anterior |
| Combustibles | nafta | 29 | 2,10 | 1,48 | **sí** |
| Combustibles | nafta+fx | 29 | 2,10 | 1,48 | sí, si falta la anterior |
| Transporte público | ipc | 94 | 3,63 | 3,49 | **sí** |
| Transporte público | ipc2 | 94 | 3,63 | 3,62 | no |
| Telefonía e internet | fx | 94 | 2,78 | 2,54 | sí, si falta la anterior |
| Telefonía e internet | ipc | 94 | 2,78 | 2,34 | **sí** |
| Telefonía e internet | ipc2 | 94 | 2,78 | 2,56 | sí, si falta la anterior |
| Telefonía e internet | ipcl | 94 | 2,78 | 2,66 | sí, si falta la anterior |
| Servicios recreativos y culturales | fx | 94 | 2,62 | 2,62 | no |
| Servicios recreativos y culturales | ipc | 94 | 2,62 | 2,31 | **sí** |
| Servicios recreativos y culturales | ipcl | 94 | 2,62 | 2,43 | sí, si falta la anterior |
| Servicios recreativos y culturales | sal | 94 | 2,62 | 2,49 | sí, si falta la anterior |
| Diarios, libros y papelería | fx | 94 | 1,92 | 1,91 | no |
| Diarios, libros y papelería | ipc | 94 | 1,92 | 1,75 | **sí** |
| Diarios, libros y papelería | ipcl | 94 | 1,92 | 1,93 | no |
| Educación | ipc | 94 | 3,06 | 3,46 | no |
| Educación | ipcl | 94 | 3,06 | 3,42 | no |
| Educación | sal | 94 | 3,06 | 3,56 | no |
| Restaurantes y comidas fuera del hogar | alim | 18 | 1,01 | 0,91 | sí, si falta la anterior |
| Restaurantes y comidas fuera del hogar | alim1 | 89 | 1,77 | 1,54 | **sí** |
| Restaurantes y comidas fuera del hogar | alim1+sal | 89 | 1,77 | 1,53 | sí, si falta la anterior |
| Restaurantes y comidas fuera del hogar | ipc | 89 | 1,77 | 1,57 | sí, si falta la anterior |
| Restaurantes y comidas fuera del hogar | ipc+sal | 89 | 1,77 | 1,59 | sí, si falta la anterior |
| Restaurantes y comidas fuera del hogar | ipcl | 89 | 1,77 | 1,80 | no |
| Restaurantes y comidas fuera del hogar | sal | 89 | 1,77 | 1,78 | no |
| Cuidado personal | ipc | 94 | 2,08 | 1,69 | **sí** |
| Cuidado personal | ipcl | 94 | 2,08 | 2,03 | sí, si falta la anterior |
| Cuidado personal | sal | 94 | 2,08 | 2,05 | sí, si falta la anterior |
| Cuidado personal | SEPA | 18 | 0,70 | 0,69 | no |

