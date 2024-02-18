# Industrias estratégicas en el margen extensivo

## Filtrado de industrias

El análisis de complejidad quedó restringido a 71 actividades de la reclasificación CIIU. Estas industrias se eligieron dado que dichas industrias contaban con datos de empleo tanto en El Salvador como en las Zonas Metropolitanas de México. Las 71 actividades elegidas se listan a continuación:

{{#include tables/ciiu_71_sectores.md}}

Con estas 71 industrias, se realizó el cálculo de las medidas complejidad. Específicamente, se calculó:

* RCA
* Densidad
* Diversidad
* Ubicuidad
* Índice de Complejidad del Producto
* Ganancia de Oportunidad

Una primera prueba de coherencia de resultados es el rankeo por el Índice de Complejidad Económica de las unidades geográficas que son comparadas. La siguiente tabla presenta el ranking de las Zonas Metropolitanas de México y El Salvador. Para los años 2013, 2020 y 2021, El Salvador entra en el top 10 de las zonas con mayor complejidad económica. Particularmente llama la atención que en 2021 se coloca en el puesto 5 del ranking. Como era de esperarse, Zonas Metropolitanas para las cuales hay evidencia que presentan alta complejidad (Monterrey y Ciudad de México), aparecen en los primeros puestos.

{{#include tables/ranking_zonas_metro.md}}

El análisis del márgen extensivo consiste en enfocarse en aquellas actividades que no cuentan con ventajas comparativas reveladas (esto es, aquellas actividades que tienen un RCA < 1). Fueron 37 industrias las que no cuentan con ventajas comparativas reveladas. Las industrias se encuentran listadas en el apéndice de la documentación en linea. La siguiente tabla presenta la distribución de las 37 industrias en la agregación de Sección del CIIU.

{{#include tables/conteo_seccion_industrias.md}}

## Proceso de identificación de industrias clave
Para la identificación de industrias clave se utilizó una técnica TOPSI (Technique for Order of Preference by Similarity to Ideal Solution) del enfoque de Decisión Multicriterio. El método compara un conjunto de alternativas, normaliza los scores para cada criterio y calcula la distancia geométrica entre cada alternativa y la alternativa ideal, la cual es el mejor score de cada criterio. En este caso, las alternativas corresponden a las industrias que se priorizarán, mientras que los criterios de selección corresponden a las métricas de complejidad:

* Ganancia de Oportunidad
* Índice de complejidad del Producto
* Distancia

Para cada métrica se necesita definir qué tipo de optimización debe realizar el método. Para el caso de la Distancia, el método debe encontrar industrias que minimicen la métrica, dado que nos interesa priorizar industrias para las cuales la brecha entre las capácidades existentes sea la más pequeña. Para el caso de Ganancia de Oportunidad y Complejidad del Producto, necesitamos que el método máximice su valor. **Todos los criterios tienen los mismos pesos de importancia**.

El método TOPSI compara los criterios de cada una de las alternativas para generar un ranking que toma valor entre 0 y 1 de las alternativas que cumplen con los criterios de optimización. 

La siguiente tabla presenta las industrias priorizadas de acuerdo al ranking calculado por TOPSI:

{{#include tables/sectores_priorizados.md}}