import pandas as pd 
import numpy as np 
import os 

MD_BOOK_PATH = os.path.abspath(os.path.join("..", "docs", "src", "contenido", "tables"))

## Carga datos con todas las medidas de complejidad
df_complexity = pd.read_csv("complexity_todo_metricas.csv")


"""
DECISIÓN MULTICRITERIO

Utilizaremos el método ELECTRE II que es una técnica de toma de decisión multicriterio el cual
nos permite generar un ranking de acciones dada una ponderación a lo criterios de esa acción

Criterios a utilizar:
    * Opportunity Gain
    * Distance
    * CPI
    * Tamaño del sector en México

El análisis lo realizaremos para las industrias que no han aparecido en El Salvador (i.e. aquellas con un RCA < 0.2)
"""
# Sólo falta calcular el criterio del tamaño del sector en México
mex_sector_empleo = df_complexity.query("zm_nombre!='SLV'")[["variable","value"]].groupby("variable").sum().apply(lambda x : np.log(x)).reset_index()
mex_sector_empleo.columns = ["variable", "log_empleo_mx"]

# Nos quedamos con las industrias que no han aparecido en El Salvador en 2021 y con las columnas pci (product complexity index), cog (complexity opportunity gain), distance
# Margen extensivo
#extensivo_slv_multicriteria = df_complexity.query("anio==2021 and zm=='SLV' and rca < 1.0")[["variable", "ciiu_nombre", "pci", "cog", "distance", "rca"]].set_index("variable")
extensivo_slv_multicriteria = df_complexity.query("anio==2021 and zm=='SLV'")[["variable", "ciiu_nombre", "pci", "cog", "distance", "rca"]].set_index("variable")
extensivo_slv_multicriteria = extensivo_slv_multicriteria.merge(right=mex_sector_empleo, how = "left", on = "variable")

# Agregamos los sectores más agregados
from ciiu_agregacion import ciiu_agregacion

df_ciiu_agregacion = pd.DataFrame(
    [(actividad, ciiu_agregacion[actividad[:2]][0], ciiu_agregacion[actividad[:2]][1]) for actividad in extensivo_slv_multicriteria.variable],
    columns = ["variable", "division", "seccion"]
)

# Concatenamos información
extensivo_slv_multicriteria = pd.concat([df_ciiu_agregacion.set_index("variable"), extensivo_slv_multicriteria.set_index("variable")], axis = 1).reset_index()

# Guardamos el dataframe
extensivo_slv_multicriteria.query("rca < 1.0").to_csv("extensivo_slv_multicriteria.csv", index = False)

# Exportamos dataframe a tabla markdown
tabla_md_71_sectores = extensivo_slv_multicriteria[["variable", "ciiu_nombre", "division", "seccion", "rca"]].copy()

tabla_md_71_sectores.columns = ["CIIU", "Nombre", "División", "Sección", "RCA"]

tabla_md_71_sectores.sort_values("Sección", ascending=False).reset_index(drop=True)

tabla_md_71_sectores["RCA"] = tabla_md_71_sectores["RCA"].round(3)

## Exportamos tabla a formato markdown
with open(os.path.join(MD_BOOK_PATH, "ciiu_71_sectores.md"), "w") as file:
    file.write(tabla_md_71_sectores[["CIIU", "Nombre", "RCA", "División", "Sección"]].to_markdown(index = False))


#### EJECUTAMOS EL PROGRAMA : julia multicriterio_sectores.jl
#### Regresamos aquí

df_resultados_extensivo = pd.read_csv("extensivo_multicriterio_ranking_sectores.csv")
df_resultados_extensivo["ranking"] = df_resultados_extensivo["ranking"].round(4)
df_resultados_extensivo = df_resultados_extensivo[["ciiu_clave", "ciiu_nombre", "ranking"]]

df_resultados_extensivo.columns = ["CIIU", "Nombre", "Ranking TOPSI"]
df_resultados_extensivo["Nombre"] = df_resultados_extensivo["Nombre"].apply(lambda x:x.replace(" (elaboración de pulque)", ""))
## Exportamos tabla a formato markdown
with open(os.path.join(MD_BOOK_PATH, "sectores_priorizados.md"), "w") as file:
    file.write(df_resultados_extensivo.to_markdown(index = False))
