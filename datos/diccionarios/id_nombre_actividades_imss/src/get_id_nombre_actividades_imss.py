import pandas as pd 
import os 

## Definimos rutas
FILE_PATH = os.getcwd()
DATOS_PATH = os.path.abspath(os.path.join(FILE_PATH, "..", "datos"))
OUTPUT_PATH = os.path.abspath(os.path.join(FILE_PATH, "..", "output"))

## Cargamos diccionario de nombre de actividades del imss
imss_actividades = pd.read_excel(os.path.join(DATOS_PATH, "diccionario_de_datos_1.xlsx"), skiprows = 1, sheet_name = "sector 4", usecols = "E,F")

## Guardamos datos
imss_actividades.to_csv(os.path.join(OUTPUT_PATH, "imss_id_nombres_actividades.csv"), index = False)