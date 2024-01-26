import pandas as pd 
import numpy as np
import json
import math
import os 

FILE_PATH = os.getcwd()
DATA_PATH = os.path.abspath(os.path.join(FILE_PATH, "..", "datos"))

## Carga datos censo economico 2019
censo = pd.read_csv(os.path.join(DATA_PATH, "censo-economico-2019", "censo_2019_empleo_clases.csv"))
## Carga datos arbol scian
arbol_scian = json.load(open(os.path.join(DATA_PATH, "scian-2023", "arbol_scian_actividades.json"), "r")) 
## Carga todas las clases de scian 2018
clases_scian = pd.read_csv(os.path.join(DATA_PATH, "scian-2023", "datos", "clases_scian_2018.csv"))
clases_scian = pd.DataFrame(columns = clases_scian["scian"])
clases_scian.columns = [str(i) for i in clases_scian.columns]

## Carga zonas metropolitanas
zm = pd.read_excel(os.path.join(DATA_PATH, "zonas-metropolitanas", "datos", "mpios_en_metropoli.xlsx"),  sheet_name = "real")
## Cargamos crosswalks 
cw_imss_scian = pd.read_csv(os.path.join(DATA_PATH, "cw-imss-scian", "cw_imss-scian.csv"))
cw_imss_scian["scian"] = cw_imss_scian["scian"].apply(lambda x : [i.lstrip() for i in x.split(",")]).to_list()
cw_imss_scian = cw_imss_scian.set_index("imss")

cw_imss_scian_agrega = pd.read_csv(os.path.join(DATA_PATH, "cw-imss-scian", "cw_imss-scian-agrega.csv"))

## Cargamos crosswalk ciiu-rev-4_scian-2018
ciiu_scian = json.load(open(os.path.join(DATA_PATH, "scian-ciiu", "ciiu-4_scian-2018.json"), "r"))
ciiu_scian = dict(sorted(ciiu_scian.items(), key=lambda item: int(item[0])))

## Agrega etiqueta de zm a los municipios del censo
zm["CVEGEO"] = zm["CVEGEO"].apply(lambda x: f"{x:05d}")
censo["CVEGEO"] = censo["ENTIDAD"].apply(lambda x : f"{x:02d}") + censo["MUNICIPIO"].apply(lambda x : f"{x:03d}")
censo["CLAVE_ZONA"] = censo["CVEGEO"].replace({i:j for i,j in zm[["CVEGEO", "CVE_ZONA"]].to_records(index=False)})

## Nos quedamos sólo con los municipios en ZM así como la entidad en agregado
censo = censo[censo["CLAVE_ZONA"].apply(lambda x : len(x)==7)]
censo["CODIGO"] = censo["CODIGO"].apply(lambda x : str(x))

# Zonas metropolitanas
censo_zm = censo[["CLAVE_ZONA", "CODIGO", "empleo"]].groupby(["CLAVE_ZONA", "CODIGO"]).sum().reset_index()

# Entidades
censo_entidad = censo[["ENTIDAD", "CODIGO", "empleo"]].groupby(["ENTIDAD", "CODIGO"]).sum().reset_index()
censo_entidad.columns = ['CLAVE_ZONA', 'CODIGO', 'empleo']
censo_entidad["CLAVE_ZONA"] = censo_entidad["CLAVE_ZONA"].apply(lambda x:f"{x:02}")

# Concatenamos ZM y Entidades
censo = pd.concat([censo_zm, censo_entidad], ignore_index = True)

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

    if datos_ubicacion["empleo"].sum()==0:
        valor = int(round(valor/len(clases_actividad),0))
        df_faltan_clases = pd.DataFrame({"CLAVE_ZONA" : [ubicacion]*len(clases_actividad), "CODIGO" : clases_actividad, "empleo_clase" : [0]*len(clases_actividad)})
        return df_faltan_clases

    datos_ubicacion["empleo_clase"] = ((datos_ubicacion["empleo"]/datos_ubicacion["empleo"].sum())*valor).apply(lambda x : round(x))

    faltan_clases = list(set(clases_actividad) - set(datos_ubicacion["CODIGO"]))
    df_faltan_clases = pd.DataFrame({"CLAVE_ZONA" : [ubicacion]*len(faltan_clases), "CODIGO" : faltan_clases, "empleo_clase" : [0]*len(faltan_clases)})

    if not df_faltan_clases.empty:
        datos_ubicacion = pd.concat([datos_ubicacion[["CLAVE_ZONA", "CODIGO", "empleo_clase"]] , df_faltan_clases[["CLAVE_ZONA", "CODIGO", "empleo_clase"]]], ignore_index = False)
        return datos_ubicacion[["CLAVE_ZONA", "CODIGO", "empleo_clase"]].groupby(["CLAVE_ZONA", "CODIGO"]).sum().reset_index()
    else:
        return datos_ubicacion[["CLAVE_ZONA", "CODIGO", "empleo_clase"]].groupby(["CLAVE_ZONA", "CODIGO"]).sum().reset_index()

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

    datos_ubicacion["empleo_clase"] = datos_ubicacion["empleo"]

    faltan_clases = list(set(clases_actividad) - set(datos_ubicacion["CODIGO"]))
    df_faltan_clases = pd.DataFrame({"CLAVE_ZONA" : [ubicacion]*len(faltan_clases), "CODIGO" : faltan_clases, "empleo_clase" : [0]*len(faltan_clases)})

    if not df_faltan_clases.empty:
        datos_ubicacion = pd.concat([datos_ubicacion[["CLAVE_ZONA", "CODIGO", "empleo_clase"]] , df_faltan_clases[["CLAVE_ZONA", "CODIGO", "empleo_clase"]]], ignore_index = False)
        return datos_ubicacion[["CLAVE_ZONA", "CODIGO", "empleo_clase"]].groupby(["CLAVE_ZONA", "CODIGO"]).sum().reset_index()
    else:
        return datos_ubicacion[["CLAVE_ZONA", "CODIGO", "empleo_clase"]].groupby(["CLAVE_ZONA", "CODIGO"]).sum().reset_index()

get_ponderadores_clases("09.1.01", ["112"], 100, censo, arbol_scian)
get_raw_censo("09.1.01", ["112"], censo, arbol_scian)

## Prueba con datos del imss de empleo a nivel Zona Metropolitana y Entidad
empleo_imss = pd.read_csv("/home/milo/Documents/egap/iniciativas/desarrollo-regional/el_salvador/datos/datos/empleo/MEX/datos/imss_csv/asg-2018-04-30.csv", sep="|", encoding='latin-1')

empleo_imss = empleo_imss[~empleo_imss["sector_economico_4"].isna()]
empleo_imss["sector_economico_4"] = empleo_imss["sector_economico_4"].apply(lambda x: str(int(x)))
empleo_imss.loc[empleo_imss.cve_entidad==9,"cve_municipio"]="CDMX"

# Nivel municipio para el cálculo a Zona Metropolitana
empleo_imss_municipio = empleo_imss[["cve_municipio", "sector_economico_4","ta"]].groupby(["cve_municipio", "sector_economico_4"]).sum().reset_index()
empleo_imss_entidad = empleo_imss[["cve_entidad", "sector_economico_4","ta"]].groupby(["cve_entidad", "sector_economico_4"]).sum().reset_index()
empleo_imss_entidad["cve_entidad"] = empleo_imss_entidad["cve_entidad"].apply(lambda x : f"{x:02}")

### Cargamos zonas metropolitanas y clasificación de imss
zm_imss_muni = pd.read_csv("/home/milo/Documents/egap/iniciativas/desarrollo-regional/el_salvador/datos/datos/empleo/MEX/datos/zonas_metropolitanas/zm_imss_muni.csv")
zm_imss_muni["CLAVE"] = zm_imss_muni["CLAVE"].apply(lambda x : x.split("-")[-1])

### Hacemos una consulta para la zona metropolitana de la cdmx 

def datos_imss_to_scian(zona_metropolitana : str,
                        datos_zonas_metropolitanas : pd.DataFrame,
                        datos_empleo_imss : pd.DataFrame,
                        datos_template_scian : pd.DataFrame,
                        datos_cw_imss_scian : pd.DataFrame,
                        datos_cw_imss_scian_agrega : pd.DataFrame,
                        tipo_region : str):
                        
    # Agrupamos de acuerdo al tipo de region
    if tipo_region == 'zm':
        zm = datos_empleo_imss[datos_empleo_imss["cve_municipio"].isin(datos_zonas_metropolitanas.query(f"CVE_ZONA=='{zona_metropolitana}'")["CLAVE"].to_list())]
    elif tipo_region == 'entidad':
        zm = datos_empleo_imss.query(f"cve_entidad=='{zona_metropolitana}'")

    #### Agregamos algunas actividades del imss
    zm["sector_economico_4"] = zm["sector_economico_4"].replace({str(i):str(j) for i,j in datos_cw_imss_scian_agrega.to_records(index=False)})
    zm = zm[["sector_economico_4","ta"]].groupby("sector_economico_4").sum()

    acumula_valores = []
    for i in zm.index:
        actividad_imss = i 
        valor_actividad = zm.loc[i,'ta']
        if int(actividad_imss) in cw_imss_scian.index.to_list():
            actividades_scian = datos_cw_imss_scian.loc[int(actividad_imss)].values[0]
            #print(f"Actividad imss : {actividad_imss} . Actividad scian : {actividades_scian} --> {valor_actividad}")
            acumula_valores.append(get_ponderadores_clases(zona_metropolitana, actividades_scian, valor_actividad, censo, arbol_scian))

    zm_scian = pd.concat(acumula_valores, ignore_index = True)
    zm_scian = zm_scian.groupby(["CLAVE_ZONA", "CODIGO"]).sum().reset_index()
    zm_scian = zm_scian[["CODIGO", "empleo_clase"]].set_index("CODIGO").transpose().reset_index(drop=True)
    zm_scian = pd.concat([datos_template_scian, zm_scian])

    return pd.concat([pd.DataFrame({"zm" : [zona_metropolitana]}), zm_scian], axis = 1).replace(np.nan, 0)

## Probamos la función para una zona metropolitana y una entidad
datos_imss_to_scian('09.1.01', zm_imss_muni, empleo_imss_municipio, clases_scian, cw_imss_scian, cw_imss_scian_agrega, "zm")
datos_imss_to_scian('09', zm_imss_muni, empleo_imss_entidad, clases_scian, cw_imss_scian, cw_imss_scian_agrega, "entidad")


### Ejecuta función para todas las zm
acumula_zm_scian = []
for i, zona_metropolitana in enumerate(zm_imss_muni.CVE_ZONA.unique()):
    print(f"{i}/{len(zm_imss_muni.CVE_ZONA.unique())}  {zona_metropolitana}")
    acumula_zm_scian.append(datos_imss_to_scian(zona_metropolitana, zm_imss_muni, empleo_imss, clases_scian, cw_imss_scian, cw_imss_scian_agrega, "zm"))

zonas_metropolitanas_scian = pd.concat(acumula_zm_scian, ignore_index = True)

### Ejecuta función para todas las entidades
acumula_entidad_scian = []
for i, entidad in enumerate([f"{i:02}"for i in range(1,33)]):
    print(f"{i}/{len(range(32))}  {entidad}")
    acumula_entidad_scian.append(datos_imss_to_scian(entidad, zm_imss_muni, empleo_imss_entidad, clases_scian, cw_imss_scian, cw_imss_scian_agrega, "entidad"))

entidades_scian = pd.concat(acumula_entidad_scian, ignore_index = True)


### Genera dataframe con clasificación ciiu
zonas_metropolitanas_ciiu = pd.DataFrame()

zonas_metropolitanas_ciiu["zm"] = zonas_metropolitanas_scian["zm"]

for ciiu, scian in ciiu_scian.items():
    zonas_metropolitanas_ciiu[f"{int(ciiu):04}"] = zonas_metropolitanas_scian[scian].sum(axis = 1)

#######################################
#######################################
### PRUEBAS
#######################################
#######################################

zm_imss_muni.query(f"CVE_ZONA=={zona_metropolitana}")["CLAVE"].to_list()
zmvm = empleo_imss[empleo_imss["cve_municipio"].isin(zm_imss_muni.query("CVE_ZONA=='09.1.01'")["CLAVE"].to_list())]

#### Agregamos algunas actividades del imss
zmvm["sector_economico_4"] = zmvm["sector_economico_4"].replace({str(i):str(j) for i,j in cw_imss_scian_agrega.to_records(index=False)})
zmvm_scian
zmvm = zmvm[["sector_economico_4","ta"]].groupby("sector_economico_4").sum()

acumula_valores = []
for i in zmvm.index:
    actividad_imss = i 
    valor_actividad = zmvm.loc[i,'ta']
    if int(actividad_imss) in cw_imss_scian.index.to_list():
        actividades_scian = cw_imss_scian.loc[int(actividad_imss)].values[0]
        print(f"Actividad imss : {actividad_imss} . Actividad scian : {actividades_scian} --> {valor_actividad}")
        print(get_ponderadores_clases(zona_metropolitana, actividades_scian, valor_actividad, censo, arbol_scian))
        acumula_valores.append(get_ponderadores_clases(zona_metropolitana, actividades_scian, valor_actividad, censo, arbol_scian))

zmvm_scian = pd.concat(acumula_valores, ignore_index = True)
zmvm_scian = zmvm_scian.groupby(["CLAVE_ZONA", "CODIGO"]).sum().reset_index()
zmvm_scian = zmvm_scian[["CODIGO", "empleo_clase"]].set_index("CODIGO").transpose().reset_index(drop=True)
zmvm_scian = pd.concat([clases_scian, zmvm_scian])

actividad_imss = "1101"
valor_actividad = zmvm.loc[i,'ta']
actividades_scian = cw_imss_scian.loc[int(actividad_imss)].values[0]

ubicacion = zona_metropolitana
actividad_scian = actividades_scian
valor = valor_actividad
datos = censo
arbol = arbol_scian

