using JMcDM
using DataFrames
using CSV

#### Hacemos ejecución para el margen extensivo
## Cargamos los datos para realizar el análisis multicriterio
extensivo_slv_multicriteria = DataFrame(CSV.File("extensivo_slv_multicriteria.csv"))

## Eliminamos la columna del sector
extensivo_slv_multicriteria_mat = extensivo_slv_multicriteria[!, [:pci, :cog, :distance]]

## Definimos los pesos de cada criterio
w  = [0.25, 0.25, 0.25, 0.25];

## Definimos la optimización a realizar en cada criterio
fns = [maximum, maximum, minimum];

## Ejecutamos el algoritmo
result_extensivo = topsis(Matrix(extensivo_slv_multicriteria_mat), w, fns);

## Guardamos los resultados en un dataframe
df_resultados_extensivo = DataFrame(
                          :ciiu_clave => extensivo_slv_multicriteria.variable, 
                          :ciiu_nombre => extensivo_slv_multicriteria.ciiu_nombre,
                          :ciiu_division => extensivo_slv_multicriteria.division,
                          :ciiu_seccion => extensivo_slv_multicriteria.seccion,
                          :pci => extensivo_slv_multicriteria.pci,
                          :cog => extensivo_slv_multicriteria.cog,
                          :distance => extensivo_slv_multicriteria.distance,
                          :rca => extensivo_slv_multicriteria.rca,
                          :ranking => result_extensivo.scores
                          )


## Exportamos el dataframe a csv
sort!(df_resultados_extensivo, [:ranking], rev = true)


CSV.write("extensivo_multicriterio_ranking_sectores.csv", df_resultados_extensivo)            

