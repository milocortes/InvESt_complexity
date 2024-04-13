# Cálculo de Factores de Viabilidad

## Relación Directa de Insumos/```input_similarity```

La métrica expresa la presencia de actividades que producen insumos necesarios para las industrias. Es decir, trata de responder a la pregunta ¿están presentes las actividades que a las cuales las actividades les compran insumos?. Para la construcción de esta métrica se utilizó la [Matriz de Insumo Producto para México](https://www.inegi.org.mx/temas/mip/#informacion_general) de 2018 en precios constantes y la matriz de presencia-ausencia para las actividades CIIU-Recodificado-Rev-4 estimada en el ejercicio de Complejidad (o matriz \\( M_{u,a} \\), donde los subíndices \\( u\\) y \\(a\\) corresponden a una unidad geográfica-zona metropolitana- y actividad, respectivamente). La Matriz Insumo Producto fue traducida de SCIAN 2018 a CIIU-Recodificado-Rev-4. 

Para el cálculo de la metrica se utilizó la matriz de coeficientes técnicos , \\(A\\), de la Matriz Insumo Producto. Siendo \\(Z\\) la matriz de flujo entre sectores y \\(X\\) es el vector de producto total, la matriz de coeficientes técnicos se calcularía como:

\\[
A= Z \cdot (X \cdot I)^{-1}
\\]

Las entradas de la matriz \\(A\\) definen los coeficientes técnicos como la proporción de insumo ofrecido por el sector \\(i\\) y comprado por el sector \\(j\\) con respecto al producto total del sector \\(j\\), \\(a_{ij}= \dfrac{z_{ij}}{x_j}\\).

La presencia entre insumos utilizados por las actividades se calcularía como una medida de densidad donde la matriz de proximidad entre industrias, \\(\phi_{a,a'}\\), se sustituye por la matriz de coeficientes técnicos:

\\[
\begin{equation}
    \dfrac{ \sum_{a'}M_{ua'}A_{aa'}^{T} }{\sum_{a'} A^{T}_{aa'}}
\end{equation}
\\]

Dado que las columnas de la matriz de coeficientes técnicos representa la proporción de insumo ofrecido por el sector  \\(j\\) y comprado por el sector \\(i\\), transponemos la matriz para poder realizar el cálculo.

## Relación Directa de Productos/```output_similarity```

La métrica expresa la presencia de actividades que compran productos de las actividades. Es decir, trata de responder a la pregunta ¿están presentes las actividades que son clientes de los productos de las actividades? El cálculo es prácticamente el mismo que el de la medida de Relación Directa de Insumos. Sin embargo, dado que las entradas de la matriz de coeficientes técnicod corresponden a la proporción de insumo ofrecido por el sector \\(i\\) y comprado por el sector \\(j\\) con respecto al producto total del sector \\(j\\), no es necesario transponer la matriz: 

\\[
\begin{equation}
    \dfrac{ \sum_{a'}M_{ua'}A_{aa'} }{\sum_{a'} A_{aa'}}
\end{equation}
\\]


## Similitud de industrias provedoras/input_presence_similarity

La métrica expresa la presencia de actividades similares respecto a la demanda de mismos insumos. Es decir, trata de responder a la pregunta ¿están presentes industrias que demandan los mismos insumos? Para el cálculo de la medida se utilizó la matriz de coeficientes técnicos \\(A\\) para realizar el cáculo *row wise correlation*, esto es, calcular la correlación para cada par de industrias para obtener una medida de similitud entre industrias de acuerdo a los insumos que utilizan.

La presencia entre industrias que demandan insumos similares se calcularía como una medida de densidad donde la matriz de proximidad entre industrias, \\(\phi_{a,a'}\\), se sustituye por la matriz de correlación entre pares de industrias de la matriz de coeficientes técnicos:

\\[
\begin{equation}
    \dfrac{ \sum_{a'}M_{ua'}corr(A_{aa'}^T) }{\sum_{a'} corr(A_{aa'}^T)}
\end{equation}
\\]

Dado que las columnas de la matriz de coeficientes técnicos representa la proporción de insumo ofrecido por el sector  \\(j\\) y comprado por el sector \\(i\\), transponemos la matriz de coeficientes técnicos para calcular la correlación entre pares de industrias.

## Similitud de industrias compradoras/output_presence_similarity

La métrica expresa la presencia de actividades similares respecto a si le venden sus producción a las mismas industrias. Es decir, trata de responder a la pregunta ¿están presentes industrias que tienen como clientes a las mismas activiades? Para el cálculo de la medida se utilizó la matriz de coeficientes técnicos \\(A\\) para realizar el cáculo *column wise correlation*, esto es, calcular la correlación para cada par de industrias para obtener una medida de similitud entre industrias de acuerdo a las industrias que tienen como clientes.

La presencia entre industrias que demandan insumos similares se calcularía como una medida de densidad donde la matriz de proximidad entre industrias, \\(\phi_{a,a'}\\), se sustituye por la matriz de correlación entre pares de industrias de la matriz de coeficientes técnicos:

\\[
\begin{equation}
    \dfrac{ \sum_{a'}M_{ua'}corr(A_{aa'}) }{\sum_{a'} corr(A_{aa'})}
\end{equation}
\\]

## Relación Directa de Ocupaciones/coempleo_similarity
La métrica expresa la presencia de actividades que demandan los mismos tipos de ocupaciones. Para calcular la métrica se utilizaron datos de Staffing Patterns. Dichos datos por tipo de empleo de acuerdo al [Standard Occupational Classification (SOC) 2018](https://www.bls.gov/soc/2018/home.htm) para las actividades NAICS 2017.

Una muestra de los datos se presenta en la siguiente tabla:

|   NAICS | NAICS_TITLE                    | OCC_CODE   | OCC_TITLE                                     |   TOT_EMP |
|--------:|:-------------------------------|:-----------|:----------------------------------------------|----------:|
|  221111 | Hydroelectric Power Generation | 00-0000    | Industry Total                                |      5610 |
|  221111 | Hydroelectric Power Generation | 11-0000    | Management Occupations                        |       250 |
|  221111 | Hydroelectric Power Generation | 11-1000    | Top Executives                                |       180 |
|  221111 | Hydroelectric Power Generation | 11-1021    | General and Operations Managers               |       180 |
|  221111 | Hydroelectric Power Generation | 11-3000    | Operations Specialties Managers               |        40 |

A partir de estos datos se estimó una matriz de presencia-ausencia donde nos interesa conocer si las actividades están especializadas en el empleo de algún tipo de ocupación. Denotamos la matriz como \\(M_{occ,a}\\) donde los subíndices \\(a\\) y \\(occ\\) corresponden a la actividad CIIU Recodificada Rev 4 y al tipo de ocupación SOC, respectivamente. De esta matriz calculamos una matriz de proximidad del tipo de ocupación empleado entre actividades , \\(\phi_{a,a'}^{\text{SOC}}\\). 

Al sustituir esta matriz de proximidad \\(\phi_{a,a'}^{\text{SOC}}\\) en el cálculo de la densidad, y usando la matriz \\( M_{u,a} \\), podemos calcular una medida de la presencia de actividades que demandan las mismas ocupaciones-o coempleo- 

\\[
\begin{equation}
    \dfrac{ \sum_{a'}M_{ua'}\phi_{a,a'}^{\text{SOC}} }{\sum_{a'} \phi_{a,a'}^{\text{SOC}}}
\end{equation}
\\]

## Medida de requerimientos de trabajo calificado (Balance de Competencias Laborales/onet_metrica)

Se estimó una medida de requerimientos de trabajo calificado por industria en clasificación CIIU-Recodificada-Rev 4.

Se usaron dos fuentes de datos:

* Tipo de empleo por actividad NAICS (Staffing Patterns).
* [O*NET datos de Educación, Training and Experience](https://www.onetcenter.org/dictionary/28.2/excel/education_training_experience.html)

Se necesita una medida que manifieste la intensidad de trabajo calificado requerido por las industrias. Consideramos trabajo calificado a aquellas ocupaciones que cuentan, cómo mínimo, con grado de Bachelor. De manera que agrupamos los datos de O*NET para considerar la suma de las razones de empleo de Bachelor a Pos-Doctoral.

Posteriormente, de los datos de Staffing Patterns ponderamos los datos agrupados por la razón cantidad de empleo en cada categoría O*NET y el empleo total de la actividad CIIU-Recodificada-Rev 4, esto con la intensión de modular el nivel de educación requerido en el tipo de ocupación ONET con la demanda de esa ocupación en la actividad CIIU.

Por último, ponderamos ese valor por la razón entre el empleo de la actividad CIIU con respecto al total del empleo.

