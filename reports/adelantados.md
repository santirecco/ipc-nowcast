# Indicadores adelantados de alimentos

*Generado el 18/11/2026.*

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
| Pan y cereales | fx | 34 | 2,12 | 2,28 | no |
| Pan y cereales | SEPA | 18 | 0,49 | 0,51 | no |
| Pan y cereales | sepa+fx | 18 | 0,49 | 0,53 | no |
| Carnes y derivados | mayorista | 34 | 3,49 | 2,05 | **sí** |
| Carnes y derivados | SEPA | 18 | 2,52 | 2,47 | sí, si falta la anterior |
| Carnes y derivados | SEPA + mayorista | 18 | 2,52 | 1,74 | sí, si falta la anterior |
| Carnes y derivados | sepa_carne | 18 | 2,52 | 2,30 | sí, si falta la anterior |
| Carnes y derivados | sepa_carne+may | 18 | 2,52 | 1,72 | sí, si falta la anterior |
| Leche, lácteos y huevos | SEPA | 18 | 1,00 | 0,81 | **sí** |
| Leche, lácteos y huevos | sepa+fx | 18 | 1,00 | 0,88 | sí, si falta la anterior |
| Aceites, grasas y manteca | fx | 34 | 2,43 | 2,69 | no |
| Aceites, grasas y manteca | SEPA | 18 | 0,97 | 0,91 | **sí** |
| Aceites, grasas y manteca | sepa+fx | 18 | 0,97 | 1,05 | no |
| Frutas | arr | 14 | 4,58 | 4,30 | sí, si falta la anterior |
| Frutas | mayorista | 4 | 4,16 | 4,36 | no |
| Frutas | SEPA | 18 | 4,04 | 3,37 | **sí** |
| Verduras, tubérculos y legumbres | mayorista | 4 | 3,86 | 3,85 | no |
| Verduras, tubérculos y legumbres | SEPA | 18 | 6,52 | 6,58 | no |
| Azúcar, dulces y golosinas | SEPA | 18 | 0,79 | 0,72 | **sí** |
| Azúcar, dulces y golosinas | sepa+fx | 18 | 0,79 | 0,77 | no |
| Café, té, yerba y cacao | fx | 34 | 2,56 | 2,76 | no |
| Café, té, yerba y cacao | SEPA | 18 | 0,87 | 0,79 | **sí** |
| Café, té, yerba y cacao | sepa+fx | 18 | 0,87 | 0,85 | sí, si falta la anterior |
| Aguas, gaseosas y jugos | SEPA | 18 | 0,75 | 0,70 | **sí** |
| Aguas, gaseosas y jugos | sepa+fx | 18 | 0,75 | 0,70 | sí, si falta la anterior |
| Ropa | fx | 34 | 1,97 | 2,33 | no |
| Equipamiento del hogar | fx | 34 | 1,84 | 2,00 | no |
| Compra de vehículos | fx | 34 | 2,91 | 3,09 | no |
| Combustibles | nafta | 29 | 2,07 | 1,79 | **sí** |
| Combustibles | nafta+fx | 29 | 2,07 | 1,79 | sí, si falta la anterior |
| Diarios, libros y papelería | ipc | 34 | 2,03 | 1,63 | **sí** |
| Restaurantes y comidas fuera del hogar | ipc | 34 | 1,89 | 1,44 | **sí** |

### Mes completo

| Clase | Fuentes | Meses evaluados | Error solo estadística (pp) | Error con la fuente (pp) | ¿Se usa? |
|---|---|---|---|---|---|
| Pan y cereales | fx | 34 | 2,12 | 2,27 | no |
| Pan y cereales | SEPA | 18 | 0,49 | 0,50 | no |
| Pan y cereales | sepa+fx | 18 | 0,49 | 0,52 | no |
| Carnes y derivados | mayorista | 34 | 3,49 | 2,27 | **sí** |
| Carnes y derivados | SEPA | 18 | 2,52 | 2,43 | sí, si falta la anterior |
| Carnes y derivados | SEPA + mayorista | 18 | 2,52 | 1,81 | sí, si falta la anterior |
| Carnes y derivados | sepa_carne | 18 | 2,52 | 2,04 | sí, si falta la anterior |
| Carnes y derivados | sepa_carne+may | 18 | 2,52 | 1,70 | sí, si falta la anterior |
| Leche, lácteos y huevos | SEPA | 18 | 1,00 | 0,88 | **sí** |
| Leche, lácteos y huevos | sepa+fx | 18 | 1,00 | 0,92 | sí, si falta la anterior |
| Aceites, grasas y manteca | fx | 34 | 2,43 | 2,76 | no |
| Aceites, grasas y manteca | SEPA | 18 | 0,97 | 0,88 | **sí** |
| Aceites, grasas y manteca | sepa+fx | 18 | 0,97 | 0,94 | sí, si falta la anterior |
| Frutas | arr | 14 | 4,58 | 4,30 | sí, si falta la anterior |
| Frutas | mayorista | 4 | 4,16 | 4,32 | no |
| Frutas | SEPA | 18 | 4,04 | 3,11 | **sí** |
| Verduras, tubérculos y legumbres | mayorista | 4 | 3,86 | 3,61 | **sí** |
| Verduras, tubérculos y legumbres | SEPA | 18 | 6,52 | 6,47 | sí, si falta la anterior |
| Azúcar, dulces y golosinas | SEPA | 18 | 0,79 | 0,65 | **sí** |
| Azúcar, dulces y golosinas | sepa+fx | 18 | 0,79 | 0,70 | sí, si falta la anterior |
| Café, té, yerba y cacao | fx | 34 | 2,56 | 2,80 | no |
| Café, té, yerba y cacao | SEPA | 18 | 0,87 | 0,72 | **sí** |
| Café, té, yerba y cacao | sepa+fx | 18 | 0,87 | 0,77 | sí, si falta la anterior |
| Aguas, gaseosas y jugos | SEPA | 18 | 0,75 | 0,66 | **sí** |
| Aguas, gaseosas y jugos | sepa+fx | 18 | 0,75 | 0,66 | sí, si falta la anterior |
| Ropa | fx | 34 | 1,97 | 2,31 | no |
| Equipamiento del hogar | fx | 34 | 1,84 | 1,99 | no |
| Medicamentos | SEPA | 18 | 0,52 | 0,43 | **sí** |
| Compra de vehículos | fx | 34 | 2,91 | 3,03 | no |
| Combustibles | nafta | 29 | 2,07 | 1,47 | **sí** |
| Combustibles | nafta+fx | 29 | 2,07 | 1,47 | sí, si falta la anterior |
| Diarios, libros y papelería | ipc | 34 | 2,03 | 1,63 | **sí** |
| Restaurantes y comidas fuera del hogar | ipc | 34 | 1,89 | 1,44 | **sí** |

