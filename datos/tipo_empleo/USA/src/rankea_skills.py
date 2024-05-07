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

#skills = skills[skills.duplicated(subset=['O*NET-SOC Code'], keep='last')]
#abilities = abilities[abilities.duplicated(subset=['O*NET-SOC Code'], keep='last')]
#knowledge = knowledge[knowledge.duplicated(subset=['O*NET-SOC Code'], keep='last')]
skills = skills[["O*NET-SOC Code", "Element ID", "Scale ID", "Data Value"]].groupby(["O*NET-SOC Code", "Element ID", "Scale ID"]).mean().reset_index()
abilities = abilities[["O*NET-SOC Code", "Element ID", "Scale ID", "Data Value"]].groupby(["O*NET-SOC Code", "Element ID", "Scale ID"]).mean().reset_index()
knowledge = knowledge[["O*NET-SOC Code", "Element ID", "Scale ID", "Data Value"]].groupby(["O*NET-SOC Code", "Element ID", "Scale ID"]).mean().reset_index()

### Agregamos información correspondiente al empleo por actividad ciiu y tipo de ocupación
skills_completo = occ_ciiu.merge(right=skills[["O*NET-SOC Code", "Element ID", "Scale ID", "Data Value"]], how="inner", left_on="occ_code", right_on="O*NET-SOC Code")
skills_completo = skills_completo.drop(columns=["O*NET-SOC Code"])

skills_completo = skills_completo.query("empleo>0")

skills_importance = skills_completo[skills_completo["Scale ID"]=='IM']
skills_nivel = skills_completo[skills_completo["Scale ID"]=='LV']


skills_importance["pondera_skill"] = (skills_importance["empleo"]/skills_importance["ciiu_empleo_total"])*skills_importance["Data Value"]
skills_nivel["pondera_skill"] = (skills_nivel["empleo"]/skills_nivel["ciiu_empleo_total"])*skills_nivel["Data Value"]

skills_importance = skills_importance.rename(columns={"Element ID" : "Element_ID"})
skills_nivel = skills_nivel.rename(columns={"Element ID" : "Element_ID"})

#### SKILLS NIVEL
guarda = []
for element in skills_nivel.Element_ID.unique():
    element_skill_nivel = skills_nivel.query(f"Element_ID=='{element}'")
    ciiu_skill = element_skill_nivel[["ciiu", "pondera_skill"]].groupby("ciiu").agg(media=pd.NamedAgg(column="pondera_skill", aggfunc="mean"), suma=pd.NamedAgg(column="pondera_skill", aggfunc="sum")).reset_index()
    ciiu_skill["element_id"] = element

    guarda.append(ciiu_skill)

skills_ciiu = pd.concat(guarda, ignore_index=True)
skills_ciiu["ciiu_3d"] = skills_ciiu["ciiu"].apply(lambda x : str(x)[:3])
skills_ciiu["ciiu_2d"] = skills_ciiu["ciiu"].apply(lambda x : str(x)[:2])


skills_ciiu_3d = skills_ciiu[["ciiu_3d", "element_id","suma"]].groupby(["ciiu_3d", "element_id"]).mean().reset_index()
skills_ciiu_2d = skills_ciiu[["ciiu_2d", "element_id","suma"]].groupby(["ciiu_2d", "element_id"]).mean().reset_index()

elementos = pd.read_table("https://www.onetcenter.org/dl_files/database/db_28_2_text/Content%20Model%20Reference.txt")

skills_ciiu_3d["element_name"] = skills_ciiu_3d["element_id"].replace({i:j for i,j in elementos[["Element ID", "Element Name"]].to_records(index=False)} )
skills_ciiu_2d["element_name"] = skills_ciiu_2d["element_id"].replace({i:j for i,j in elementos[["Element ID", "Element Name"]].to_records(index=False)} )

## Isic rev 4
isic = pd.read_csv("/home/milo/Documents/egtp/iniciativas/InvESt_complexity/datos/tipo_empleo/USA/datos/ISICRev4_NT_input.csv")

skills_ciiu_2d["ciiu_2d_label"] = skills_ciiu_2d["ciiu_2d"].replace({i:j for i,j in isic[["Code", "ISIC Rev. 4 label"]].to_records(index = False)})
skills_ciiu_3d["ciiu_3d_label"] = skills_ciiu_3d["ciiu_3d"].apply(lambda x : x.replace("-","")).replace({i:j for i,j in isic[["Code", "ISIC Rev. 4 label"]].to_records(index = False)})

## Agrega ranking
agrega_2d = []

for ciiu in skills_ciiu_2d.ciiu_2d.unique():
    parcial = skills_ciiu_2d.query(f"ciiu_2d=='{ciiu}'").sort_values(by="suma", ascending= False)
    parcial["ranking"] = range(1,parcial.shape[0]+1 )
    agrega_2d.append(parcial)

skills_ciiu_2d = pd.concat(agrega_2d, ignore_index=True)

agrega_3d = []

for ciiu in skills_ciiu_3d.ciiu_3d.unique():
    parcial = skills_ciiu_3d.query(f"ciiu_3d=='{ciiu}'").sort_values(by="suma", ascending= False)
    parcial["ranking"] = range(1,parcial.shape[0]+1 )
    agrega_3d.append(parcial)

skills_ciiu_3d = pd.concat(agrega_3d, ignore_index=True)

skills_ciiu_3d_nivel = skills_ciiu_3d.copy()
skills_ciiu_2d_nivel = skills_ciiu_2d.copy()

#### SKILLS IMPORTANCIA

guarda = []
for element in skills_importance.Element_ID.unique():
    element_skill_nivel = skills_importance.query(f"Element_ID=='{element}'")
    ciiu_skill = element_skill_nivel[["ciiu", "pondera_skill"]].groupby("ciiu").agg(media=pd.NamedAgg(column="pondera_skill", aggfunc="mean"), suma=pd.NamedAgg(column="pondera_skill", aggfunc="sum")).reset_index()
    ciiu_skill["element_id"] = element

    guarda.append(ciiu_skill)

skills_ciiu = pd.concat(guarda, ignore_index=True)
skills_ciiu["ciiu_3d"] = skills_ciiu["ciiu"].apply(lambda x : str(x)[:3])
skills_ciiu["ciiu_2d"] = skills_ciiu["ciiu"].apply(lambda x : str(x)[:2])


skills_ciiu_3d = skills_ciiu[["ciiu_3d", "element_id","suma"]].groupby(["ciiu_3d", "element_id"]).mean().reset_index()
skills_ciiu_2d = skills_ciiu[["ciiu_2d", "element_id","suma"]].groupby(["ciiu_2d", "element_id"]).mean().reset_index()

elementos = pd.read_table("https://www.onetcenter.org/dl_files/database/db_28_2_text/Content%20Model%20Reference.txt")

skills_ciiu_3d["element_name"] = skills_ciiu_3d["element_id"].replace({i:j for i,j in elementos[["Element ID", "Element Name"]].to_records(index=False)} )
skills_ciiu_2d["element_name"] = skills_ciiu_2d["element_id"].replace({i:j for i,j in elementos[["Element ID", "Element Name"]].to_records(index=False)} )

## Isic rev 4
isic = pd.read_csv("/home/milo/Documents/egtp/iniciativas/InvESt_complexity/datos/tipo_empleo/USA/datos/ISICRev4_NT_input.csv")

skills_ciiu_2d["ciiu_2d_label"] = skills_ciiu_2d["ciiu_2d"].replace({i:j for i,j in isic[["Code", "ISIC Rev. 4 label"]].to_records(index = False)})
skills_ciiu_3d["ciiu_3d_label"] = skills_ciiu_3d["ciiu_3d"].apply(lambda x : x.replace("-","")).replace({i:j for i,j in isic[["Code", "ISIC Rev. 4 label"]].to_records(index = False)})

## Agrega ranking
agrega_2d = []

for ciiu in skills_ciiu_2d.ciiu_2d.unique():
    parcial = skills_ciiu_2d.query(f"ciiu_2d=='{ciiu}'").sort_values(by="suma", ascending= False)
    parcial["ranking"] = range(1,parcial.shape[0]+1 )
    agrega_2d.append(parcial)

skills_ciiu_2d = pd.concat(agrega_2d, ignore_index=True)

agrega_3d = []

for ciiu in skills_ciiu_3d.ciiu_3d.unique():
    parcial = skills_ciiu_3d.query(f"ciiu_3d=='{ciiu}'").sort_values(by="suma", ascending= False)
    parcial["ranking"] = range(1,parcial.shape[0]+1 )
    agrega_3d.append(parcial)

skills_ciiu_3d = pd.concat(agrega_3d, ignore_index=True)

skills_ciiu_3d_importancia = skills_ciiu_3d.copy()
skills_ciiu_2d_importancia = skills_ciiu_2d.copy()


###############################
skills_importance_ranking = skills_importance[["ciiu", "Element_ID", "pondera_skill"]].groupby(["ciiu", "Element_ID"]).sum().reset_index()
skills_nivel_ranking = skills_nivel[["ciiu", "Element_ID", "pondera_skill"]].groupby(["ciiu", "Element_ID"]).sum().reset_index()

agrega_skills_importance_ranking = []
agrega_skills_nivel_ranking = []

for ciiu in skills_importance_ranking.ciiu.unique():
    parcial = skills_importance_ranking.query(f"ciiu=='{ciiu}'").sort_values(by="pondera_skill", ascending= False)
    parcial["ranking"] = range(1,parcial.shape[0]+1 )
    agrega_skills_importance_ranking.append(parcial)

skills_importance_ranking = pd.concat(agrega_skills_importance_ranking, ignore_index=True)

for ciiu in skills_nivel_ranking.ciiu.unique():
    parcial = skills_nivel_ranking.query(f"ciiu=='{ciiu}'").sort_values(by="pondera_skill", ascending= False)
    parcial["ranking"] = range(1,parcial.shape[0]+1 )
    agrega_skills_nivel_ranking.append(parcial)

skills_nivel_ranking = pd.concat(agrega_skills_nivel_ranking, ignore_index=True)

skills_nivel_ranking["element_name"] = skills_nivel_ranking["Element_ID"].replace({i:j for i,j in elementos[["Element ID", "Element Name"]].to_records(index=False)} )
skills_importance_ranking["element_name"] = skills_importance_ranking["Element_ID"].replace({i:j for i,j in elementos[["Element ID", "Element Name"]].to_records(index=False)} )

#### GUARDAMOS DATOS
skills_ciiu_3d_importancia["tipo_skill"] = "importancia"
skills_ciiu_2d_importancia["tipo_skill"] = "importancia"

skills_ciiu_3d_nivel["tipo_skill"] = "nivel"
skills_ciiu_2d_nivel["tipo_skill"] = "nivel"

skills_ciiu_3d_nivel = skills_ciiu_3d_nivel.rename(columns = {"ciiu_3d" : "ciiu", "ciiu_3d_label" : "ciiu_label", "element_id":"skill_id", "element_name" : "skill_name", "suma" : "skill_metrica"})
skills_ciiu_2d_nivel = skills_ciiu_2d_nivel.rename(columns = {"ciiu_2d" : "ciiu", "ciiu_2d_label" : "ciiu_label", "element_id":"skill_id", "element_name" : "skill_name", "suma" : "skill_metrica"})

skills_ciiu_3d_importancia = skills_ciiu_3d_importancia.rename(columns = {"ciiu_3d" : "ciiu", "ciiu_3d_label" : "ciiu_label", "element_id":"skill_id", "element_name" : "skill_name", "suma" : "skill_metrica"})
skills_ciiu_2d_importancia = skills_ciiu_2d_importancia.rename(columns = {"ciiu_2d" : "ciiu", "ciiu_2d_label" : "ciiu_label", "element_id":"skill_id", "element_name" : "skill_name", "suma" : "skill_metrica"})


skills_ciiu_2d_3d = pd.concat([skills_ciiu_2d_nivel, skills_ciiu_3d_nivel, skills_ciiu_2d_importancia, skills_ciiu_3d_importancia], ignore_index=True)

skills_ciiu_2d_3d.to_csv("skills_ciiu_2d_3d.csv", index = False)


###############
skills_nivel_ranking = skills_nivel_ranking.rename(columns = {"Element_ID":"skill_id", "pondera_skill" : "skill_metrica", "element_name":"skill_name"})
skills_importance_ranking = skills_importance_ranking.rename(columns = {"Element_ID":"skill_id", "pondera_skill" : "skill_metrica", "element_name":"skill_name"})

skills_nivel_ranking["tipo_skill"] = "nivel"
skills_importance_ranking["tipo_skill"] = "importancia"

skills_ciiu_4d = pd.concat([skills_nivel_ranking, skills_importance_ranking], ignore_index=True)
skills_ciiu_4d.to_csv("skills_ciiu_4d.csv", index = False)

#elementos = pd.read_table("https://www.onetcenter.org/dl_files/database/db_28_2_text/Content%20Model%20Reference.txt")
#skills_nivel["Element Name"] = skills_nivel["Element ID"].replace({i:j for i,j in elementos[["Element ID", "Element Name"]].to_records(index=False)} )
#skills_importance["Element Name"] = skills_importance["Element ID"].replace({i:j for i,j in elementos[["Element ID", "Element Name"]].to_records(index=False)} )