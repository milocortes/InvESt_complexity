import pandas as pd 
import numpy as np
import glob
import os 

# Definimos rutas
PATH_FILE = os.getcwd()
DATA_PATH = os.path.abspath(os.path.join(PATH_FILE, "..", "output"))
OUTPUT_PATH = os.path.abspath(os.path.join(PATH_FILE, "..", "output"))
ONET_DATA_PATH = os.path.abspath(os.path.join(PATH_FILE, "..", "datos", "onet", "db_28_2_text"))

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

### Agregamos las categorías de O*NET-SOC Code
skills["O*NET-SOC Code"] = skills["O*NET-SOC Code"].apply(lambda x : str(x).split(".")[0])
abilities["O*NET-SOC Code"] = abilities["O*NET-SOC Code"].apply(lambda x : str(x).split(".")[0])
knowledge["O*NET-SOC Code"] = knowledge["O*NET-SOC Code"].apply(lambda x : str(x).split(".")[0])

skills = skills[skills.duplicated(subset=['O*NET-SOC Code'], keep='last')]
abilities = abilities[abilities.duplicated(subset=['O*NET-SOC Code'], keep='last')]
knowledge = knowledge[knowledge.duplicated(subset=['O*NET-SOC Code'], keep='last')]

### Agregamos información correspondiente al empleo por actividad ciiu y tipo de ocupación
occ_ciiu_completo = occ_ciiu.merge(right=skills, how="inner", left_on="occ_code", right_on="O*NET-SOC Code")
occ_ciiu_completo["coempleo_share"] = (occ_ciiu_completo["coempleo"]/occ_ciiu_completo["ciiu_empleo_total"]).replace(np.nan, 0.0)