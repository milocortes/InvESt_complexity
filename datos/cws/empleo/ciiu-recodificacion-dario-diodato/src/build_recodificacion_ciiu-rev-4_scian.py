## Cargamos paquetes 
import networkx as nx
from networkx.algorithms import community
import numpy as np
import pandas as pd
import json
import os 

## Definimos rutas donde se encuentran las correspondencias scian-ciiu
FILE_PATH = os.getcwd()
CWS_PATH = os.path.abspath(os.path.join(*[".."]*3, "empleo"))
CIIU_SCIAN_FILE_PATH = os.path.join(CWS_PATH, "scian-ciiu", "ciiu-4_scian-2018.json")
CIIU_NAICS_FILE_PATH = os.path.join(CWS_PATH, "naics", "output","isic_4_to_naics_2017.json")
OUTPUT_PATH = os.path.abspath(os.path.join("..", "output"))
DATOS_PATH = os.path.abspath(os.path.join("..", "datos"))

# Cargamos las correspondencias entre CIIU Rev 4-SCIAN 2018
ciiu_scian = json.load(open(CIIU_SCIAN_FILE_PATH, "r"))
df_ciiu_scian = pd.DataFrame(
    [(f"{int(ciiu):04}", scian) for ciiu, scian_clases in ciiu_scian.items() for scian in scian_clases]
    , columns = ["ciiu", "scian"]
)

# Cargamos las correspondencias entre CIIU Rev 4-NAICS 2017
ciiu_naics = json.load(open(CIIU_NAICS_FILE_PATH, "r"))
df_ciiu_naics = pd.DataFrame(
    [(f"{int(ciiu):04}", scian) for ciiu, scian_clases in ciiu_naics.items() for scian in scian_clases]
    , columns = ["ciiu", "naics"]
)

## Generate graph/network here
# empty graph/network
G_ciiu_scian = nx.Graph()
  

# add edges    
for k in df_ciiu_scian.index:
    i = tuple(df_ciiu_scian.iloc[[k]]["ciiu"].values)[0] 
    j = tuple(df_ciiu_scian.iloc[[k]]["scian"].values)[0] 
    G_ciiu_scian.add_edge(int(i),int(j)) 

#gen sets
set_i = df_ciiu_scian[['ciiu']]
set_i = set_i.drop_duplicates(keep='first')
set_i['set_type']=int(1)
set_j = df_ciiu_scian[['scian']]
set_j = set_j.drop_duplicates(keep='first')
set_j['set_type']=int(2)

set_i.ciiu = set_i.ciiu.astype(int)
set_i

set_j.scian = set_j.scian.astype(int)
set_j
# node attributes
node_type = set_i.set_index("ciiu").set_type.to_dict()
node_type.update(set_j.set_index("scian").set_type.to_dict() )
for k in node_type:
    node_type[k]=int(node_type[k])

# assign attributes to networkx G
nx.set_node_attributes(G_ciiu_scian,node_type,"n_type")

## The complex case in a many-to-many mapping
C2 = community.label_propagation_communities(G_ciiu_scian)
list_comp2=sorted(C2, key = len, reverse=True)
nc2 = len(list_comp2)

# final concordance tables generation
C123=pd.DataFrame(columns= ["code","code_3","s"])

i = 0
for c in range(nc2):
    code_3 =c+1 
    for n in list_comp2[c]:
        C123.loc[i] = 0
        C123.loc[i]["code"] = n
        C123.loc[i]["code_3"] = code_3        
        C123.loc[i]["s"] = np.floor(n / (10**(6) ) )  
        i += 1
## Add tags for each classification system
C123["s"] = 2
C123.loc[C123.code.apply(lambda x: len(str(x))==4 or len(str(x))==3), "s"] = 1

T13=C123.loc[C123["s"]== 1] 
T23=C123.loc[C123["s"]== 2] 

T13.columns=["ciiu","new_code","s"]
T23.columns=["scian","new_code","s"]

codificacion = C123.copy()
codificacion.columns = ["codigo", "codigo_nuevo", "clasificador"]
codificacion.loc[codificacion.clasificador==1,"clasificador"] = "ciiu"
codificacion.loc[codificacion.clasificador==2,"clasificador"] = "scian"

## Add names and group for each new classification id

nombres = pd.read_csv(os.path.join(DATOS_PATH, "ciiu-rev-4_nombres.csv"))

codificacion = codificacion.query("clasificador=='ciiu'").merge(right=nombres, how="inner", left_on="codigo", right_on="ciiu")
codificacion["ciiu"] = codificacion["ciiu"].apply(lambda x: f"{x:04}")

nueva_codificacion = []
for i in codificacion.codigo_nuevo.unique():
    actividades_integra = codificacion.query(f"codigo_nuevo=={i}")["descripcion_ciiu"].to_list()
    if len(actividades_integra)==1:
        nueva_codificacion.append(
            (i,"".join(actividades_integra),"".join(codificacion.query(f"codigo_nuevo=={i}")["ciiu"]),",".join(codificacion.query(f"codigo_nuevo=={i}")["ciiu"].to_list()) )
        )
    else:
        print((i,"/-/".join(actividades_integra),min(codificacion.query(f"codigo_nuevo=={i}")["ciiu"].to_list()),",".join(codificacion.query(f"codigo_nuevo=={i}")["ciiu"].to_list())))
        nueva_codificacion.append(
            (i,"/-/".join(actividades_integra),min(codificacion.query(f"codigo_nuevo=={i}")["ciiu"].to_list()),",".join(codificacion.query(f"codigo_nuevo=={i}")["ciiu"].to_list()) )
        )

nueva_codificacion = pd.DataFrame(nueva_codificacion, columns = ["codigo_nuevo", "descripcion_codigo_nuevo", "ciiu_asignado", "actividades_ciiu_integra"])

## Get repeated values
#import collections
#repeated_prefix = [item for item, count in collections.Counter(nueva_codificacion[nueva_codificacion.actividades_ciiu_integra.apply(lambda x : "," in x)].ciiu_asignado.apply(lambda x : x[:2])).items() if count > 1]
repeated_prefix = nueva_codificacion[nueva_codificacion.actividades_ciiu_integra.apply(lambda x : "," in x)].ciiu_asignado.apply(lambda x : x[:2]).unique()
nueva_codificacion["ciiu_nueva_cod"] = nueva_codificacion["ciiu_asignado"].copy()

for prefix in repeated_prefix:
    logical_test = nueva_codificacion.ciiu_asignado.apply(lambda x : x.startswith(prefix)) & nueva_codificacion.actividades_ciiu_integra.apply(lambda x : "," in x)
    num_repetidos = nueva_codificacion[logical_test].shape[0]
    nueva_codificacion.loc[logical_test, "ciiu_nueva_cod"] = [f"{prefix}-X{i:02}"for i in range(1,num_repetidos+1)]
    
nueva_codificacion = nueva_codificacion.sort_values(by="ciiu_nueva_cod").reset_index(drop=True)


## Get correspondence between the new classification and the ciiu-naics and ciiu-scian correspondences.
ciiu_recodificado_naics = {i:[] for i in nueva_codificacion["ciiu_nueva_cod"]}
ciiu_recodificado_scian = {i:[] for i in nueva_codificacion["ciiu_nueva_cod"]}


## Generate cw for ciiu-naics
for i in range(nueva_codificacion.shape[0]):
    nueva_ciiu = nueva_codificacion.loc[i, "ciiu_nueva_cod"]
    actividades_integradas = nueva_codificacion.loc[i, "actividades_ciiu_integra"].split(",")

    for actividades_integrada in actividades_integradas:
        ciiu_recodificado_naics[nueva_ciiu].extend(df_ciiu_naics[df_ciiu_naics.ciiu.isin(actividades_integradas)]["naics"].to_list())

for k,v in ciiu_recodificado_naics.items():
    ciiu_recodificado_naics[k] = list(set(v))


## Generate cw for ciiu-scian
ciiu_scian_merge = C123.query("s==2").merge(right=nueva_codificacion[["codigo_nuevo", "ciiu_nueva_cod"]], how = "left", left_on="code_3", right_on="codigo_nuevo")[["code", "ciiu_nueva_cod"]]

for scian, ciiu_nuevo in ciiu_scian_merge.to_records(index = False):
    ciiu_recodificado_scian[ciiu_nuevo].append(str(scian))

## Save dictionaries
nueva_codificacion.to_csv(os.path.join(OUTPUT_PATH, "recodificacion_ciiu-rev-4_scian_2018-nombres-correspondencia-ciiu.csv"), index = False)
json.dump(ciiu_recodificado_scian, open( os.path.join(OUTPUT_PATH, "ciiu_recodificado_scian_2018.json"), "w"))
json.dump(ciiu_recodificado_naics, open( os.path.join(OUTPUT_PATH, "ciiu_recodificado_naics_2017.json"), "w"))