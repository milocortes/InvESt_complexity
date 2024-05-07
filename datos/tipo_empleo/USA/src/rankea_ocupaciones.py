import pandas as pd 
import numpy as np
import glob
import os 

# Definimos rutas
PATH_FILE = os.getcwd()
DATA_PATH = os.path.abspath(os.path.join(PATH_FILE, "..", "output"))
OUTPUT_PATH = os.path.abspath(os.path.join(PATH_FILE, "..", "output"))
ONET_DATA_PATH = os.path.abspath(os.path.join(PATH_FILE, "..", "datos", "onet", "db_28_2_text"))

OUTPUT_EDUCACION_PATH =  os.path.join(OUTPUT_PATH, "iniciativa_educacion")

# Cargamos ciiu occ
occ_ciiu = pd.read_csv(os.path.join(DATA_PATH, "usa_ciiu_occ_empleo.csv"), low_memory=False)
# Nos quedamos sólo con las categorías de la taxonomía onet 2019
onet_taxonomia = pd.read_html("https://www.onetcenter.org/taxonomy/2019/list.html")[0]
onet_taxonomia = onet_taxonomia.rename(columns = {"O*NET-SOC 2019 Code" : "O*NET-SOC Code"})

onet_ocupaciones = {i[:7] :[] for i in onet_taxonomia["O*NET-SOC Code"].unique()} 

## Nos quedamos las ocupaciones que vienen en onet taxonomia 2019
occ_ciiu = occ_ciiu[occ_ciiu["occ_code"].isin(onet_ocupaciones.keys())]

occ_ciiu = occ_ciiu.merge(right = occ_ciiu[["ciiu", "coempleo"]].groupby("ciiu").sum().reset_index().rename(columns = {"coempleo":"ciiu_empleo_total"}), how="left", on="ciiu")
occ_ciiu = occ_ciiu.rename(columns = {"coempleo" : "empleo"})

occ_ciiu = occ_ciiu.query("empleo>0")
occ_ciiu["razon_ocupacion"] = occ_ciiu["empleo"]/occ_ciiu["ciiu_empleo_total"]

# Rankeamos por razon de ocupación
rankea_ocupaciones = []

for ciiu in occ_ciiu.ciiu.unique():
    parcial = occ_ciiu.query(f"ciiu=='{ciiu}'").sort_values(by="razon_ocupacion", ascending= False)
    parcial["ranking"] = range(1,parcial.shape[0]+1 )
    rankea_ocupaciones.append(parcial)

rankea_ocupaciones = pd.concat(rankea_ocupaciones, ignore_index=True)

### Agregamos información del nombre de los identificadores 

for i,j in onet_taxonomia.to_records(index = False):
    print(i)
    for ocupacion_id in onet_ocupaciones:
        if i.startswith(ocupacion_id):
            onet_ocupaciones[ocupacion_id].append(j)

onet_ocupaciones = {i:"/-/".join(j) for i,j in onet_ocupaciones.items()}
rankea_ocupaciones["onet_name"] = rankea_ocupaciones["occ_code"].replace(onet_ocupaciones)

isic = pd.read_csv("/home/milo/Documents/egtp/iniciativas/InvESt_complexity/datos/tipo_empleo/USA/datos/ISICRev4_NT_input.csv")
#### Cargamos diccionario de actividades ciiu-scian-naics
ciiu_scian = pd.read_html("https://milocortes.github.io/InvESt_complexity/contenido/datos_empleo.html")[0]


rankea_ocupaciones["ciiu_name"] = rankea_ocupaciones["ciiu"].replace({i:j for i,j in ciiu_scian[["CIIU (recodificación)", "CIIU nombre"]].to_records(index = False)})

### Para 3 digitos
occ_ciiu_3d = occ_ciiu[["occ_code", "ciiu", "empleo"]]
occ_ciiu_3d["ciiu"] = occ_ciiu_3d["ciiu"].apply(lambda x : x[:3])
occ_ciiu_3d = occ_ciiu_3d.groupby(["ciiu", "occ_code"]).sum().reset_index()
occ_ciiu_3d["ciiu_empleo_total"] = occ_ciiu_3d["ciiu"].replace( {i:j for i,j in occ_ciiu_3d[["ciiu", "empleo"]].groupby("ciiu").sum().reset_index().to_records(index=False)})
occ_ciiu_3d = occ_ciiu_3d.query("empleo>0")
occ_ciiu_3d["razon_ocupacion"] = occ_ciiu_3d["empleo"]/occ_ciiu_3d["ciiu_empleo_total"]

rankea_ocupaciones_3d = []

for ciiu in occ_ciiu_3d.ciiu.unique():
    parcial = occ_ciiu_3d.query(f"ciiu=='{ciiu}'").sort_values(by="razon_ocupacion", ascending= False)
    parcial["ranking"] = range(1,parcial.shape[0]+1 )
    rankea_ocupaciones_3d.append(parcial)

rankea_ocupaciones_3d = pd.concat(rankea_ocupaciones_3d, ignore_index=True)
rankea_ocupaciones_3d["onet_name"] = rankea_ocupaciones_3d["occ_code"].replace(onet_ocupaciones)
rankea_ocupaciones_3d["ciiu_name"] = rankea_ocupaciones_3d["ciiu"].apply(lambda x : x.replace("-","")).replace({i:j for i,j in isic[["Code", "ISIC Rev. 4 label"]].to_records(index = False)})


### Para 2 digitos
occ_ciiu_2d = occ_ciiu[["occ_code", "ciiu", "empleo"]]
occ_ciiu_2d["ciiu"] = occ_ciiu_2d["ciiu"].apply(lambda x : x[:2])
occ_ciiu_2d = occ_ciiu_2d.groupby(["ciiu", "occ_code"]).sum().reset_index()

occ_ciiu_2d["ciiu_empleo_total"] = occ_ciiu_2d["ciiu"].replace( {i:j for i,j in occ_ciiu_2d[["ciiu", "empleo"]].groupby("ciiu").sum().reset_index().to_records(index=False)})
occ_ciiu_2d = occ_ciiu_2d.query("empleo>0")
occ_ciiu_2d["razon_ocupacion"] = occ_ciiu_2d["empleo"]/occ_ciiu_2d["ciiu_empleo_total"]

rankea_ocupaciones_2d = []

for ciiu in occ_ciiu_2d.ciiu.unique():
    parcial = occ_ciiu_2d.query(f"ciiu=='{ciiu}'").sort_values(by="razon_ocupacion", ascending= False)
    parcial["ranking"] = range(1,parcial.shape[0]+1 )
    rankea_ocupaciones_2d.append(parcial)

rankea_ocupaciones_2d = pd.concat(rankea_ocupaciones_2d, ignore_index=True)
rankea_ocupaciones_2d["onet_name"] = rankea_ocupaciones_2d["occ_code"].replace(onet_ocupaciones)
rankea_ocupaciones_2d["ciiu_name"] = rankea_ocupaciones_2d["ciiu"].apply(lambda x : x.replace("-","")).replace({i:j for i,j in isic[["Code", "ISIC Rev. 4 label"]].to_records(index = False)})

## Guardamos salidas
rankea_ocupaciones.to_csv("ranking_ocupaciones_ciiu_4d.csv", index = False)
rankea_ocupaciones_2d.to_csv("ranking_ocupaciones_ciiu_2d.csv", index = False)
rankea_ocupaciones_3d.to_csv("ranking_ocupaciones_ciiu_3d.csv", index = False)