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

### Ponderamos el data value por la categoria de Required Level of Education
training["data_value_ponderado"] = [j*(1/((j/100)+0.0000001))**(i/5) for i,j in training[["Category", "Data Value"]].to_records(index = False)]

### Agregamos las categorías de O*NET-SOC Code
training["O*NET-SOC Code"] = training["O*NET-SOC Code"].apply(lambda x : str(x).split(".")[0])
training = training[training.duplicated(subset=['O*NET-SOC Code'], keep='last')]

### Mezclamos los dataframes
occ_ciiu_completo = occ_ciiu.merge(right=training[["O*NET-SOC Code", "Category", "Data Value", "data_value_ponderado"]], how="inner", left_on="occ_code", right_on="O*NET-SOC Code")
occ_ciiu_completo["coempleo_share"] = (occ_ciiu_completo["coempleo"]/occ_ciiu_completo["ciiu_empleo_total"]).replace(np.nan, 0.0)
occ_ciiu_completo["ciiu_share_empleo_total"] = occ_ciiu_completo["ciiu_empleo_total"]/occ_ciiu_completo["ciiu_empleo_total"].sum()

occ_ciiu_completo["data_value_ponderado_empleo_total"] = occ_ciiu_completo["ciiu_share_empleo_total"]*occ_ciiu_completo["coempleo_share"]*occ_ciiu_completo["data_value_ponderado"]


### Agrupamos por ciiu

df_ciiu_onet_metrica = occ_ciiu_completo[["ciiu","data_value_ponderado_empleo_total"]].groupby("ciiu").sum().reset_index().rename(columns = {"data_value_ponderado_empleo_total":"onet_metrica"})


ciiu = pd.read_html("https://milocortes.github.io/InvESt_complexity/contenido/datos_empleo.html")[0]
df_ciiu_onet_metrica["ciiu_nombre"] =df_ciiu_onet_metrica["ciiu"].replace({i:j for i,j in ciiu[["CIIU (recodificación)", "CIIU nombre"]].to_records(index = False)})

### Reescalamos la medida
def reescala(medida : pd.Series, t_max : float, t_min : float) -> pd.Series:
    r_min = medida.min()
    r_max = medida.max()

    return medida.apply(lambda m : (m - r_min)/(r_max-r_min) * (t_max - t_min) + t_min)

df_ciiu_onet_metrica["r_onet_metrica"] = reescala(df_ciiu_onet_metrica["onet_metrica"], 10.0, 0.0)

df_ciiu_onet_metrica[["ciiu", "ciiu_nombre", "onet_metrica", "r_onet_metrica"]].sort_values(by="r_onet_metrica", ascending=False).to_csv(os.path.join(OUTPUT_PATH, "df_ciiu_onet_metrica.csv"), index = False)


