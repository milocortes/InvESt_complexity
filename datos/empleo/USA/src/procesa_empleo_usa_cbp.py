import pandas as pd 
import numpy as np 
import glob 
import os
import json 

import h5py

import yaml

# Definimos el periodo de cobertura
anio_inicio = 2012
anio_fin = 2021

#anio_inicio = 2019
#anio_fin = 2020

# Definimos rutas
PATH_FILE = os.getcwd()
DATA_PATH = os.path.abspath(os.path.join(PATH_FILE, "..", "datos","cbp"))
OUTPUT_PATH = os.path.abspath(os.path.join(PATH_FILE, "..", "output"))
DOCS_PATH = os.path.abspath(os.path.join(PATH_FILE, "..", "docs"))
CW_PATH = os.path.abspath(os.path.join(PATH_FILE, *[".."]*3, "cws", "empleo"))

# Lista de archivos txt de CBP
cbp_files = glob.glob(DATA_PATH+"/*.txt") 
cbp_files.sort()

guarda_anios_datos = {}

for file in cbp_files:
    anio = 2000 + int(file.split("/")[-1][3:5])
    print(anio)
    cbp_data = pd.read_csv(file)
    cbp_data.columns = [i.lower() for i in cbp_data.columns]
    guarda_anios_datos[anio] = cbp_data[["msa", "naics", "emp"]]

## Creamos HDF5

def scian_digitos(cadena : str, digitos : int) -> int:
    return sum(i.isnumeric() for i in cadena)==digitos

## Cargamos cw
# El siguiente crosswalk no tiene la recodificación de la metología de diodato
#isic_4_to_naics_2017 = json.load(open(os.path.join(CW_PATH,"isic_4_to_naics_2017.json"), "r"))
isic_4_to_naics_2017 = json.load(open(os.path.join(CW_PATH,"ciiu-recodificacion-dario-diodato", "output", "ciiu_recodificado_naics_2017.json"), "r"))
naics_2017_to_naics_2012 = json.load(open(os.path.join(CW_PATH, "naics", "output", "naics_2017_to_naics_2012.json"), "r"))

naics_clases_2017 = []
for i in isic_4_to_naics_2017.values():
    naics_clases_2017.extend(i)
naics_clases_2017 = list(set(naics_clases_2017))
naics_clases_2017.sort()

todo_naics_2017 = pd.DataFrame(columns=["msa"] + naics_clases_2017)

## Poblamos el hdf5

with h5py.File(os.path.join(OUTPUT_PATH, 'matrices_laborales_cbp.h5'), 'w') as f_h5:

    grupo_usa = f_h5.create_group("USA")
    grupo_datos = grupo_usa.create_group("datos")
    grupo_tags = grupo_usa.create_group("tags")

    ## Creamos el subgrupo ciiu en el grupo datos
    grupo_ciiu_datos = grupo_datos.create_group("ciiu")

    for digito_scian in range(2, 7):
        print(f"scian-{digito_scian}-digitos")
        
        grupo_scian_datos = grupo_datos.create_group(f"scian-{digito_scian}-digitos")
        
        for anio in range(anio_inicio, anio_fin+1):
            
            df_cbp_anio = guarda_anios_datos[anio]
            
            df_cbp_anio = df_cbp_anio[df_cbp_anio["naics"].apply(lambda x : scian_digitos(x, digito_scian))].reset_index(drop=True)
            df_cbp_anio["naics"] = df_cbp_anio["naics"].apply(lambda x : x[:digito_scian])
            df_cbp_anio = df_cbp_anio.pivot(index = "msa", columns = "naics", values = "emp").reset_index().replace(np.nan, 0.0)

            if digito_scian==6:
                # Hacemos crosswalk entre las clases de naics 2012 y naics 2017
                for k,v in naics_2017_to_naics_2012.items():
                    actividades_coincide = list(set(v).intersection(df_cbp_anio.columns))
                    df_cbp_anio[k] = df_cbp_anio[actividades_coincide].sum(1)
                    df_cbp_anio = df_cbp_anio.drop(columns = actividades_coincide)
                
                df_cbp_anio[list(set(naics_clases_2017)-set(df_cbp_anio.columns[1:]))] = 0
                columnas_sectores = list(df_cbp_anio.columns[1:])
                columnas_sectores.sort()
                df_cbp_anio.columns = ["msa"] + columnas_sectores

                ## Generamos el dataframe con la clasificación ciiu recodificada
                df_cbp_ciiu_anio = df_cbp_anio[["msa"]]

                for ciiu_cod, naics_clases in isic_4_to_naics_2017.items():
                    df_cbp_ciiu_anio[ciiu_cod] = df_cbp_anio[naics_clases].sum(axis = 1)

                
            grupo_scian_datos.create_dataset(str(anio), (df_cbp_anio.shape[0], df_cbp_anio.shape[1]), data = df_cbp_anio.to_numpy(), dtype = np.int32)

            if digito_scian==6:
                grupo_ciiu_datos.create_dataset(str(anio), (df_cbp_ciiu_anio.shape[0], df_cbp_ciiu_anio.shape[1]), data = df_cbp_ciiu_anio.to_numpy(), dtype = np.int32)

        grupo_scian_tags = grupo_tags.create_group(f"scian-{digito_scian}-digitos")

        tags_actividades_naics = [str(n).encode("ascii", "ignore") for n in df_cbp_anio.columns]
        grupo_scian_tags.create_dataset("tag", (len(tags_actividades_naics),), 'S10', tags_actividades_naics)

        if digito_scian==6:
            grupo_ciiu_tags = grupo_tags.create_group(f"ciiu")

            tags_actividades_ciiu = [str(n).encode("ascii", "ignore") for n in df_cbp_ciiu_anio.columns]
            grupo_ciiu_tags.create_dataset("tag", (len(tags_actividades_ciiu),), 'S10', tags_actividades_ciiu)


## Definimos metadatos a partir del archivo yaml

empleo_cbp = h5py.File(os.path.join(OUTPUT_PATH, 'matrices_laborales_cbp.h5'), "r+")

with open(os.path.join(DOCS_PATH, "metadata.yml"), "r") as file:
    metadatos = yaml.load(file, Loader=yaml.Loader)

empleo_cbp["USA"].attrs['titulo'] = metadatos["variable"]["titulo"]
empleo_cbp["USA"].attrs['clasificacion_industrial'] = metadatos["variable"]["clasificacion"]
empleo_cbp["USA"].attrs['descripcion'] = metadatos["resources"][0]["descrip"]
empleo_cbp["USA"].attrs['url'] = metadatos["resources"][0]["url"]

#for scian_dig in empleo_cbp["USA"]["datos"].keys():
#    for anio in empleo_cbp["USA"]["datos"][scian_dig].keys():
#        empleo_cbp["USA"]["datos"][scian_dig][anio].dims[0].label = metadatos["variable"]["label-0"]
#        empleo_cbp["USA"]["datos"][scian_dig][anio].dims[1].label = metadatos["variable"]["label-1"]

empleo_cbp.flush()
empleo_cbp.close()