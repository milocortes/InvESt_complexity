import pandas as pd 
import os 

## Definimos rutas
FILE_PATH = os.getcwd()
DATOS_PATH = os.path.abspath(os.path.join(FILE_PATH, "..", "datos"))
OUTPUT_PATH = os.path.abspath(os.path.join(FILE_PATH, "..", "output"))

with open(os.path.join(DATOS_PATH, "estados_raw.txt"), "r") as file:
    estados_usa = pd.DataFrame([
            (j[0], " ".join(j[1:]))
            for j in [i[7:].strip().split() for i in file.readlines()]
    ], columns = ["id", "nombre"])
    
estados_usa.to_csv(os.path.join(OUTPUT_PATH, "usa_id_estados.csv"), index = False)