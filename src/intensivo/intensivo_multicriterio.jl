using JMcDM
using DataFrames
using CSV

#### Hacemos ejecución para el margen extensivo
## Cargamos los datos para realizar el análisis multicriterio
intensivo_slv_multicriteria = DataFrame(CSV.File("ec_ES2021.csv"))

## Nos quedamos con los RCA >=1

## Eliminamos la columna del sector
intensivo_slv_multicriteria_mat = intensivo_slv_multicriteria[!, [:PCI, :ES_Share, :Comercio_Mundial, :RCA ]]

## Definimos los pesos de cada criterio
w  = [0.25, 0.25, 0.25, 0.25];

## Definimos la optimización a realizar en cada criterio
fns = [maximum, maximum, maximum, maximum];

## Ejecutamos el algoritmo
result_intensivo = topsis(Matrix(intensivo_slv_multicriteria_mat), w, fns);

## Guardamos los resultados en un dataframe

df_resultados_intensivo = DataFrame(
                          :sitc_code => intensivo_slv_multicriteria.sitc_code, 
                          :industria => intensivo_slv_multicriteria.Industria,
                          :ranking => result_intensivo.scores
                          )                        


## Exportamos el dataframe a csv
sort!(df_resultados_intensivo, [:ranking], rev = true)

CSV.write("exportaciones_intensivo_multicriterio_ranking_sectores.csv", df_resultados_intensivo)            
