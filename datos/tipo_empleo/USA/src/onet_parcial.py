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


# Cargamos lista de archivos de onet
file_data_path_onet = glob.glob(ONET_DATA_PATH+"/*.txt")

file_topic_name = [i.split("/")[-1].replace(".txt","").replace(" ", "_").lower() for i in file_data_path_onet]

topic_data_path = {i:j for i,j in zip(file_topic_name, file_data_path_onet)}

"""
Exploramos los datos correspondientes a :
    * skills --> skills
    * training --> education,_training,_and_experience
    * educación --> education,_training,_and_experience
    * titulo universitario --> education,_training,_and_experience
    * habilidades más elevadas ---> 
    * profesional no profesional --> education,_training,_and_experience
    * tipo de profesion
    * tecnología --> technology_skills
"""

skills = pd.read_table(topic_data_path["skills"])
training = pd.read_table(topic_data_path["education,_training,_and_experience"])
training_categories = pd.read_table(topic_data_path["education,_training,_and_experience_categories"])
tecnologia = pd.read_table(topic_data_path["technology_skills"])

### Nos quedamos sólo con los datos de Required Level of Education
training = training[(training["Element Name"]=="Required Level of Education") & (training["Domain Source"]=="Incumbent")]

### Obtenemos el porcentaje de empleo con grado y posgrado necesario para cada ocupación
educacion_shares = training.query("Category <= 6.0")[["O*NET-SOC Code", "Data Value"]].groupby("O*NET-SOC Code").sum().reset_index()
educacion_shares["Data Value"] /=100

### Generamos el promedio entre las ocupaciones onet
educacion_shares["O*NET-SOC Code"] = educacion_shares["O*NET-SOC Code"].apply(lambda x : x.split(".")[0])
educacion_shares = educacion_shares.groupby("O*NET-SOC Code").mean().reset_index()

### Renombramos la columna de ocupación
educacion_shares = educacion_shares.rename(columns = {"O*NET-SOC Code" : "occ_code"})

### Guadamos los resultados
educacion_shares.to_csv(os.path.join(OUTPUT_PATH, "onet_ocupaciones_razon_empleo_calificado.csv"), index = False)