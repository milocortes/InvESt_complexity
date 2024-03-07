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
occ_ciiu = pd.read_csv(os.path.join(DATA_PATH, "usa_ciiu_occ_empleo.csv"))

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

