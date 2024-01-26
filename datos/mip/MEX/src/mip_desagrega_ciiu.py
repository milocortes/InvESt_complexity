### Cargamos paquetes para hacer consultas a las clases por zona metropolitana y entidad
import pandas as pd 
import numpy as np
import json
import math
import os 
import re

FILE_PATH = os.getcwd()
CW_PATH = os.path.abspath(os.path.join(FILE_PATH, *[".."]*3, "cws", "empleo"))
DATA_PATH = os.path.abspath(os.path.join(FILE_PATH, "..", "datos"))
OUTPUT_PATH = os.path.abspath(os.path.join(FILE_PATH, "..", "output"))

## Carga datos censo economico 2019
censo = pd.read_csv(os.path.join(CW_PATH, "censo-economico-2019", "censo_2019_producto_clases.csv"))

## Todo el país
censo_mex = pd.DataFrame({"CLAVE_ZONA" : ["MEX"]*censo.shape[0]}) 
censo_mex = pd.concat([censo_mex, censo[["CODIGO", "producto"]].copy()], axis = 1)
censo_mex = censo_mex.groupby(["CLAVE_ZONA", "CODIGO"]).sum().reset_index()
censo_mex["CODIGO"] = censo_mex["CODIGO"].apply(lambda x : str(x))

## Carga datos arbol scian
arbol_scian = json.load(open(os.path.join(CW_PATH, "scian-2023", "arbol_scian_actividades.json"), "r")) 
## Carga todas las clases de scian 2018
clases_scian = pd.read_csv(os.path.join(CW_PATH, "scian-2023", "datos", "clases_scian_2018.csv"))
clases_scian = pd.DataFrame(columns = clases_scian["scian"])
clases_scian.columns = [str(i) for i in clases_scian.columns]

## Carga zonas metropolitanas
zm = pd.read_excel(os.path.join(CW_PATH, "zonas-metropolitanas", "datos", "mpios_en_metropoli.xlsx"),  sheet_name = "real")
## Cargamos crosswalks 
cw_imss_scian = pd.read_csv(os.path.join(CW_PATH, "cw-imss-scian", "cw_imss-scian.csv"))
cw_imss_scian["scian"] = cw_imss_scian["scian"].apply(lambda x : [i.lstrip() for i in x.split(",")]).to_list()
cw_imss_scian = cw_imss_scian.set_index("imss")

cw_imss_scian_agrega = pd.read_csv(os.path.join(CW_PATH, "cw-imss-scian", "cw_imss-scian-agrega.csv"))

## Cargamos el crosswalk entre ciiu y scian
cw_ciiu_scian = json.load(open(os.path.join(CW_PATH, "ciiu-recodificacion-dario-diodato", "output", "ciiu_recodificado_scian_2018.json"), "r"))

## Cargamos crosswalk ciiu-rev-4_scian-2018
ciiu_scian = json.load(open(os.path.join(CW_PATH, "scian-ciiu", "ciiu-4_scian-2018.json"), "r"))
ciiu_scian = dict(sorted(ciiu_scian.items(), key=lambda item: int(item[0])))

## Agrega etiqueta de zm a los municipios del censo
zm["CVEGEO"] = zm["CVEGEO"].apply(lambda x: f"{x:05d}")
censo["CVEGEO"] = censo["ENTIDAD"].apply(lambda x : f"{x:02d}") + censo["MUNICIPIO"].apply(lambda x : f"{x:03d}")
censo["CLAVE_ZONA"] = censo["CVEGEO"].replace({i:j for i,j in zm[["CVEGEO", "CVE_ZONA"]].to_records(index=False)})

## Nos quedamos sólo con los municipios en ZM así como la entidad en agregado
censo = censo[censo["CLAVE_ZONA"].apply(lambda x : len(x)==7)]
censo["CODIGO"] = censo["CODIGO"].apply(lambda x : str(x))

# Zonas metropolitanas
censo_zm = censo[["CLAVE_ZONA", "CODIGO", "producto"]].groupby(["CLAVE_ZONA", "CODIGO"]).sum().reset_index()

# Entidades
censo_entidad = censo[["ENTIDAD", "CODIGO", "producto"]].groupby(["ENTIDAD", "CODIGO"]).sum().reset_index()
censo_entidad.columns = ['CLAVE_ZONA', 'CODIGO', 'producto']
censo_entidad["CLAVE_ZONA"] = censo_entidad["CLAVE_ZONA"].apply(lambda x:f"{x:02}")

# Concatenamos ZM y Entidades
censo = pd.concat([censo_zm, censo_entidad, censo_mex], ignore_index = True)

def get_clases(actividad_scian : str, arbol : dict, acumula_clases : list) -> list:

    if len(actividad_scian) == 6:
        if not actividad_scian in acumula_clases:
            acumula_clases.append(actividad_scian)
    
    else:
        for i in arbol[actividad_scian]:
            get_clases(i, arbol, acumula_clases)

def get_ponderadores_clases(ubicacion : str, 
                            actividad_scian : list, 
                            valor : int, 
                            datos : pd.DataFrame, 
                            arbol : dict):
    datos_ubicacion = datos.query(f"CLAVE_ZONA == '{ubicacion}'")
    clases_actividad = []

    for act_scian in actividad_scian:
        get_clases(act_scian, arbol, clases_actividad)

    clases_actividad = list(set(clases_actividad))

    datos_ubicacion = datos_ubicacion[datos_ubicacion["CODIGO"].isin(clases_actividad)]

    if datos_ubicacion["producto"].sum()==0:
        valor = int(round(valor/len(clases_actividad),0))
        df_faltan_clases = pd.DataFrame({"CLAVE_ZONA" : [ubicacion]*len(clases_actividad), "CODIGO" : clases_actividad, "producto_clase" : [0]*len(clases_actividad)})
        return df_faltan_clases

    datos_ubicacion["producto_clase"] = ((datos_ubicacion["producto"]/datos_ubicacion["producto"].sum())*valor).apply(lambda x : round(x))

    faltan_clases = list(set(clases_actividad) - set(datos_ubicacion["CODIGO"]))
    df_faltan_clases = pd.DataFrame({"CLAVE_ZONA" : [ubicacion]*len(faltan_clases), "CODIGO" : faltan_clases, "producto_clase" : [0]*len(faltan_clases)})

    if not df_faltan_clases.empty:
        datos_ubicacion = pd.concat([datos_ubicacion[["CLAVE_ZONA", "CODIGO", "producto_clase"]] , df_faltan_clases[["CLAVE_ZONA", "CODIGO", "producto_clase"]]], ignore_index = False)
        return datos_ubicacion[["CLAVE_ZONA", "CODIGO", "producto_clase"]].groupby(["CLAVE_ZONA", "CODIGO"]).sum().reset_index()
    else:
        return datos_ubicacion[["CLAVE_ZONA", "CODIGO", "producto_clase"]].groupby(["CLAVE_ZONA", "CODIGO"]).sum().reset_index()

def get_raw_censo(ubicacion : str, 
                  actividad_scian : list, 
                  datos : pd.DataFrame, 
                  arbol : dict):

    datos_ubicacion = datos.query(f"CLAVE_ZONA == '{ubicacion}'")
    clases_actividad = []

    for act_scian in actividad_scian:
        get_clases(act_scian, arbol, clases_actividad)

    clases_actividad = list(set(clases_actividad))

    datos_ubicacion = datos_ubicacion[datos_ubicacion["CODIGO"].isin(clases_actividad)]

    datos_ubicacion["producto_clase"] = datos_ubicacion["producto"]

    faltan_clases = list(set(clases_actividad) - set(datos_ubicacion["CODIGO"]))
    df_faltan_clases = pd.DataFrame({"CLAVE_ZONA" : [ubicacion]*len(faltan_clases), "CODIGO" : faltan_clases, "producto_clase" : [0]*len(faltan_clases)})

    if not df_faltan_clases.empty:
        datos_ubicacion = pd.concat([datos_ubicacion[["CLAVE_ZONA", "CODIGO", "producto_clase"]] , df_faltan_clases[["CLAVE_ZONA", "CODIGO", "producto_clase"]]], ignore_index = False)
        datos_ubicacion = datos_ubicacion[["CLAVE_ZONA", "CODIGO", "producto_clase"]].groupby(["CLAVE_ZONA", "CODIGO"]).sum().reset_index()

        return datos_ubicacion
    else:
        return datos_ubicacion[["CLAVE_ZONA", "CODIGO", "producto_clase"]].groupby(["CLAVE_ZONA", "CODIGO"]).sum().reset_index()

#### Cargamos datos de la MIP de mexico
mip = pd.read_excel(os.path.join(DATA_PATH, "MIP_53.xlsx"), index_col=None, na_values=['-'],header =0, skiprows=5, nrows=263,usecols = "D:JF")

ramas_dict = {re.findall(r'^\D*(\d+)', rama)[0]:rama[7:] for rama in mip.columns}

# Renombramos el nombre de las columnas
mip.columns = ramas_dict.keys()

# Asignamos índice de filas a las ramas scian
mip.index = ramas_dict.keys()

#### Construimos la matriz a nivel de clase
def build_from_to_clases(rama_from : str, rama_to : str):
    flujo_ramas = mip.loc[rama_from, rama_to]
    reparte_rama_from = get_ponderadores_clases("MEX", [rama_from], flujo_ramas, censo, arbol_scian)[["CODIGO", "producto_clase"]]
    reparte_rama_from.columns = ["rama_from", "producto_clase"]
    
    if  reparte_rama_from["producto_clase"].sum()==0:
        reparte_rama_from["producto_clase"] = flujo_ramas/reparte_rama_from.shape[0]

    reparte_rama_to = get_raw_censo("MEX", [rama_to], censo, arbol_scian)[["CODIGO", "producto_clase"]]
    reparte_rama_to.columns = ["rama_to", "producto_clase"]

    if reparte_rama_to["producto_clase"].sum()==0:
        reparte_rama_to["producto_clase"] = 1
    reparte_rama_to["share_producto_clase"] = reparte_rama_to["producto_clase"]/reparte_rama_to["producto_clase"].sum()
    reparte_rama_to = reparte_rama_to[["rama_to", "share_producto_clase"]]
    

    reune = reparte_rama_from.merge(right=reparte_rama_to, how = "cross")

    
    reune["value"] = reune["producto_clase"]*reune["share_producto_clase"]

    return reune[["rama_from", "rama_to", "value"]]

acumula_reparticion = []

for i in mip.columns:
    print(i)
    for j in mip.columns:
        acumula_reparticion.append(
            build_from_to_clases(i,j)
        )

mip_clases = pd.concat(acumula_reparticion, ignore_index=True)

mip_clases_mat = mip_clases.pivot(index = "rama_from", columns = "rama_to", values = "value")
mip_clases_mat

# Reconstruye matriz rama a partir de matriz clases
acumula = []

for rama_from in mip.columns:
    for rama_to in mip.columns:
        clases_actividad_from = []
    
        for act_scian in [rama_from]:
            get_clases(act_scian, arbol_scian, clases_actividad_from)

        clases_actividad_to = []
    
        for act_scian in [rama_to]:
            get_clases(act_scian, arbol_scian, clases_actividad_to)
            
        clases_coinciden_from = list(set(mip_clases_mat.index).intersection(clases_actividad_from))
        clases_coinciden_to = list(set(mip_clases_mat.index).intersection(clases_actividad_to))

        acumula.append((rama_from, rama_to, mip_clases_mat.loc[clases_coinciden_from, clases_coinciden_to].sum().sum()))

mip_recostruida = pd.DataFrame(acumula, columns = ["from", "to", "values"]).pivot(index = "from", columns = "to", values = "values")

## Construimos matriz en clasificación CIIU-Recodificado
acumula_ciiu = []

for rama_from, clases_from in cw_ciiu_scian.items():
    print(rama_from)
    for rama_to, clases_to in cw_ciiu_scian.items():
        clases_from_coinciden = list(set(clases_from).intersection(mip_clases_mat.columns))
        clases_to_coinciden = list(set(clases_to).intersection(mip_clases_mat.columns))

        acumula_ciiu.append(
            (rama_from, rama_to, mip_clases_mat.loc[clases_from_coinciden, clases_to_coinciden].sum().sum())
        )

mip_ciiu = pd.DataFrame(acumula_ciiu, columns = ["from", "to", "value"]).pivot(index = "from", columns = "to", values = "value")

### Guardamos resultados
mip_clases_mat = mip_clases_mat.reset_index().rename(columns = {'rama_from':"actividad"})
mip_ciiu = mip_ciiu.reset_index().rename(columns={"from":"actividad"})

mip_clases_mat.to_csv(os.path.join(OUTPUT_PATH, "mip_clases_scian_2018.csv"), index = False)
mip_ciiu.to_csv(os.path.join(OUTPUT_PATH, "mip_ciiu.csv"), index = False)

