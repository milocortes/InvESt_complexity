# Industrias transables

El análisis de complejidad con datos se empleo se restringió a industrias transables.  

No existe una clasificación oficial de industrias transables. Para el estudio, se utilizó la clasificación de [Delgado (2014)](https://www.nber.org/system/files/working_papers/w20375/w20375.pdf).  

A continuación se listan los Cluster de actividades transables que indentifican los autores, así como el número de industrias que los integran y el porcentaje de empleo incorporado.

{{#include tables/porter_transables.md}}


La clasificación está elaborada para NAICS 2008 a nivel de clase, de manera que se procedió a realizar los encadenamientos necesarios para harmonizar dicha clasificación con la versión más actual de NAICS 2017. Posteriormente se realizó un diccionario de las actividades transables en NAICS 2017 a SCIAN 2018. Por último, se utilizó la reclasificación CIIU Rev 4- SCIAN 2018 para identificar las industrias CIIU Rev 4 para las cuales todas las actividades SCIAN 2018 corresponden a actividades transables. Es decir, filtramos por industrias CIIU para las cuales la suma del empleo de clases SCIAN 2018 correspondiera al 100% del total de empleo. 

La siguiente tabla presenta la correspondencia entre los cluster de actividades transables y las clases de actividad NAICS que los integran. 

{{#include tables/porter_transables_cluster_clases_NAICS_2017.md}}

Cabe señalar que es preciso realizar un filtrado adicional de actividades transables para ajustarlo al contexto particular de la economía Salvadoreña. Es posible que en Estados Unidos las actividades como Marketing puedan ser consideradas transables por su capacidad de ser demandadas por economías del resto del mundo. Sin embargo, dichas capacidades no han sido desarrolladas en economías latinoamericanas. Por ello, se está tomando en cuenta realizar un filtrado adicional para contextualizar las actividades transables al caso de El Salvador. 
