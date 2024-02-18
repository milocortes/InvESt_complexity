import pandas as pd 
import os 

from ciiu_agregacion import ciiu_agregacion

## Definimos paths
PATH_FILE = os.getcwd()
DATA_PATH = os.path.abspath(os.path.join(PATH_FILE, "..", "datos"))
OUTPUT_PATH = os.path.abspath(os.path.join(PATH_FILE, "..", "output"))

## Cargamos datos
ciiu_rev = pd.read_csv(os.path.join(DATA_PATH, "recodificacion_ciiu-rev-4.csv"))
sitc2_naics = pd.read_csv(os.path.join(DATA_PATH, "sitc-2_to_naics-2017.csv"))
intensivo = pd.read_excel(os.path.join(DATA_PATH,"intensivo_ec_ES2021.xlsx"))

intensivo_min = intensivo[['code', 'sitc_code', 'sitc_version', 'Name']]

## Agregamos a ciiu rev la división y sección
division = []
seccion = []

for ciiu in ciiu_rev.ciiu_nueva_cod:
    division.append(ciiu_agregacion[ciiu[:2]][0])
    seccion.append(ciiu_agregacion[ciiu[:2]][1])

ciiu_rev["division"] = division
ciiu_rev["seccion"] = seccion

## Guardamos resultados
ciiu_rev.to_csv(os.path.join(OUTPUT_PATH, "ciiu-rev-4-division-seccion.csv"), index = False)