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
| Pan y cereales | SEPA | 18 | 0,49 | 0,50 | no |
| Carnes y derivados | mayorista | 112 | 3,36 | 1,98 | **sí** |
| Carnes y derivados | SEPA | 18 | 2,52 | 2,50 | no |
| Carnes y derivados | SEPA + mayorista | 18 | 2,52 | 1,75 | sí, si falta la anterior |
| Leche, lácteos y huevos | SEPA | 18 | 1,00 | 0,82 | **sí** |
| Aceites, grasas y manteca | SEPA | 18 | 0,97 | 0,91 | **sí** |
| Frutas | mayorista | 4 | 4,16 | 4,36 | no |
| Frutas | SEPA | 18 | 4,04 | 3,36 | **sí** |
| Verduras, tubérculos y legumbres | mayorista | 4 | 3,86 | 3,85 | no |
| Verduras, tubérculos y legumbres | SEPA | 18 | 6,52 | 6,61 | no |
| Azúcar, dulces y golosinas | SEPA | 18 | 0,79 | 0,72 | **sí** |
| Café, té, yerba y cacao | SEPA | 18 | 0,87 | 0,79 | **sí** |
| Aguas, gaseosas y jugos | SEPA | 18 | 0,75 | 0,70 | **sí** |

### Mes completo

| Clase | Fuentes | Meses evaluados | Error solo estadística (pp) | Error con la fuente (pp) | ¿Se usa? |
|---|---|---|---|---|---|
| Pan y cereales | SEPA | 18 | 0,49 | 0,49 | no |
| Carnes y derivados | mayorista | 112 | 3,36 | 2,09 | **sí** |
| Carnes y derivados | SEPA | 18 | 2,52 | 2,47 | sí, si falta la anterior |
| Carnes y derivados | SEPA + mayorista | 18 | 2,52 | 1,83 | sí, si falta la anterior |
| Leche, lácteos y huevos | SEPA | 18 | 1,00 | 0,89 | **sí** |
| Aceites, grasas y manteca | SEPA | 18 | 0,97 | 0,88 | **sí** |
| Frutas | mayorista | 4 | 4,16 | 4,32 | no |
| Frutas | SEPA | 18 | 4,04 | 3,10 | **sí** |
| Verduras, tubérculos y legumbres | mayorista | 4 | 3,86 | 3,61 | **sí** |
| Verduras, tubérculos y legumbres | SEPA | 18 | 6,52 | 6,50 | no |
| Azúcar, dulces y golosinas | SEPA | 18 | 0,79 | 0,65 | **sí** |
| Café, té, yerba y cacao | SEPA | 18 | 0,87 | 0,73 | **sí** |
| Aguas, gaseosas y jugos | SEPA | 18 | 0,75 | 0,65 | **sí** |

