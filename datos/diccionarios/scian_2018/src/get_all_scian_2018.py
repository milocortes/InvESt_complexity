# Cargamos paquetes
import pandas as pd 
import numpy as np
import os 

# Definimos rutas
FILE_PATH = os.getcwd()
DATA_PATH = os.path.abspath(os.path.join(FILE_PATH, "..", "datos"))
OUTPUT_PATH = os.path.abspath(os.path.join(FILE_PATH, "..", "output"))
DATA_FILE_PATH = os.path.join(DATA_PATH, "tablaxiii.xls")

# Cargamos datos
scian = pd.read_excel(DATA_FILE_PATH, sheet_name = "SCIAN2018-SCIAN2013 ", usecols = "A", skiprows=3).iloc[:,0].to_list()
