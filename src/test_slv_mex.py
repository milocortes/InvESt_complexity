import h5py
import os 
import pandas as pd 
import json 

### Usamos el paquete ecomplexity para hacer pruebas de las métricas de complejidad
from ecomplexity import ecomplexity
from ecomplexity import proximity as proximity_ecomplexity

# Definimos rutas
PATH_FILE = os.getcwd()
OUTPUT_PATH = os.path.abspath(os.path.join(PATH_FILE, "..", "output"))
CW_PATH = os.path.abspath(os.path.join(PATH_FILE, "..", "datos", "cws", "empleo"))
DICT_PATH = os.path.abspath(os.path.join(PATH_FILE, "..", "datos", "diccionarios"))
MIP_PATH = os.path.abspath(os.path.join(PATH_FILE, "..", "datos", "mip", "MEX", "output"))
OCC_EMPLEO_PATH = os.path.abspath(os.path.join(PATH_FILE, "..", "datos", "tipo_empleo", "USA", "output"))

# Carga datos de empleo
empleo = h5py.File(os.path.join(OUTPUT_PATH, 'complexity_empleo.hdf5'), "r")

# Obtenemos listas de clasificadores
ciiu_recod = [str(i, encoding = "UTF-8") for i in empleo["MEX"]["tags"]["ciiu"]["tag"][:]]
scian_tags = [str(i, encoding = "UTF-8") for i in empleo["MEX"]["tags"]["scian"]["tag"][:]]
imss_tags = [str(i, encoding = "UTF-8") for i in empleo["MEX"]["tags"]["imss"]["tag"][:]]
naics_tags = [str(i, encoding = "UTF-8") for i in empleo["USA"]["tags"]["scian-6-digitos"]["tag"][:]]

# Los guardamos en un diccionario 
clasificadores_dict = {
    "imss" : imss_tags[:],
    "scian" : scian_tags[:],
    "ciiu" : ciiu_recod[:],
    "naics" : naics_tags[:]
}


## TEST PARA MEXICO
## CLASIFICACIÓN IMSS
# Cargamos diccionario de nombres de zonas metropolitanas 
zm_mex_nombres = pd.read_csv(os.path.join(DICT_PATH, "zonas_metropolitanas", "MEX", "output", "zonas_metropolitanas_MEX.csv"))
zm_mex_nombres["CVE_ENT"] = zm_mex_nombres["CVEGEO"].apply(lambda x: int(f"{x:05}"[:2]))

zm_mex_nombres_zm_cw = {i:j for i,j in zm_mex_nombres[["CVE_ZONA", "NOM_ZM"]].to_records(index = False)}
zm_mex_nombres_zm_cw = {i:j.replace("≤", "ó").replace("ß", "á") for i,j in zm_mex_nombres_zm_cw.items()}
zm_mex_nombres_entidad_cw = {i:j for i,j in zm_mex_nombres[["CVE_ENT", "NOM_ENT"]].to_records(index = False)}

# Cargamos diccionario de nombres de actividades 
actividades_imss = pd.read_csv(os.path.join(DICT_PATH, "id_nombre_actividades_imss", "output", "imss_id_nombres_actividades.csv"))
actividades_imss = {i:j for i,j in actividades_imss.to_records(index=False)}

# Cargamos nombres de actividades del CIIU recodificado
ciiu_recod_nombres = pd.read_csv(os.path.join(CW_PATH, "ciiu-recodificacion-dario-diodato", "output", "recodificacion_ciiu-rev-4.csv"))
ciiu_recod_nombres_cw = {i:j for i,j in ciiu_recod_nombres[["ciiu_nueva_cod", "descripcion_codigo_nuevo"]].to_records(index = False)}

# Cargamos diccionario de nombres de zonas metropolitanas USA
msa_usa = pd.read_csv(os.path.join(DICT_PATH, "zonas_metropolitanas", "USA", "msa_usa.csv"))
msa_usa = msa_usa[msa_usa["Metropolitan/Micropolitan Statistical Area"]=="Metropolitan Statistical Area"].reset_index(drop=True)

zm_usa_nombres_msa_cw = {int(i):j for i,j in msa_usa[["CBSA Code", "CBSA Title"]].to_records(index = False)}


## CLASIFICACIÓN CIIU razon transables
transables = {i:j for i,j in pd.read_csv("razon_transables_total_ciiu_usa_2014.csv")[["ciiu", "razon_transable_total"]].to_records(index = False)}


## Obtenemos datos
## MEXICO

datos_slv_mex = []

for anio in range(2012, 2023):
    geografia = "zm"
    clasificador = "ciiu"
    #anio = 2019
    pais = "MEX"
    mex = pd.DataFrame(empleo[pais]["datos"][geografia][clasificador][str(anio)][11,:,:], columns = clasificadores_dict[clasificador]).astype(int)
    columnas_no_ceros = list(mex.set_index("zm").sum()[mex.set_index("zm").sum() > 0].index)

    todas_actividades = mex.columns[1:]

    ## SLV
    slv = pd.DataFrame(empleo["SLV"]["datos"]["ciiu-recodificado"]["2013-2022"][:], columns = ciiu_recod).astype(int)
    slv = slv.query(f"zm == {anio}")
    slv["zm"] = "SLV"
    slv = slv.rename(columns = {slv.columns[0] : mex.columns[0]})

    print(len(columnas_no_ceros))
    print(f"Razon empleo_actividades_mex/empleo_total{slv[columnas_no_ceros].sum().sum()/slv[todas_actividades].sum().sum()}")

    ## USA
    #usa = pd.DataFrame(empleo["USA"]["datos"][clasificador][str(anio)][:], columns = clasificadores_dict[clasificador]).astype(int)
    #usa = usa[usa["zm"].isin(msa_usa["CBSA Code"].to_list())].reset_index(drop=True)


    datos_empleo = pd.concat([mex, slv], ignore_index = True)
    datos_empleo = datos_empleo[["zm"]+columnas_no_ceros]


    datos_empleo = pd.melt(datos_empleo, id_vars=["zm"])

    datos_empleo = pd.concat([
        pd.DataFrame({"anio" : [anio]*datos_empleo.shape[0]}),
        datos_empleo
    ], axis = 1)

    datos_empleo["zm_nombre"] = datos_empleo["zm"].replace(zm_mex_nombres_zm_cw)
    datos_empleo["ciiu_nombre"] = datos_empleo["variable"].replace(ciiu_recod_nombres_cw)
    datos_empleo["razon_transable_total"] = datos_empleo["variable"].replace(transables)
    datos_empleo = datos_empleo.query("razon_transable_total==1")
    trade_cols = {'time':'anio', 'loc':"zm", 'prod':'variable', 'val':'value'}

    cdata_datos_empleo = ecomplexity(datos_empleo, trade_cols)

    cdata_datos_empleo = cdata_datos_empleo.sort_values(by="eci", ascending=False)
    {i:j for i,j in cdata_datos_empleo[["zm_nombre", "eci"]].to_records(index = False)}
    datos_slv_mex.append(datos_empleo)

datos_slv_mex = pd.concat(datos_slv_mex, ignore_index=False)


cdata_datos_empleo = ecomplexity(datos_slv_mex.query("anio==2020"), trade_cols)
cdata_datos_empleo = cdata_datos_empleo.sort_values(by="eci", ascending=False)
ranking_ci = {i:j for i,j in cdata_datos_empleo[["zm_nombre", "eci"]].to_records(index = False)}
ranking_ci

## Obtenemos el ranking para el periodo 2013-2022
acumula_ranking = []

for anio in range(2013, 2022):
    cdata_datos_empleo = ecomplexity(datos_slv_mex.query(f"anio=={anio}"), trade_cols)
    cdata_datos_empleo = cdata_datos_empleo.sort_values(by="eci", ascending=False)
    ranking_ci = {i:j for i,j in cdata_datos_empleo[["zm_nombre", "eci"]].to_records(index = False)}

    acumula_ranking += [[anio,i+1,j] for i,j in enumerate(tuple(ranking_ci)[:10])]

df_ranking = pd.DataFrame(acumula_ranking, columns = ["anio", "ranking", "unidad"])
df_ranking["unidad"] = df_ranking["unidad"].apply(lambda x : x.replace("MΘxico", "México").replace("QuerΘtaro","Querétaro").replace("Zona metropolitana de la ","").replace("Zona metropolitana de ","").replace("Metrópoli municipal de ",""))
df_ranking.to_csv("zm_complexity_ranking.csv", index=False)

datos_slv_mex.to_csv("empleo_slv_mex_2013-2022.csv", index = False)

### Verificamos si los cálculos de ec-complexity coinciden con nuestra implementación
### Métricas de complejidad
from complexity_measures import *

###############################

industrias_solo_mex = list(cdata_datos_empleo.variable.unique())
industrias_solo_mex.sort()

occ_trade_cols = {'time':'anio', 'loc':"occ_code", 'prod':'ciiu', 'val':'coempleo'}

occ_empleo = pd.read_csv(os.path.join(OCC_EMPLEO_PATH, "usa_ciiu_occ_empleo.csv"))
occ_empleo["occ_code"] = occ_empleo["occ_code"].apply(lambda x : str(x))
occ_empleo["ciiu"] = occ_empleo["ciiu"].apply(lambda x : str(x))
occ_empleo = occ_empleo[occ_empleo.ciiu.isin(industrias_solo_mex)]

value_col_name = "coempleo"
activiy_col_name = "ciiu"
place_col_name = "occ_code"

sum_cp_X_cp = occ_empleo[[value_col_name]].sum().values[0]
sum_c_X_cp = occ_empleo[[activiy_col_name, value_col_name]].groupby(activiy_col_name).sum()


values_RCA = {"df" : occ_empleo, 
            "value_col_name" : value_col_name, 
            "activiy_col_name" : activiy_col_name, 
            "place_col_name" : place_col_name,
            "sum_cp_X_cp" : sum_cp_X_cp, 
            "sum_c_X_cp" : sum_c_X_cp}


occ_empleo_complexity = pd.concat([RCA(**values_RCA, place=p) for p in occ_empleo.occ_code.unique()], ignore_index = True)
occ_RCA = occ_empleo_complexity.query("coempleo>=1.0").reset_index(drop=True)
all_activities = occ_empleo_complexity.ciiu.unique()
pair_RCA = occ_RCA[["place","ciiu"]].to_numpy()
Mcp = build_Mcp(pair_RCA, all_activities)
Mcp = Mcp.replace(np.nan, 0)
df_proximity = proximity(Mcp, ["actA", "actB", "proximity"])
occ_proximity_mat = df_proximity.pivot(index = ["actA"], columns = ["actB"], values = "proximity")

## Calculamos la versión continua de proximidad
RCA_mat = occ_empleo_complexity.pivot(index = ["place"], columns = ["ciiu"])
RCA_mat.columns = [i[1] for i in RCA_mat.columns]
RCA_mat = RCA_mat.replace(np.nan, 0.0)

occ_proximity_mat_continua = pd.DataFrame((1 + np.corrcoef(RCA_mat.T)) / 2, columns = occ_proximity_mat.columns)
occ_proximity_mat_continua.index = occ_proximity_mat.columns
occ_proximity_mat_continua = occ_proximity_mat_continua.replace(np.nan, 0.0)

#### IO similarity
## Cargamos IO
mip_ciiu = pd.read_csv(os.path.join(MIP_PATH, "mip_ciiu.csv"))
mip_ciiu.set_index("actividad", inplace = True)

## Obtenemos la matriz de coeficientes técnicos (matriz A)
# X es el vector de producto total
X = mip_ciiu.sum(axis = 1).to_numpy()

# Z es la matriz de demanda intermedia 
Z = mip_ciiu.to_numpy()

# Calculamos la matriz de coeficientes técnicos
A = Z/X[:,None]

# Lac convertimos en un dataframe
df_A = pd.DataFrame(A, columns=list(mip_ciiu.index))
df_A.index = list(mip_ciiu.index)
df_A = df_A.replace(np.nan, 0.0)

# Nos quedamos con el subset de industrias
df_A = df_A.loc[datos_slv_mex.variable.unique() ,datos_slv_mex.variable.unique()]

## Input presence similarity (column wise correlation)
df_A_input_presence_similarity = df_A.corr().replace(np.nan, 0.0)
# Normalizamos entre 0 y 1 
df_A_input_presence_similarity = (df_A_input_presence_similarity - np.min(df_A_input_presence_similarity.to_numpy()))/2

## Output presence similarity (row wise correlation)
df_A_output_presence_similarity = df_A.T.corr().replace(np.nan, 0.0)
# Normalizamos entre 0 y 1
df_A_output_presence_similarity = (df_A_output_presence_similarity - np.min(df_A_output_presence_similarity.to_numpy()))/2

###############################
acumula_complexity = []

for anio in range(2012, 2023):
    print(anio)
    complexity_data = datos_slv_mex.query(f"anio=={anio}")[["zm", "variable", "value"]]
    complexity_data["zm"] = complexity_data["zm"].apply(lambda x : str(x))

    value_col_name = "value"
    activiy_col_name = "variable"
    place_col_name = "zm"

    sum_cp_X_cp = complexity_data[[value_col_name]].sum().values[0]
    sum_c_X_cp = complexity_data[[activiy_col_name, value_col_name]].groupby(activiy_col_name).sum()

    values_RCA = {"df" : complexity_data, 
                "value_col_name" : value_col_name, 
                "activiy_col_name" : activiy_col_name, 
                "place_col_name" : place_col_name,
                "sum_cp_X_cp" : sum_cp_X_cp, 
                "sum_c_X_cp" : sum_c_X_cp}


    zm_RCA_completo = pd.concat([RCA(**values_RCA, place=p) for p in complexity_data.zm.unique()], ignore_index = True)
    zm_RCA_completo["llave"] = zm_RCA_completo.place + "/" + zm_RCA_completo.variable  

    ### Diversity
    zm_RCA = zm_RCA_completo.query("value>=1.0").reset_index(drop=True)
    all_activities = complexity_data.variable.unique()
    pair_RCA = zm_RCA[["place","variable"]].to_numpy()

    df_diversity = pd.DataFrame({k:[v] for k,v in metrics_diversity_ubiquity(pair_RCA, all_activities, "diversity").items()}).transpose().reset_index()
    df_diversity.columns = ["place", "diversity"]

    ### Ubiquity
    df_ubiquity = pd.DataFrame({k:[v] for k,v in metrics_diversity_ubiquity(pair_RCA, all_activities, "ubiquity").items()}).transpose().reset_index()
    df_ubiquity.columns = ["variable", "ubiquity"]

    df_ubiquity_diversity = df_diversity.merge(right = df_ubiquity, how="cross")
    df_ubiquity_diversity["llave"] = df_ubiquity_diversity.place + "/" + df_ubiquity_diversity.variable

    zm_RCA_completo = zm_RCA_completo.rename(columns={"value" : "rca"})
    zm_RCA_completo = zm_RCA_completo.merge(right=df_ubiquity_diversity[["llave", "diversity", "ubiquity"]], on ="llave")


    ### Mcp
    Mcp = build_Mcp(pair_RCA, all_activities)

    ### Proximity
    df_proximity = proximity(Mcp, ["actA", "actB", "proximity"])
    proximity_matrix = df_proximity.pivot_table(index = ["actA"], columns = ["actB"])
    proximity_matrix.reset_index(drop = True, inplace = True)
    proximity_matrix.columns = [i[1] for i in proximity_matrix.columns]  
    proximity_matrix.index = proximity_matrix.columns
    proximity_matrix

    ### Distance
    almacena = []
    for place in complexity_data.zm.unique():
        for activity in complexity_data.variable.unique():
            almacena.append((place,
                            activity,
                            distance(place, activity, Mcp, proximity_matrix)
                            ))


    df_distance = pd.DataFrame(almacena, columns = ["place", "activity", "distance"])
    df_distance

    ### Density
    almacena = []
    for place in complexity_data.zm.unique():
        for activity in complexity_data.variable.unique():
            almacena.append((place,
                            activity,
                            density(place, activity, Mcp, proximity_matrix)
                            ))


    df_density = pd.DataFrame(almacena, columns = ["place", "activity", "density"])
    df_density


    ### Input presence
    almacena = []
    for place in complexity_data.zm.unique():
        for activity in complexity_data.variable.unique():
            almacena.append((place,
                            activity,
                            IO_similarity(place, activity, Mcp, df_A, "input_similarity")
                            ))


    df_input_similarity = pd.DataFrame(almacena, columns = ["place", "activity", "input_similarity"])
    df_input_similarity

    ### Output presence
    almacena = []
    for place in complexity_data.zm.unique():
        for activity in complexity_data.variable.unique():
            almacena.append((place,
                            activity,
                            IO_similarity(place, activity, Mcp, df_A, "output_similarity")
                            ))


    df_output_similarity = pd.DataFrame(almacena, columns = ["place", "activity", "output_similarity"])
    df_output_similarity

    # Input presence similarity (column wise correlation)
    almacena = []
    for place in complexity_data.zm.unique():
        for activity in complexity_data.variable.unique():
            almacena.append((place,
                            activity,
                            density(place, activity, Mcp, df_A_input_presence_similarity)
                            ))


    df_input_presence_similarity = pd.DataFrame(almacena, columns = ["place", "activity", "input_presence_similarity"])
    df_input_presence_similarity

    # Output presence similarity (row wise correlation)
    almacena = []
    for place in complexity_data.zm.unique():
        for activity in complexity_data.variable.unique():
            almacena.append((place,
                            activity,
                            density(place, activity, Mcp, df_A_output_presence_similarity)
                            ))


    df_output_presence_similarity = pd.DataFrame(almacena, columns = ["place", "activity", "output_presence_similarity"])
    df_output_presence_similarity

    ### Cooempleo similarity (density con Mcp y matriz de proximidad de coempleo)
    ## Version discreta
    almacena = []
    for place in complexity_data.zm.unique():
        for activity in complexity_data.variable.unique():
            almacena.append((place,
                            activity,
                            density(place, activity, Mcp, occ_proximity_mat)
                            ))


    df_coempleo_similarity = pd.DataFrame(almacena, columns = ["place", "activity", "coempleo_similarity"])
    
    ## Version continua
    almacena = []
    for place in complexity_data.zm.unique():
        for activity in complexity_data.variable.unique():
            almacena.append((place,
                            activity,
                            density(place, activity, Mcp, occ_proximity_mat_continua)
                            ))


    df_coempleo_similarity_continua = pd.DataFrame(almacena, columns = ["place", "activity", "coempleo_similarity_continua"])

    ### Reunimos datos de Mcp y distancia
    df_Mcp = Mcp.reset_index().melt(id_vars="index", value_vars=Mcp.columns)
    df_Mcp["llave"] = df_Mcp["index"].apply(lambda x : str(x)) + "/" + df_Mcp.variable
    zm_RCA_completo = zm_RCA_completo.merge(right=df_Mcp.rename(columns={"value":"mcp"})[["llave","mcp"]], on = "llave")

    df_distance["llave"] = df_distance["place"].apply(lambda x : str(x)) + "/" + df_distance.activity
    df_density["llave"] = df_density["place"].apply(lambda x : str(x)) + "/" + df_density.activity
    df_input_similarity["llave"] = df_input_similarity["place"].apply(lambda x : str(x)) + "/" + df_input_similarity.activity
    df_output_similarity["llave"] = df_output_similarity["place"].apply(lambda x : str(x)) + "/" + df_output_similarity.activity

    df_input_presence_similarity["llave"] = df_input_presence_similarity["place"].apply(lambda x : str(x)) + "/" + df_input_similarity.activity
    df_output_presence_similarity["llave"] = df_output_presence_similarity["place"].apply(lambda x : str(x)) + "/" + df_output_presence_similarity.activity


    df_coempleo_similarity["llave"] = df_coempleo_similarity["place"].apply(lambda x : str(x)) + "/" + df_coempleo_similarity.activity
    df_coempleo_similarity_continua["llave"] = df_coempleo_similarity["place"].apply(lambda x : str(x)) + "/" + df_coempleo_similarity.activity

    zm_RCA_completo = zm_RCA_completo.merge(right=df_distance[["llave","distance"]], on = "llave")
    zm_RCA_completo = zm_RCA_completo.merge(right=df_density[["llave","density"]], on = "llave")
    zm_RCA_completo = zm_RCA_completo.merge(right=df_input_similarity[["llave","input_similarity"]], on = "llave")
    zm_RCA_completo = zm_RCA_completo.merge(right=df_output_similarity[["llave","output_similarity"]], on = "llave")
    zm_RCA_completo = zm_RCA_completo.merge(right=df_coempleo_similarity[["llave","coempleo_similarity"]], on = "llave")
    zm_RCA_completo = zm_RCA_completo.merge(right=df_coempleo_similarity_continua[["llave","coempleo_similarity_continua"]], on = "llave")
    zm_RCA_completo = zm_RCA_completo.merge(right=df_input_presence_similarity[["llave","input_presence_similarity"]], on = "llave")
    zm_RCA_completo = zm_RCA_completo.merge(right=df_output_presence_similarity[["llave","output_presence_similarity"]], on = "llave")

    zm_RCA_completo = zm_RCA_completo[["place", "variable", "rca","diversity", "ubiquity", "mcp", "density", "distance", "output_similarity", "input_similarity", "coempleo_similarity", "coempleo_similarity_continua", "input_presence_similarity", "output_presence_similarity"]]

    ## Agregamos etiquetas de nombres de actividades y zm
    zm_RCA_completo["zm_nombre"] = zm_RCA_completo["place"].replace({str(i):j for i,j in zm_mex_nombres_zm_cw.items()})
    zm_RCA_completo["ciiu_nombre"] = zm_RCA_completo["variable"].replace(ciiu_recod_nombres_cw)

    zm_RCA_completo["anio"] = anio
    zm_RCA_completo = zm_RCA_completo[["anio"] + list(zm_RCA_completo.columns[:-1])]
    acumula_complexity.append(zm_RCA_completo)


data_complexity = pd.concat(acumula_complexity, ignore_index = True)

#### Hacemos un test de nuestros resultados vis a vis el paquete ecomplexity
cdata_datos_empleo = ecomplexity(datos_slv_mex, trade_cols)
cdata_datos_empleo["zm"] = cdata_datos_empleo["zm"].apply(lambda x : str(x))
cdata_datos_empleo_todo = cdata_datos_empleo.copy()
cdata_datos_empleo = cdata_datos_empleo.sort_values(by=["anio", "variable", "zm"])[["anio", "zm", "variable", "rca", "diversity", "ubiquity", "density", "mcp"]].reset_index(drop=True)

data_complexity = data_complexity.sort_values(by=["anio", "variable", "place"]).reset_index(drop=True)

### TESTS
## RCA
(cdata_datos_empleo.rca - data_complexity.rca).sum()
## Diversity
(cdata_datos_empleo.diversity - data_complexity.diversity).sum()
## Ubiquity
(cdata_datos_empleo.ubiquity - data_complexity.ubiquity).sum()
## Mcp
(cdata_datos_empleo.mcp - data_complexity.mcp).sum()

### Agregamos distancia a nuestros datos del paquete ecomplexity
cdata_datos_empleo_todo["distance"] = data_complexity["distance"]
cdata_datos_empleo_todo["input_similarity"] = data_complexity["input_similarity"]
cdata_datos_empleo_todo["output_similarity"] = data_complexity["output_similarity"]
cdata_datos_empleo_todo["coempleo_similarity_discreta"] = data_complexity["coempleo_similarity"]
cdata_datos_empleo_todo["coempleo_similarity_continua"] = data_complexity["coempleo_similarity_continua"]
cdata_datos_empleo_todo["input_presence_similarity"] = data_complexity["input_presence_similarity"]
cdata_datos_empleo_todo["output_presence_similarity"] = data_complexity["output_presence_similarity"]

cdata_datos_empleo_todo.to_csv("complexity_todo_metricas.csv", index=False)

#### Matriz de proximidad
proximidad = proximity_ecomplexity(datos_slv_mex, trade_cols)
proximidad = proximidad.query("anio==2021")[["variable_1", "variable_2", "proximity"]]
proximidad.proximity = proximidad.proximity.replace(np.nan, 1.0)


import networkx as nx 
import matplotlib.pyplot as plt
from py2cytoscape import util as cy 
from py2cytoscape import cytoscapejs as cyjs
import requests
import json

# empty graph/network
G = nx.Graph()

# add nodes
for i in proximidad.variable_1.unique():
    G.add_node(i)
  
# add edges    
for in_node, out_node, w in proximidad.to_records(index = False):
    if w!=0.0:
        G.add_edge(in_node, out_node, key=0, weight=w)

# attributes
node_rca = {}
node_ciiu_seccion = {}

# node attributes 
from ciiu_agregacion import ciiu_agregacion

for node_name, rca_value in cdata_datos_empleo_todo.query("anio==2021 and zm=='SLV'")[["variable", "rca"]].to_records(index = False):
    node_rca[node_name]=rca_value
    node_ciiu_seccion[node_name] = ciiu_agregacion[node_name[:2]][1]

# assign attributes to networkx G
nx.set_node_attributes(G,node_rca,"n_rca")
nx.set_node_attributes(G,node_ciiu_seccion,"n_seccion")
    
# move network from networkx to cy
G.node = G.nodes
cytoscape_network = cy.from_networkx(G)

# Basic Setup
PORT_NUMBER = 1234
IP = 'localhost'
BASE = 'http://' + IP + ':' + str(PORT_NUMBER) + '/v1/'
HEADERS = {'Content-Type': 'application/json'}
requests.delete(BASE + 'session')

res1 = requests.post(BASE + 'networks', data=json.dumps(cytoscape_network), headers=HEADERS)
res1_dict = res1.json()
new_suid = res1_dict['networkSUID']
requests.get(BASE + 'apply/layouts/force-directed/' + str(new_suid))

style_name = 'Basic_Style'

my_style = {
  "title" : style_name,
   'defaults': [{
       'visualProperty': 'EDGE_TRANSPARENCY', 
       'value': 255
  }, {
    "visualProperty" : "NODE_SIZE",
    'value': 20
  }, {
    "visualProperty" : "EDGE_WIDTH",
    'value': 1
  },{
       'visualProperty': 'NODE_LABEL_FONT_SIZE', 
       'value': 12
   },{
       'visualProperty': 'NODE_LABEL_TRANSPARENCY', 
       'value': 250
   }, {
       'visualProperty': 'NODE_TRANSPARENCY', 
       'value': 250
   }]
}

# Create new Visual Style
res = requests.post(BASE + "styles", data=json.dumps(my_style), headers=HEADERS)
new_style_name = res.json()['title']

# Apply it to current netwrok
requests.get(BASE + 'apply/styles/' + new_style_name + '/' + str(new_suid))

######## NOS OLVIDAMOS TANTITO Y HACEMOS REGRESIONES
import numpy as np


#cdata_datos_empleo = ecomplexity(datos_slv_mex, trade_cols)
#df_complexity_short = cdata_datos_empleo[["zm", "variable", "anio", "density", "rca"]]\
#                                    .pivot(index = ["zm", "variable"], columns=["anio"], values = ["density", "rca"])\
#                                    .reset_index()

data_complexity = data_complexity.rename(columns={"place":"zm"})

df_complexity_short = data_complexity[["zm", "variable", "anio", "density", "rca", "output_similarity", "input_similarity", "coempleo_similarity", "coempleo_similarity_continua", "input_presence_similarity", "output_presence_similarity"]]\
                                    .pivot(index = ["zm", "variable"], columns=["anio"], values = ["density", "rca", "output_similarity", "input_similarity", "coempleo_similarity", "coempleo_similarity_continua", "input_presence_similarity", "output_presence_similarity"])\
                                    .reset_index()

df_complexity_short.columns = ["edo", "actividad"] + [f"{i}_{j}" for i,j in df_complexity_short.columns[2:]]

anio_inicio = "2015"
anio_final = "2020"

### growth_rca
df_complexity_short["growth_rca_log"] = np.log(df_complexity_short[f"rca_{anio_final}"]/df_complexity_short[f"rca_{anio_inicio}"])
df_complexity_short["growth_rca_arcsinh"] = np.arcsinh(df_complexity_short[f"rca_{anio_final}"]/df_complexity_short[f"rca_{anio_inicio}"])

### diff_rca
df_complexity_short["diff_rca_log"] = np.log(df_complexity_short[f"rca_{anio_final}"] - df_complexity_short[f"rca_{anio_inicio}"]) 
df_complexity_short["diff_rca_arcsinh"] = np.arcsinh(df_complexity_short[f"rca_{anio_final}"] - df_complexity_short[f"rca_{anio_inicio}"])

### Apariciones
df_complexity_short["apariciones"] = 0
df_complexity_short.loc[(df_complexity_short[f"rca_{anio_final}"]>0.2) & (df_complexity_short[f"rca_{anio_inicio}"]<0.05) , "apariciones"] = 1

### Desapariciones
df_complexity_short["desapariciones"] = 0
df_complexity_short.loc[(df_complexity_short[f"rca_{anio_final}"]<0.05) & (df_complexity_short[f"rca_{anio_inicio}"]>0.2) , "desapariciones"] = 1

### Density
df_complexity_short["log_density"] = np.log(df_complexity_short[f"density_{anio_inicio}"])
df_complexity_short["arcsinh_density"] = np.arcsinh(df_complexity_short[f"density_{anio_inicio}"])

### RCA
df_complexity_short["log_rca"] = np.log(df_complexity_short[f"rca_{anio_inicio}"])
df_complexity_short["arcsinh_rca"] = np.arcsinh(df_complexity_short[f"rca_{anio_inicio}"])

### Output presence
df_complexity_short["log_output_presence"] = np.log(df_complexity_short[f"output_similarity_{anio_inicio}"])
df_complexity_short["arcsinh_output_presence"] = np.arcsinh(df_complexity_short[f"output_similarity_{anio_inicio}"])

### Input presence
df_complexity_short["log_input_presence"] = np.log(df_complexity_short[f"input_similarity_{anio_inicio}"])
df_complexity_short["arcsinh_input_presence"] = np.arcsinh(df_complexity_short[f"input_similarity_{anio_inicio}"])

### Cooempleo presence (discreta)
df_complexity_short["log_coempleo_presence"] = np.log(df_complexity_short[f"coempleo_similarity_{anio_inicio}"])
df_complexity_short["arcsinh_coempleo_presence"] = np.arcsinh(df_complexity_short[f"coempleo_similarity_{anio_inicio}"])

### Cooempleo presence (continua)
df_complexity_short["log_coempleo_presence_continua"] = np.log(df_complexity_short[f"coempleo_similarity_continua_{anio_inicio}"])
df_complexity_short["arcsinh_coempleo_presence_continua"] = np.arcsinh(df_complexity_short[f"coempleo_similarity_continua_{anio_inicio}"])

### Output presence similarity
df_complexity_short["log_output_presence_similarity"] = np.log(df_complexity_short[f"output_presence_similarity_{anio_inicio}"])
df_complexity_short["arcsinh_output_presence_similarity"] = np.arcsinh(df_complexity_short[f"output_presence_similarity_{anio_inicio}"])

### Input presence similarity
df_complexity_short["log_input_presence_similarity"] = np.log(df_complexity_short[f"input_presence_similarity_{anio_inicio}"])
df_complexity_short["arcsinh_input_presence_similarity"] = np.arcsinh(df_complexity_short[f"input_presence_similarity_{anio_inicio}"])


df_complexity_short.to_csv("regresiones_crecimiento.csv", index = False)


#### Condiciona por los sectores que en el año inicial estaban presentes y las que en el final estaban ausentes