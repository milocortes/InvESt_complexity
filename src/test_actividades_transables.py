import pandas as pd 
import os 
import h5py
import json
import numpy as np 

# Definimos rutas
PATH_FILE = os.getcwd()
OUTPUT_PATH = os.path.abspath(os.path.join(PATH_FILE, "..", "output"))
CW_PATH = os.path.abspath(os.path.join(PATH_FILE, "..", "datos", "cws", "empleo"))
DICT_PATH = os.path.abspath(os.path.join(PATH_FILE, "..", "datos", "diccionarios"))

# Carga datos de empleo
empleo = h5py.File(os.path.join(OUTPUT_PATH, 'complexity_empleo.hdf5'), "r")

# CIIU-recodificado
scian_2018 = [str(i, encoding = "UTF-8") for i in empleo["MEX"]["tags"]["scian"]["tag"][:]]
naics_2017 = [str(i, encoding = "UTF-8") for i in empleo["USA"]["tags"]['scian-6-digitos']["tag"][:]]

# Definimos variables
anio_inicio = 2013
anio_final = 2021

# Generamos las matrices para mexico y usa
guarda_dfs = {}


### Cargamos cw entre naics-scian a ciiu
## Cargamos el crosswalk entre ciiu y scian
cw_ciiu_scian = json.load(open(os.path.join(CW_PATH, "ciiu-recodificacion-dario-diodato", "output", "ciiu_recodificado_scian_2018.json"), "r"))

## Cargamos el crosswalk entre ciiu y naics
isic_4_to_naics_2017 = json.load(open(os.path.join(CW_PATH,"ciiu-recodificacion-dario-diodato", "output", "ciiu_recodificado_naics_2017.json"), "r"))

### Cargamos las clases que son transables en naics 2017
transables_naics_2017 = json.load(open(os.path.join(DICT_PATH, "traded_clusters_appendix", "output", "clases_transables_naics_2017.json"), "r"))
transables_naics_2017 = [str(i) for i in transables_naics_2017["clases_transables"]]

anio = 2014

mex_scian = pd.DataFrame(empleo["MEX"]["datos"]["zm"]["scian"][str(anio)][11,:,:], columns = scian_2018).astype(int)
usa_scian = pd.DataFrame(empleo["USA"]["datos"]["scian-6-digitos"][str(anio)][:], columns = naics_2017).astype(int)
usa_scian = usa_scian[usa_scian.columns[1:]].sum()

mex_ciiu = mex_scian[["zm"]]

for ciiu, scian_clases in cw_ciiu_scian.items():
    clases_coinciden = list(set(scian_clases).intersection(mex_scian.columns))
    clases_coinciden_transables = list(set(clases_coinciden).intersection(transables_naics_2017))
    print(f"{ciiu} --> clases transable --> {clases_coinciden_transables}")

    mex_ciiu[ciiu] = mex_scian[clases_coinciden].sum(axis=1)
    mex_ciiu[f"{ciiu}_transable"] = mex_scian[clases_coinciden_transables].sum(axis=1)/mex_ciiu[ciiu]


transables_ciiu_usa = []

for ciiu, naics_clases in isic_4_to_naics_2017.items():
    clases_coinciden = list(set(naics_clases).intersection(usa_scian.keys()))
    clases_coinciden_transables = list(set(clases_coinciden).intersection(transables_naics_2017))
    
    ciiu_total = usa_scian[clases_coinciden].sum()

    if clases_coinciden_transables:
        ciiu_transable = usa_scian[clases_coinciden_transables].sum()
    else:
        ciiu_transable = 0
    transables_ciiu_usa.append(
        (ciiu, ciiu_total, ciiu_transable)
    )

df_transables_ciiu_usa = pd.DataFrame(transables_ciiu_usa, columns = ["ciiu", "total", "transable"])
df_transables_ciiu_usa["razon_transable_total"] = df_transables_ciiu_usa["transable"]/df_transables_ciiu_usa["total"]
df_transables_ciiu_usa.replace(np.nan, 0.0, inplace = True)

df_transables_ciiu_usa = df_transables_ciiu_usa.sort_values(by = "razon_transable_total", ascending = False).reset_index(drop=True)
