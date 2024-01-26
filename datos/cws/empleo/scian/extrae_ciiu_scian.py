import pandas as pd 
import numpy as np 

ciiu_scian_excel = pd.read_excel("tablaxvi CIIU-SCIAN.xlsx", sheet_name='CIIU Rev.4-SCIAN 2023', skiprows=3, usecols = "A,E")

cw_ciiu_scian = {}
for ciiu,scian in ciiu_scian_excel.to_records(index=False):
    ciiu = str(ciiu)
    scian = str(scian)
    if ciiu.isnumeric() and scian.isnumeric():
        ciiu_key = ciiu
        cw_ciiu_scian[ciiu] = [scian]
    elif scian.isnumeric():
        cw_ciiu_scian[ciiu_key].append(scian)
    else:
        pass

acumula = []
for i,j in cw_ciiu_scian.items():
    for k in j:
        acumula.append((i,k))

# Guardamos cw en csv
df_cw_ciiu_scian = pd.DataFrame(acumula, columns=["ciiu-4d","scian-6d"])
df_cw_ciiu_scian.to_csv("ciiu-4d_scian-6d.csv", index = False)

# Guardamos cw en json
import json

# ciiu-4d ---> scian-6d
json.dump(cw_ciiu_scian, open("ciiu-4d_scian-6d.json", "w"))


# scian-6d ---> ciiu-4d
cw_scian_ciiu = {}

for k,v in cw_ciiu_scian.items():
    for i in v:
        cw_scian_ciiu[i] = k

json.dump(cw_scian_ciiu, open("scian-6d_ciiu-4d.json", "w"))