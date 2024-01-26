import pandas as pd 
import numpy as np 
import json 

## Cargamos cw entre NAICS 2017 e ISIC Rev 4
isic_naics_excel = pd.read_excel("datos/ISIC_4_to_2017_NAICS.xlsx", sheet_name='ISIC 4 to NAICS 17 technical', usecols = "B,E")
isic_naics_excel.columns = ["isic", "naics"]

isic_naics_excel = isic_naics_excel.astype(str)
isic_naics_excel = isic_naics_excel.query("naics!='0'")

tmp_act = ""

isic_4_to_naics_2017 = {i:[] for i in isic_naics_excel["isic"]}

for i,j in zip(isic_naics_excel["isic"],isic_naics_excel["naics"]):
    
    if tmp_act!=i:
        tmp_act = i
    
    isic_4_to_naics_2017[tmp_act].append(j) 

## Guardamos el crosswalk
json.dump(isic_4_to_naics_2017, open("output/isic_4_to_naics_2017.json", "w"))

## Obtenemos todas las clases de NAICS 2017
juan = []

for i in isic_4_to_naics_2017.values():
    juan.extend(i)

juan = list(set(juan))


## Cargamos cw entre NAICS 2017 y NAICS 2012
naics_2017_naics_2012 = pd.read_excel("datos/2017_to_2012_NAICS_Changes_Only.xlsx", sheet_name='Sheet1', usecols = "A,D", skiprows = 1)
naics_2017_naics_2012.columns = ["naics_2017", "naics_2012"]
naics_2017_naics_2012 = naics_2017_naics_2012[(~naics_2017_naics_2012["naics_2017"].isnull()) & (~naics_2017_naics_2012["naics_2012"].isnull())]

naics_2017_to_naics_2012 = {}

for i,j in naics_2017_naics_2012.to_records(index = False):
    naics_2017_to_naics_2012[str(i)] = [i for i in str(j).replace("*","").split("\n") if i!=""]

## NOTA: voy a dejar el mapeo '211120' -> '211111' y voy a quitar a '211111' de '211130': ['211111', '211112']
naics_2017_to_naics_2012["211130"].remove('211111')

## Guardamos el crosswalk
json.dump(naics_2017_to_naics_2012, open("output/naics_2017_to_naics_2012.json", "w"))

## Hacemos inverso NAICS 2012 a NAICS 2017
naics_2012_to_naics_2017 = {}

for k,v in naics_2017_to_naics_2012.items():
    for j in v:
        naics_2012_to_naics_2017[j] = k


#### Hacemos una prueba del cv naics 2012 a naics 2017
for i in range(12, 22):
    df = pd.read_csv(f"/home/milo/Documents/egap/iniciativas/desarrollo-regional/el_salvador/datos/datos/empleo/USA/datos/cbp/cbp{i}msa.txt")
    df.columns = [i.lower() for i in df.columns]
    naics = [i for i in df["naics"].unique() if  all([i.isnumeric() for j in i])]

    df = df[df.naics.isin(naics)]



    print(f"{2000+i}")
    print(len(naics))
    print(len(set(juan).intersection(naics)))
    print("")