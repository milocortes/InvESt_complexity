import h5py
import os 
import pandas as pd 
import json 

### Usamos el paquete ecomplexity para hacer pruebas de las métricas de complejidad
from ecomplexity import proximity, ecomplexity

# Definimos rutas
PATH_FILE = os.getcwd()
OUTPUT_PATH = os.path.abspath(os.path.join(PATH_FILE, "..", "output"))
CW_PATH = os.path.abspath(os.path.join(PATH_FILE, "..", "datos", "cws", "empleo"))
DICT_PATH = os.path.abspath(os.path.join(PATH_FILE, "..", "datos", "diccionarios"))

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

for anio in range(2013, 2023):
    geografia = "zm"
    clasificador = "ciiu"
    #anio = 2019
    pais = "MEX"
    mex = pd.DataFrame(empleo[pais]["datos"][geografia][clasificador][str(anio)][11,:,:], columns = clasificadores_dict[clasificador]).astype(int)
    columnas_no_ceros = list(mex.set_index("zm").sum()[mex.set_index("zm").sum() > 0].index)

    todas_actividades = mex.columns[1:]

    print(len(columnas_no_ceros))
    print(f"Razon empleo_actividades_mex/empleo_total{slv[columnas_no_ceros].sum().sum()/slv[todas_actividades].sum().sum()}")

    ## SLV
    slv = pd.DataFrame(empleo["SLV"]["datos"]["ciiu-recodificado"]["2013-2022"][:], columns = ciiu_recod).astype(int)
    slv = slv.query(f"zm == {anio}")
    slv["zm"] = "SLV"
    slv = slv.rename(columns = {slv.columns[0] : mex.columns[0]})

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



cdata_datos_empleo = ecomplexity(datos_slv_mex.query("anio==2019"), trade_cols)

cdata_datos_empleo = cdata_datos_empleo.sort_values(by="eci", ascending=False)
{i:j for i,j in cdata_datos_empleo[["zm_nombre", "eci"]].to_records(index = False)}


datos_slv_mex.to_csv("empleo_slv_mex_2013-2022.csv", index = False)
