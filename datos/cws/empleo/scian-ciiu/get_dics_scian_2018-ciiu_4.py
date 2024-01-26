import pandas as pd 
import numpy as np 
import json 

df = pd.read_excel("tablaxiv.xls", sheet_name="SCIAN México 2018 - CIIU Rev. 4", skiprows=3, usecols="A,B,E,F")
df = df.iloc[:-6]
df.columns = ["scian", "descripcion_scian", "ciiu", "descripcion_ciiu"]
df = df[~((df.scian.isna()) & (df.ciiu.isna()))]
df = df[~df.ciiu.isna()]
df["ciiu"] = df["ciiu"].astype(int).astype(str)
df = df[~df["scian"].isin(["XXXXXX", "YYYYYY"])]

ciiu_descripcion = {i:j for i,j in df[["ciiu", "descripcion_ciiu"]].to_records(index = False)}

## Completamos nan con el registro anterior del scian
cubre_nan_scian = []
scian_nan = df["scian"].to_list()

for scian in scian_nan:
    if np.isnan(scian):
        cubre_nan_scian.append(cubre_nan_scian[-1])
    else:
        cubre_nan_scian.append(scian)

df["scian"] = cubre_nan_scian

df["scian"] = df["scian"].astype(int).astype(str)



df["ciiu"] = df["ciiu"].apply(lambda x : f"{int(x):04}")

ciiu_scian = {i : [] for i in df["ciiu"].unique()}

for scian, ciiu in df[["scian", "ciiu"]].to_records(index=False):
    ciiu_scian[ciiu].append(scian)

## Guardamos el crosswalk
with open("ciiu-4_scian-2018.json", "w") as file:
    json.dump(ciiu_scian, file)

## Verificamos cuantas clases tienen en común las actividades ciiu
scian_compartidas_ciiu = {}

for ciiu, scian in ciiu_scian.items():
    for ciiu_otro, scian_otro in ciiu_scian.items():
        if ciiu!=ciiu_otro:
            clases_compartidas = set(scian).intersection(scian_otro)
            if clases_compartidas:
                scian_compartidas_ciiu.setdefault(ciiu, {})
                scian_compartidas_ciiu[ciiu][ciiu_otro] = list(clases_compartidas)

### Verifica tamaño de repetidos con respecto al empleo total
zm = pd.read_csv("/home/milo/Documents/egap/iniciativas/desarrollo-regional/el_salvador/datos/datos/empleo/MEX/test/src/zonas_metropolitanas_scian_2018.csv")
zm = zm.query("zm=='09.1.01'")
zm = zm[zm.columns[1:]]

empleo_total = zm.sum().sum()

resumen = pd.DataFrame([(ciiu, ciiu_descripcion[ciiu], ciiu_comparten, ",".join(clases_comparten), (zm[clases_comparten].sum().values[0]/empleo_total)*100) 
                        for ciiu,ciiu_comparten_todos in scian_compartidas_ciiu.items() 
                        for ciiu_comparten, clases_comparten in ciiu_comparten_todos.items()],
                        columns = ["ciiu", "ciiu_descripcion","ciiu_clases_comparten", "clases_comparten", "razon_empleo_total"]
                        )

resumen = resumen.query("razon_empleo_total >0.0")
resumen.to_csv("resumen_ciiu_comparten_clases.csv", index = False)
resumen_problematicas = resumen.query("razon_empleo_total > 1.0")
resumen_problematicas.to_csv("resumen_ciiu_comparten_clases_1_por_ciento.csv", index = False)