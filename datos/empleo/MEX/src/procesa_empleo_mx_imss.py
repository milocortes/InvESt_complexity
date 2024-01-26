import pandas as pd 
import numpy as np 
import glob 
import os
import json

import h5py

import yaml

from ligas_descarga import ligas_imss_empleo
from desagrega_imss_scian_censo import get_ponderadores_clases, datos_imss_to_scian, censo_zm, censo_entidad, arbol_scian, clases_scian, cw_imss_scian, cw_imss_scian_agrega, get_raw_censo

import warnings
warnings.filterwarnings("ignore")

# Definimos el periodo de cobertura
anio_inicio = 2011
anio_fin = 2023
#anio_inicio = 2019
#anio_fin = 2020

# Definimos rutas
PATH_FILE = os.getcwd()
DATA_PATH = os.path.abspath(os.path.join(PATH_FILE, "..", "datos","imss_csv"))
OUTPUT_PATH = os.path.abspath(os.path.join(PATH_FILE, "..", "output"))
DOCS_PATH = os.path.abspath(os.path.join(PATH_FILE, "..", "docs"))
CW_PATH = os.path.abspath(os.path.join(PATH_FILE, *[".."]*3, "cws", "empleo"))

## Obtenemos los nombres de los archivos ordenados por años
ligas_imss_empleo_anios = {str(i) : {k[-5:] : v for k,v in ligas_imss_empleo.items() if str(i) in k} for i in range(anio_inicio, anio_fin+1)}

## Obtenemos el cw de las zonas metropolitanas
zm_imss_muni = pd.read_csv(os.path.abspath(os.path.join(PATH_FILE, "..", "datos","zonas_metropolitanas", "zm_imss_muni.csv")) )
zm_cw = {i : j  for i,j in zip(zm_imss_muni["CLAVE"],zm_imss_muni["CVE_ZONA"])}
zm_imss_muni["CLAVE"] = zm_imss_muni["CLAVE"].apply(lambda x : x.split("-")[-1])

## Cargamos el crosswalk entre ciiu y scian
cw_ciiu_scian = json.load(open(os.path.join(CW_PATH, "ciiu-recodificacion-dario-diodato", "output", "ciiu_recodificado_scian_2018.json"), "r"))

## Obtenemos el diccionario de actividades del imss
diccionario_act = pd.read_csv(os.path.abspath(os.path.join("..", "datos", "diccionario_actividades.csv")))
tags_actividades_imss = [str(n).encode("ascii", "ignore") for n in ["cve_ent"] + diccionario_act.sector_economico_4_4_pos.to_list()]

## Obtenemos el diccionario de actividades scian
tags_actividades_scian = []

for i in cw_ciiu_scian.values():
    tags_actividades_scian.extend(i)
tags_actividades_scian.sort()

tags_actividades_scian = [str(n).encode("ascii", "ignore") for n in ["zm"] + tags_actividades_scian]

## Obtenemos el diccionario de actividades ciiu
tags_actividades_ciiu = list(cw_ciiu_scian.keys())
tags_actividades_ciiu.sort()
tags_actividades_ciiu = [str(n).encode("ascii", "ignore") for n in ["zm"] + tags_actividades_ciiu]

## Función que carga csv en dataframe
def get_data_by_file(file_name : str) -> np.array:

    print("Cargando datos de empleo del IMSS")
    df_empleo_imss = pd.read_csv(file_name, sep="|", encoding='latin-1')
    df_empleo_imss = df_empleo_imss[~df_empleo_imss["sector_economico_4"].isna()]
    
    # Entidad en clasificación IMSS
    df_empleo_imss_entidad_matrix = df_empleo_imss[["cve_entidad", "sector_economico_4", "ta"]]
    df_empleo_imss_entidad_matrix = df_empleo_imss_entidad_matrix.groupby(["cve_entidad","sector_economico_4"]).sum().reset_index()
    df_empleo_imss_entidad_matrix.sector_economico_4 = df_empleo_imss_entidad_matrix.sector_economico_4.apply(lambda x : f"{int(x):04}")
    #df.cve_entidad = df.cve_entidad.apply(lambda x : f"{int(x):02}")

    df_empleo_imss_entidad_matrix = df_empleo_imss_entidad_matrix.pivot(index = ["cve_entidad"], columns = ["sector_economico_4"], values = "ta").replace(np.nan,0).reset_index()

    #### ZONA METROPOLITANA
    # etiquetamos a la cdmx
    df_empleo_imss.loc[(df_empleo_imss["cve_entidad"]==9) & (df_empleo_imss["cve_municipio"].isna()), "cve_municipio"] = "CDMX"

    df_empleo_imss = df_empleo_imss[["cve_entidad", "cve_municipio", "sector_economico_4", "ta"]]
    df_empleo_imss = df_empleo_imss.groupby(["cve_entidad", "cve_municipio", "sector_economico_4"]).sum().reset_index()
    df_empleo_imss["CLAVE"] = df_empleo_imss["cve_entidad"].apply(lambda x : str(x)) + "-" + df_empleo_imss["cve_municipio"]
    print("Remplazando ZM")
    print("---- Este paso es tardado -----")
    df_empleo_imss["zm"] = df_empleo_imss["CLAVE"].replace(zm_cw)

    # Nos quedamos con el empleo total por zona metropolitana
    df_empleo_imss_zm = df_empleo_imss[df_empleo_imss["zm"].apply(lambda x : len(x)==7)]
    ## Generamos un dataframe para hacer el crosswalk entre imss y scian
    df_empleo_imss_zm = df_empleo_imss_zm[~df_empleo_imss_zm["sector_economico_4"].isna()][["cve_municipio", "sector_economico_4", "ta"]]

    ## Generamos el cw de imss a scian para cada zona metropolitana 
    acumula_zm_scian = []
    zonas_metropolitanas_claves = list(set(zm_cw.values()))
    zonas_metropolitanas_claves.sort()

    print("Procesando crosswalk a nivel ZM IMSS-SCIAN")
    for i, zona_metro_index in enumerate(zonas_metropolitanas_claves):
        print(f"{i}/{len(set(zm_cw.values()))}  {zona_metro_index}")
        acumula_zm_scian.append(datos_imss_to_scian(zona_metro_index, zm_imss_muni, df_empleo_imss_zm, clases_scian, cw_imss_scian, cw_imss_scian_agrega, "zm"))

    zonas_metropolitanas_scian = pd.concat(acumula_zm_scian, ignore_index = True)
    zonas_metropolitanas_scian["zm"] = zonas_metropolitanas_scian["zm"].apply(lambda x : int(x.replace(".","")))

    ## Generamos el cw de scian a ciiu para cada zona metropolitana
    zonas_metropolitanas_ciiu = zonas_metropolitanas_scian[["zm"]]
    
    for ciiu, scian_clases in cw_ciiu_scian.items():
        clases_coinciden_scian = list(set(zonas_metropolitanas_scian.columns).intersection(scian_clases))
        clases_coinciden_scian.sort()

        zonas_metropolitanas_ciiu[ciiu] = zonas_metropolitanas_scian[clases_coinciden_scian].sum(axis = 1)

    ## Generamos un dataframe para quedarnos con la clasificación del imss a nivel zona metropolitana
    df_empleo_imss_zm_matrix = df_empleo_imss[~df_empleo_imss["sector_economico_4"].isna()][["zm", "sector_economico_4", "ta"]]
    df_empleo_imss_zm_matrix = df_empleo_imss_zm_matrix[df_empleo_imss_zm_matrix["zm"].apply(lambda x : len(x)==7)]
    df_empleo_imss_zm_matrix = df_empleo_imss_zm_matrix.groupby(["zm","sector_economico_4"]).sum().reset_index()
    df_empleo_imss_zm_matrix.sector_economico_4 = df_empleo_imss_zm_matrix.sector_economico_4.apply(lambda x : f"{int(x):04}")
    #df.cve_entidad = df.cve_entidad.apply(lambda x : f"{int(x):02}")

    df_empleo_imss_zm_matrix = df_empleo_imss_zm_matrix.pivot(index = ["zm"], columns = ["sector_economico_4"], values = "ta").replace(np.nan,0).reset_index()
    df_empleo_imss_zm_matrix["zm"] = df_empleo_imss_zm_matrix["zm"].apply(lambda x : int(x.replace(".","")))

    #### ENTIDAD
    ### Generamos el crosswalk IMSS --> SCIAN a nivel ENTIDAD
    ## Generamos un dataframe para hacer el crosswalk entre imss y scian
    df_empleo_imss_entidad = df_empleo_imss[~df_empleo_imss["sector_economico_4"].isna()][["cve_entidad", "sector_economico_4", "ta"]]
    df_empleo_imss_entidad = df_empleo_imss_entidad.groupby(["cve_entidad", "sector_economico_4"]).sum().reset_index()
    df_empleo_imss_entidad["cve_entidad"] = df_empleo_imss_entidad["cve_entidad"].apply(lambda x : f"{x:02}")
    
    ## Generamos el cw de imss a scian para cada zona metropolitana 
    acumula_entidad_scian = []
    print("Procesando crosswalk a nivel ENTIDAD IMSS-SCIAN")

    for i, entidad in enumerate([f"{i:02}"for i in range(1,33)]):
        print(f"{i}/{32}  {entidad}")
        acumula_entidad_scian.append(datos_imss_to_scian(entidad, zm_imss_muni, df_empleo_imss_entidad, clases_scian, cw_imss_scian, cw_imss_scian_agrega, "entidad"))

    entidades_scian = pd.concat(acumula_entidad_scian, ignore_index = True)
    entidades_scian["zm"] = entidades_scian["zm"].apply(lambda x: int(x))

    ### Generamos el crosswalk SCIAN --> CIIU-RECODIFICADO a nivel ENTIDAD
    entidades_ciiu = entidades_scian[["zm"]]
    
    for ciiu, scian_clases in cw_ciiu_scian.items():
        clases_coinciden_scian = list(set(entidades_scian.columns).intersection(scian_clases))
        clases_coinciden_scian.sort()

        entidades_ciiu[ciiu] = entidades_scian[clases_coinciden_scian].sum(axis = 1)

    entidades_ciiu["zm"] = entidades_ciiu["zm"].apply(lambda x: int(x))

    """
    CENSO ECONÓMICO RAW
    """

    if anio == 2019:
        # Obtenemos los datos del Censo Económico crudos para las Zonas Metropolitadas en SCIAN 2018
        print("Obtenemos los datos del Censo Económico crudos para las zonas metropolitadas en SCIAN 2018")
        zonas_metropolitanas_scian_censo = []
        for i, zm_scian_raw in enumerate(zonas_metropolitanas_claves):
            print(f"{i}/{len(zonas_metropolitanas_claves)}  {zm_scian_raw}")
            zonas_metropolitanas_scian_censo.append(
                pd.concat([get_raw_censo(zm_scian_raw, [str(i, "UTF-8")], censo_zm, arbol_scian) for i in tags_actividades_scian[1:]], ignore_index = True)
            )

        zonas_metropolitanas_scian_censo = pd.concat(zonas_metropolitanas_scian_censo, ignore_index = True)
        zonas_metropolitanas_scian_censo = zonas_metropolitanas_scian_censo.pivot(index=['CLAVE_ZONA'], columns=['CODIGO'], values="empleo_clase").reset_index()
        zonas_metropolitanas_scian_censo = zonas_metropolitanas_scian_censo.rename(columns = {"CLAVE_ZONA" : "zm"})
        zonas_metropolitanas_scian_censo["zm"] = zonas_metropolitanas_scian_censo["zm"].apply(lambda x : int(x.replace(".","")))

        # Obtenemos los datos del Censo Económico crudos para los Estados en SCIAN 2018
        print("Obtenemos los datos del Censo Económico crudos para los Estados en SCIAN 2018")

        entidades_scian_censo = []

        for i, entidad_scian_raw in enumerate([f"{i:02}"for i in range(1,33)]):
            print(f"{i}/{len(range(1,33))}  {entidad_scian_raw}")
            entidades_scian_censo.append(
                pd.concat([get_raw_censo(entidad_scian_raw, [str(i, "UTF-8")], censo_entidad, arbol_scian) for i in tags_actividades_scian[1:]], ignore_index = True)
            )

        entidades_scian_censo = pd.concat(entidades_scian_censo, ignore_index = True)
        entidades_scian_censo = entidades_scian_censo.pivot(index=['CLAVE_ZONA'], columns=['CODIGO'], values="empleo_clase").reset_index()
        entidades_scian_censo = entidades_scian_censo.rename(columns = {"CLAVE_ZONA" : "zm"})
        entidades_scian_censo["zm"] = entidades_scian_censo["zm"].apply(lambda x : int(x.replace(".","")))

        ## Generamos el cw de scian a ciiu para cada zona metropolitana
        zonas_metropolitanas_scian_censo_to_ciiu = zonas_metropolitanas_scian_censo[["zm"]]

        for ciiu, scian_clases in cw_ciiu_scian.items():
            clases_coinciden_scian = list(set(zonas_metropolitanas_scian_censo.columns).intersection(scian_clases))
            clases_coinciden_scian.sort()

            zonas_metropolitanas_scian_censo_to_ciiu[ciiu] = zonas_metropolitanas_scian_censo[clases_coinciden_scian].sum(axis = 1)


        ### Generamos el crosswalk SCIAN --> CIIU-RECODIFICADO a nivel ENTIDAD
        entidades_scian_censo_to_ciiu = entidades_scian_censo[["zm"]]

        for ciiu, scian_clases in cw_ciiu_scian.items():
            clases_coinciden_scian = list(set(entidades_scian_censo.columns).intersection(scian_clases))
            clases_coinciden_scian.sort()

            entidades_scian_censo_to_ciiu[ciiu] = entidades_scian_censo[clases_coinciden_scian].sum(axis = 1)

        entidades_scian_censo_to_ciiu["zm"] = entidades_scian_censo_to_ciiu["zm"].apply(lambda x: int(x))
    else:
        (zonas_metropolitanas_scian_censo,
        entidades_scian_censo, 
        zonas_metropolitanas_scian_censo_to_ciiu,
        entidades_scian_censo_to_ciiu) = [pd.DataFrame()]*4

    ### Regresamos los datos generados
    datos_retorno = (
        df_empleo_imss_entidad_matrix.to_numpy().astype(int),               # Matriz laboral en dimensión (entidad, clasificación IMSS)
        entidades_scian.to_numpy().astype(int),                             # Matriz laboral en dimensión (entidad, clasificación SCIAN)
        entidades_ciiu.to_numpy().astype(int),                              # Matriz laboral en dimensión (entidad, clasificación CIIU-RECOD)
        df_empleo_imss_zm_matrix.to_numpy().astype(int),                    # Matriz laboral en dimensión (zona metropolitana, clasificación IMSS)
        zonas_metropolitanas_scian.to_numpy().astype(int),                  # Matriz laboral en dimensión (zona metropolitana, clasificación SCIAN)
        zonas_metropolitanas_ciiu.to_numpy().astype(int),                   # Matriz laboral en dimensión (zona metropolitana, clasificación CIIU-RECOD)
        zonas_metropolitanas_scian_censo.to_numpy().astype(int),            # Matriz laboral en dimensión (zona metropolitana, clasificación SCIAN-DATOS RAW CENSO)
        entidades_scian_censo.to_numpy().astype(int),                       # Matriz laboral en dimensión (entidad, clasificación SCIAN-DATOS RAW CENSO)
        zonas_metropolitanas_scian_censo_to_ciiu.to_numpy().astype(int),    # Matriz laboral en dimensión (zona metropolitana, clasificación CIIU-RECOD DATOS RAW CENSO)
        entidades_scian_censo_to_ciiu.to_numpy().astype(int),               # Matriz laboral en dimensión (entidad, clasificación CIIU-RECOD DATOS RAW CENSO)
    )

    return datos_retorno


## Creamos HDF5

with h5py.File(os.path.join(OUTPUT_PATH, 'matrices_laborales_imss.h5'), 'w') as f_h5:

    ## Generamos los grupos principales 
    # /MEX
    #      /MEX/datos
    #      /MEX/tags
    grupo_mex = f_h5.create_group("MEX")
    grupo_datos = grupo_mex.create_group("datos")
    grupo_tags = grupo_mex.create_group("tags")

    ## Generamos los grupos a nivel de ubicacion-geografía en grupo datos
    #      /MEX/datos/entidad
    #      /MEX/datos/zm

    grupo_datos_entidad = grupo_datos.create_group("entidad")
    grupo_datos_zm = grupo_datos.create_group("zm")

    ## Generamos los grupos a nivel de clasificador en ubicacion-geografía 
    #      /MEX/datos/entidad
    #           /MEX/datos/entidad/imss
    #           /MEX/datos/entidad/scian
    #           /MEX/datos/entidad/ciiu
    #           /MEX/datos/entidad/scian_censo
    #           /MEX/datos/entidad/ciiu_censo
    grupo_datos_entidad_imss = grupo_datos_entidad.create_group("imss")
    grupo_datos_entidad_scian = grupo_datos_entidad.create_group("scian")
    grupo_datos_entidad_ciiu = grupo_datos_entidad.create_group("ciiu")
    grupo_datos_entidad_scian_censo = grupo_datos_entidad.create_group("scian_censo")
    grupo_datos_entidad_ciiu_censo = grupo_datos_entidad.create_group("ciiu_censo")

    #      /MEX/datos/zm
    #           /MEX/datos/zm/imss
    #           /MEX/datos/zm/scian
    #           /MEX/datos/zm/ciiu
    #           /MEX/datos/zm/scian_censo
    #           /MEX/datos/zm/ciiu_censo
    grupo_datos_zm_imss = grupo_datos_zm.create_group("imss")
    grupo_datos_zm_scian = grupo_datos_zm.create_group("scian")
    grupo_datos_zm_ciiu = grupo_datos_zm.create_group("ciiu")
    grupo_datos_zm_scian_censo = grupo_datos_zm.create_group("scian_censo")
    grupo_datos_zm_ciiu_censo = grupo_datos_zm.create_group("ciiu_censo")

    for anio, values in ligas_imss_empleo_anios.items():
        ## Creamos conjuntos de datos por cada par ubicación-clasificador
        # Entidad
        grupo_anio_entidad_imss = grupo_datos_entidad_imss.create_dataset(str(anio), (12, 32, len(tags_actividades_imss)))
        grupo_anio_entidad_scian = grupo_datos_entidad_scian.create_dataset(str(anio), (12, 32, len(tags_actividades_scian)))
        grupo_anio_entidad_ciiu = grupo_datos_entidad_ciiu.create_dataset(str(anio), (12, 32, len(tags_actividades_ciiu)))

        # Zona Metropolitana
        grupo_anio_zm_imss = grupo_datos_zm_imss.create_dataset(str(anio), (12, 70, len(tags_actividades_imss)))
        grupo_anio_zm_scian = grupo_datos_zm_scian.create_dataset(str(anio), (12, 70, len(tags_actividades_scian)))
        grupo_anio_zm_ciiu = grupo_datos_zm_ciiu.create_dataset(str(anio), (12, 70, len(tags_actividades_ciiu)))

        # Zona Metropolitana
        grupo_anio_zm_scian_censo = grupo_datos_zm_scian_censo.create_dataset(str(anio), (12, 70, len(tags_actividades_scian)))
        grupo_anio_zm_ciiu_censo = grupo_datos_zm_ciiu_censo.create_dataset(str(anio), (12, 70, len(tags_actividades_ciiu)))

        # Entidad
        grupo_anio_entidad_scian_censo = grupo_datos_entidad_scian_censo.create_dataset(str(anio), (12, 32, len(tags_actividades_scian)))
        grupo_anio_entidad_ciiu_censo = grupo_datos_entidad_ciiu_censo.create_dataset(str(anio), (12, 32, len(tags_actividades_ciiu)))

        for mes in values:
            file_name = f"asg-{anio}-{mes}.csv"
            file_path = os.path.join(DATA_PATH, file_name)

            anio = int(anio)
            mes = int(mes.split("-")[0])-1

            if mes == 11:
                print(f"Guarda datos {anio} - {mes}")

                (datos_entidad_imss, 
                datos_entidad_scian, 
                datos_entidad_ciiu,  
                datos_zm_imss, 
                datos_zm_scian, 
                datos_zm_ciiu,
                datos_zm_scian_censo,
                datos_entidad_scian_censo,
                datos_zm_scian_censo_to_ciiu,
                datos_entidad_scian_censo_to_ciiu)  = get_data_by_file(file_path)

                grupo_anio_entidad_imss[mes] = datos_entidad_imss.copy()
                grupo_anio_entidad_scian[mes] = datos_entidad_scian.copy()
                grupo_anio_entidad_ciiu[mes] = datos_entidad_ciiu.copy()
                grupo_anio_zm_imss[mes] = datos_zm_imss.copy()
                grupo_anio_zm_scian[mes] = datos_zm_scian.copy()
                grupo_anio_zm_ciiu[mes] = datos_zm_ciiu.copy()

                if anio == 2019:
                    grupo_anio_zm_scian_censo[mes] = datos_zm_scian_censo
                    grupo_anio_zm_ciiu_censo[mes] = datos_zm_scian_censo_to_ciiu
                    grupo_anio_entidad_scian_censo[mes] = datos_entidad_scian_censo
                    grupo_anio_entidad_ciiu_censo[mes] = datos_entidad_scian_censo_to_ciiu


    # Creamos tags por cada clasificador
    grupo_tags_imss = grupo_tags.create_group("imss")
    grupo_tags_scian = grupo_tags.create_group("scian")
    grupo_tags_ciiu = grupo_tags.create_group("ciiu")

    grupo_tags_imss.create_dataset("tag", (len(tags_actividades_imss),), 'S10', tags_actividades_imss)
    grupo_tags_scian.create_dataset("tag", (len(tags_actividades_scian),), 'S10', tags_actividades_scian)
    grupo_tags_ciiu.create_dataset("tag", (len(tags_actividades_ciiu),), 'S10', tags_actividades_ciiu)



## Definimos metadatos a partir del archivo yaml

empleo_imss = h5py.File(os.path.join(OUTPUT_PATH, 'matrices_laborales_imss.h5'), "r+")

with open(os.path.join(DOCS_PATH, "metadata.yml"), "r") as file:
    metadatos = yaml.load(file, Loader=yaml.Loader)

empleo_imss["MEX"].attrs['titulo'] = metadatos["variable"]["titulo"]
empleo_imss["MEX"].attrs['clasificacion_industrial'] = metadatos["variable"]["clasificacion"]
empleo_imss["MEX"].attrs['descripcion'] = metadatos["resources"][0]["descrip"]
empleo_imss["MEX"].attrs['url'] = metadatos["resources"][0]["url"]

#for anio in empleo_imss["MEX"]["datos"].keys():
#    anio_dataset = empleo_imss["MEX"]["datos"][anio]
#    anio_dataset.dims[0].label = metadatos["variable"]["label-0"]
#    anio_dataset.dims[1].label = metadatos["variable"]["label-1"]
#    anio_dataset.dims[2].label = metadatos["variable"]["label-2"]

empleo_imss.flush()
empleo_imss.close()
