import pandas as pd 
import numpy as np 
import json 

scian = pd.read_excel("datos/scian_2018_categorias_y_productos.xlsx", sheet_name='CLASE', usecols = "A,B", skiprows = 1)
scian = scian[(~scian["Código"].isna()) & (~scian["Título"].isna())]
scian["Código"] = scian["Código"].astype(int).astype(str)

scian.columns = ["scian","descripcion"]

scian_clases = scian.scian.to_list()

arbol_scian = {}

for digito in range(2,6):
    print(digito)
    actividades = list(set([i[:digito]for i in scian_clases]))
    sub_actividades = list(set([i[:digito+1]for i in scian_clases]))
    for actividad in actividades:
        arbol_scian[actividad] = [i for i in sub_actividades if i.startswith(actividad)]

json.dump(arbol_scian, open("arbol_scian_actividades.json", "w"))
