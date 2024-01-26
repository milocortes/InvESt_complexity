import h5py
import os 
import pandas as pd 
import json 

from complexity_measures import *

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

#  Cargamos las clases transables por cluster
transables_clusters = json.load(open(os.path.join(DICT_PATH, "traded_clusters_appendix", "output", "clases_transables_by_cluster_naics_2017.json"), "r"))

transables_all = []

for k,v in transables_clusters.items():
    transables_all += v

transables_all = [str(i) for i in transables_all]

# Cuántas transables hay en naics_tags y scian_tags?
print(f"Total transables {len(transables_all)}. Coincidencia NAICS 2017 y total transables {len(set(naics_tags).intersection(transables_all))}")
print(f"Total transables {len(transables_all)}. Coincidencia SCIAN 2018 y total transables {len(set(scian_tags).intersection(transables_all))}")


for transables_id, transables_clases in transables_clusters.items():
    #transables_id = "Video Production & Distribution"
    #transables_clases = transables_clusters[transables_id]
    print(transables_id)
    transables_clusters_id = {transables_id : transables_clases}
    acumula_mex = []
    acumula_usa = []
    for k,v in transables_clusters_id.items():
        print(f"Cluster {k}")
        v = [str(i) for i in v]
        print(f"Total transables {len(v)}. Coincidencia NAICS 2017 y total transables {len(set(naics_tags).intersection(v))}")
        print(f"Total transables {len(v)}. Coincidencia SCIAN 2018 y total transables {len(set(scian_tags).intersection(v))}")
        print("")
        
        acumula_usa += list(set(naics_tags).intersection(v))
        acumula_mex += list(set(scian_tags).intersection(v))

    acumula_usa.sort()
    acumula_mex.sort()

    if acumula_mex:
        anio = 2019

        ## Obtenemos los datos por zm y entidad para MEX
        mex_zm = pd.DataFrame(empleo["MEX"]["datos"]["zm"]["scian_censo"][str(anio)][11,:,:], columns = scian_tags).astype(int).melt(id_vars=['zm'])
        mex_entidad = pd.DataFrame(empleo["MEX"]["datos"]["entidad"]["scian_censo"][str(anio)][11,:,:], columns = scian_tags).astype(int).melt(id_vars=['zm'])

        ## Filtramos para quedarnos sólo con las actividades scian transables
        mex_zm = mex_zm[mex_zm.variable.isin(acumula_mex)].reset_index(drop=True)
        mex_entidad = mex_entidad[mex_entidad.variable.isin(acumula_mex)].reset_index(drop=True)

        ## Concatenamos nombres
        # Cargamos diccionario de nombres de zonas metropolitanas 
        zm_mex_nombres = pd.read_csv(os.path.join(DICT_PATH, "zonas_metropolitanas", "MEX", "output", "zonas_metropolitanas_MEX.csv"))
        zm_mex_nombres["CVE_ENT"] = zm_mex_nombres["CVEGEO"].apply(lambda x: int(f"{x:05}"[:2]))

        zm_mex_nombres_zm_cw = {i:j for i,j in zm_mex_nombres[["CVE_ZONA", "NOM_ZM"]].to_records(index = False)}
        zm_mex_nombres_zm_cw = {i:j.replace("≤", "ó").replace("ß", "á") for i,j in zm_mex_nombres_zm_cw.items()}
        zm_mex_nombres_entidad_cw = {i:j for i,j in zm_mex_nombres[["CVE_ENT", "NOM_ENT"]].to_records(index = False)}

        ## Asignamos nombres
        mex_entidad["zm_nombre"] = mex_entidad["zm"].replace(zm_mex_nombres_entidad_cw)
        mex_zm["zm_nombre"] = mex_zm["zm"].replace(zm_mex_nombres_zm_cw)

        ## Asignamos anio
        mex_zm = pd.concat([pd.DataFrame({"anio" : [anio]*mex_zm.shape[0]}), mex_zm], axis = 1)
        mex_entidad = pd.concat([pd.DataFrame({"anio" : [anio]*mex_entidad.shape[0]}), mex_entidad], axis = 1)

        ## Hacemos ejercicio de complejidad

        ### TODAS LAS ACTIVIDADES
        ### Usamos el paquete ecomplexity para hacer pruebas de las métricas de complejidad
        from ecomplexity import proximity, ecomplexity

        trade_cols = {'time':'anio', 'loc':"zm", 'prod':'variable', 'val':'value'}

        cdata_datos_empleo = ecomplexity(mex_zm, trade_cols)

        cdata_datos_empleo = cdata_datos_empleo.sort_values(by="eci", ascending=False)
        {i:round(j,3) for i,j in cdata_datos_empleo[~cdata_datos_empleo.duplicated(subset=["eci", "zm_nombre"], keep="first")].iloc[:32][["zm_nombre", "eci"]].to_records(index = False)}


        actividades_usa_no_mx = list(set(acumula_usa) - set(acumula_mex))
        actividades_usa_no_mx.sort()

        mex_zm_faltan = pd.DataFrame([(anio, zm_id, acti_faltante, 0, zm_nombre) 
                                        for zm_id, zm_nombre in zm_mex_nombres_zm_cw.items() 
                                        for acti_faltante in actividades_usa_no_mx],
                                    columns = ['anio', 'zm', 'variable', 'value', 'zm_nombre']
                                    )

        mex_zm = pd.concat([mex_zm, mex_zm_faltan], ignore_index = True)

        ### Cargamos los datos de USA para hacer la comparación
        usa = pd.DataFrame(empleo["USA"]["datos"]["scian-6-digitos"][str(anio)][:], columns = naics_tags).astype(int)
        msa_usa = pd.read_csv(os.path.join(DICT_PATH, "zonas_metropolitanas", "USA", "msa_usa.csv"))
        msa_usa = msa_usa[~msa_usa.duplicated(subset="CBSA Code", keep="first")].reset_index(drop=True)
        usa = usa.merge(right = msa_usa[["CBSA Code", "CBSA Title", "Metropolitan/Micropolitan Statistical Area", "FIPS State Code"]],
                how = "inner",
                left_on = "msa",
                right_on = "CBSA Code"
                )
        ## Nos quedamos sólo con áreas metropolitanas
        usa = usa[usa["Metropolitan/Micropolitan Statistical Area"] == "Metropolitan Statistical Area"].reset_index(drop = True)
        usa = usa.drop(columns = ["CBSA Code", "Metropolitan/Micropolitan Statistical Area", "FIPS State Code"]).rename(columns = {"msa" : "zm", "CBSA Title" : "zm_nombre"})
        usa = usa.melt(id_vars=['zm', 'zm_nombre'])
        usa = pd.concat([pd.DataFrame({"anio" : [anio]*usa.shape[0]}), usa], axis = 1)

        usa = usa[usa.variable.isin(acumula_usa)].reset_index(drop=True)

        usa_mex = pd.concat([usa, mex_zm], ignore_index = True)

        usa_mex = usa_mex[["anio", "zm", "zm_nombre", "variable", "value"]]
        trade_cols = {'time':'anio', 'loc':"zm_nombre", 'prod':'variable', 'val':'value'}

        cdata_datos_empleo = ecomplexity(usa, trade_cols)

        cdata_datos_empleo = cdata_datos_empleo.sort_values(by="eci", ascending=False)

        resultado = {i:round(j,3) for i,j in cdata_datos_empleo[~cdata_datos_empleo.duplicated(subset=["eci", "zm_nombre"], keep="first")].iloc[:10][["zm_nombre", "eci"]].to_records(index = False)}
        print(resultado)
