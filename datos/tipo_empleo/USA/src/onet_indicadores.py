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
occ_ciiu = occ_ciiu.merge(right = occ_ciiu[["ciiu", "coempleo"]].groupby("ciiu").sum().reset_index().rename(columns = {"coempleo":"ciiu_empleo_total"}), how="left", on="ciiu")
occ_ciiu = occ_ciiu.rename(columns = {"coempleo" : "empleo"})

# Cargamos lista de archivos de onet
file_data_path_onet = glob.glob(ONET_DATA_PATH+"/*.txt")

file_topic_name = [i.split("/")[-1].replace(".txt","").replace(" ", "_").lower() for i in file_data_path_onet]

topic_data_path = {i:j for i,j in zip(file_topic_name, file_data_path_onet)}

# Cargamos los datos de skills, knowledge y abilities
skills = pd.read_table(topic_data_path["skills"])
knowledge = pd.read_table(topic_data_path["knowledge"])
abilities = pd.read_table(topic_data_path["abilities"])

# Nos quedamos los recursos de Incumbent y Analyst
skills = skills[skills["Domain Source"] == "Analyst"].reset_index(drop = True)
abilities = abilities[abilities["Domain Source"] == "Analyst"].reset_index(drop = True)
knowledge = knowledge[knowledge["Domain Source"] == "Incumbent"].reset_index(drop = True)

# Descargamos información de Scale ID
escalas = pd.read_table("https://www.onetcenter.org/dl_files/database/db_28_2_text/Scales%20Reference.txt")

# Agregamos información adicional
skills = skills.merge(right=escalas, how = "left", on = "Scale ID")
abilities = abilities.merge(right=escalas, how = "left", on = "Scale ID")
knowledge = knowledge.merge(right=escalas, how = "left", on = "Scale ID")

### Agregamos información del nombre de los identificadores 
onet_taxonomia = pd.read_html("https://www.onetcenter.org/taxonomy/2019/list.html")[0]
onet_taxonomia = onet_taxonomia.rename(columns = {"O*NET-SOC 2019 Code" : "O*NET-SOC Code"})

skills = skills.merge(right=onet_taxonomia, how="inner", on="O*NET-SOC Code")
abilities = abilities.merge(right=onet_taxonomia, how="inner", on="O*NET-SOC Code")
knowledge = knowledge.merge(right=onet_taxonomia, how="inner", on="O*NET-SOC Code")

### Agregamos las categorías de O*NET-SOC Code
skills["O*NET-SOC Code"] = skills["O*NET-SOC Code"].apply(lambda x : str(x).split(".")[0])
abilities["O*NET-SOC Code"] = abilities["O*NET-SOC Code"].apply(lambda x : str(x).split(".")[0])
knowledge["O*NET-SOC Code"] = knowledge["O*NET-SOC Code"].apply(lambda x : str(x).split(".")[0])

skills = skills[skills.duplicated(subset=['O*NET-SOC Code'], keep='last')]
abilities = abilities[abilities.duplicated(subset=['O*NET-SOC Code'], keep='last')]
knowledge = knowledge[knowledge.duplicated(subset=['O*NET-SOC Code'], keep='last')]


### Agregamos información correspondiente al empleo por actividad ciiu y tipo de ocupación
skills_completo = occ_ciiu.merge(right=skills[["O*NET-SOC Code", "Element ID", "Scale ID", "Data Value"]], how="inner", left_on="occ_code", right_on="O*NET-SOC Code")
skills_completo = skills_completo.drop(columns=["O*NET-SOC Code"])
skills_completo.to_csv(os.path.join(OUTPUT_EDUCACION_PATH, "onet_ciiu_skills.csv"), index=False)

del skills_completo

abilities_completo = occ_ciiu.merge(right=abilities[["O*NET-SOC Code", "Element ID", "Scale ID", "Data Value"]], how="inner", left_on="occ_code", right_on="O*NET-SOC Code")
abilities_completo = abilities_completo.drop(columns=["O*NET-SOC Code"])
abilities_completo.to_csv(os.path.join(OUTPUT_EDUCACION_PATH, "onet_ciiu_abilities.csv"), index=False)

del abilities_completo

knowledge_completo = occ_ciiu.merge(right=knowledge[["O*NET-SOC Code", "Element ID", "Scale ID", "Data Value"]], how="inner", left_on="occ_code", right_on="O*NET-SOC Code")
knowledge_completo = knowledge_completo.drop(columns=["O*NET-SOC Code"])
knowledge_completo.to_csv(os.path.join(OUTPUT_EDUCACION_PATH, "onet_ciiu_knowledge.csv"), index=False)

del knowledge_completo

### Guardamos catálogos de escalas, de elementos y la taxonomía
elementos = pd.read_table("https://www.onetcenter.org/dl_files/database/db_28_2_text/Content%20Model%20Reference.txt")
elementos.to_csv(os.path.join(OUTPUT_EDUCACION_PATH, "catalogo_onet_element_model.csv"), index=False)

escalas.to_csv(os.path.join(OUTPUT_EDUCACION_PATH, "catalogo_onet_scale_model.csv"), index=False)
onet_taxonomia.to_csv(os.path.join(OUTPUT_EDUCACION_PATH, "catalogo_onet_taxonomia.csv"), index=False)

#### Cargamos diccionario de actividades ciiu-scian-naics
ciiu_scian = pd.read_html("https://milocortes.github.io/InvESt_complexity/contenido/datos_empleo.html")[0]

def rompe_chunks(cadena : str, chunk : int):

    index_init = 0
    index_fin = chunk

    size = len(cadena)//chunk
    
    acumula = []

    for i in range(size):
        acumula.append(
            cadena[index_init:index_fin]
        )

        index_init = index_fin
        index_fin += chunk

    return ",".join(acumula)

ciiu_scian["Actividades CIIU agrupadas"] = ciiu_scian["Actividades CIIU agrupadas"].apply(lambda x : rompe_chunks(str(x),4))
ciiu_scian["NAICS 2017"] = ciiu_scian["NAICS 2017"].apply(lambda x : rompe_chunks(str(x),6))
ciiu_scian["SCIAN 2018"] = ciiu_scian["SCIAN 2018"].apply(lambda x : rompe_chunks(str(x),6))

ciiu_scian.to_csv(os.path.join(OUTPUT_EDUCACION_PATH, "catalogo_ciiu_scian_naics.csv"), index=False)
