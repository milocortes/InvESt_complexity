## Cargamos paquetes 
import networkx as nx
from networkx.algorithms import community
import numpy as np
import pandas as pd
import json
import os 

## Definimos rutas donde se encuentran las correspondencias scian-ciiu
FILE_PATH = os.getcwd()
OUTPUT_PATH = os.path.abspath(os.path.join("..", "output"))
MD_BOOK_PATH = os.path.abspath(os.path.join(*[".."]*5, "docs", "src", "contenido", "tables"))

## Cargamos datos
ciiu_reco = pd.read_csv(os.path.join(OUTPUT_PATH, "recodificacion_ciiu-rev-4.csv"))
naics_reco = json.load(open(os.path.join(OUTPUT_PATH, "ciiu_recodificado_naics_2017.json"), "r"))
scian_reco = json.load(open(os.path.join(OUTPUT_PATH, "ciiu_recodificado_scian_2018.json"), "r"))

## Hacemos merge entre los clasificadores
naics_reco = {k:",".join(v) for k,v in naics_reco.items()}
scian_reco = {k:",".join(v) for k,v in scian_reco.items()}

ciiu_reco["NAICS 2017"] = ciiu_reco["ciiu_nueva_cod"].replace(naics_reco)
ciiu_reco["SCIAN 2018"] = ciiu_reco["ciiu_nueva_cod"].replace(scian_reco)

## Renombramos columnas
ciiu_reco.columns = ["CIIU (recodificación)", "Actividades CIIU agrupadas", "CIIU nombre", "NAICS 2017", "SCIAN 2018"]

## Exportamos tabla a formato markdown
with open(os.path.join(MD_BOOK_PATH, "ciiu_recod_naics_scian.md"), "w") as file:
    file.write(ciiu_reco.to_markdown(index = False))

