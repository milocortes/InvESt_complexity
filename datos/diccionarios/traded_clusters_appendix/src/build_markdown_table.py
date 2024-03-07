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
MD_BOOK_PATH = os.path.abspath(os.path.join(*[".."]*4, "docs", "src", "contenido", "tables"))

## Cargamos industrias transables por cluster
transables = json.load(open(os.path.join(OUTPUT_PATH, "clases_transables_by_cluster_naics_2017.json"), "r"))

## Generamos dataframe para exportar a markdown
df_transables = pd.DataFrame([(k, ",".join([str(i) for i in v])) for k,v in transables.items()], columns = ["Cluster", "Clases NAICS 2017"])


## Exportamos tabla a formato markdown
with open(os.path.join(MD_BOOK_PATH, "porter_transables_cluster_clases_NAICS_2017.md"), "w") as file:
    file.write(df_transables.to_markdown(index = False))
