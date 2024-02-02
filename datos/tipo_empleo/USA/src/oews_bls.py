import h5py
import os 
import pandas as pd 
import json 
import numpy as np

# Definimos rutas
PATH_FILE = os.getcwd()
HDF5_PATH = os.path.abspath(os.path.join(PATH_FILE, *[".."]*4, "output"))
CW_PATH = os.path.abspath(os.path.join(PATH_FILE, *[".."]*4, "datos", "cws", "empleo"))
DATA_PATH = os.path.abspath(os.path.join(PATH_FILE, "..", "datos"))
OUTPUT_PATH = os.path.abspath(os.path.join(PATH_FILE, "..", "output"))


## Cargamos cw
# El siguiente crosswalk no tiene la recodificación de la metología de diodato
isic_4_to_naics_2017 = json.load(open(os.path.join(CW_PATH,"ciiu-recodificacion-dario-diodato", "output", "ciiu_recodificado_naics_2017.json"), "r"))

todas_naics = []
for i,j in isic_4_to_naics_2017.items():
    todas_naics.extend(j)

# Carga datos de empleo
empleo = h5py.File(os.path.join(HDF5_PATH, 'complexity_empleo.hdf5'), "r")

# Obtenemos listas de clasificadores
naics_tags_3d = [str(i, encoding = "UTF-8") for i in empleo["USA"]["tags"]["scian-3-digitos"]["tag"][:]]
naics_tags_4d = [str(i, encoding = "UTF-8") for i in empleo["USA"]["tags"]["scian-4-digitos"]["tag"][:]]
naics_tags_6d = [str(i, encoding = "UTF-8") for i in empleo["USA"]["tags"]["scian-6-digitos"]["tag"][:]]

# Cargamos datos de empleo
usa_3d = pd.DataFrame(empleo["USA"]["datos"]["scian-3-digitos"]["2019"][:], columns = naics_tags_3d).\
            set_index("msa").sum(axis = 0).reset_index()

usa_4d = pd.DataFrame(empleo["USA"]["datos"]["scian-4-digitos"]["2019"][:], columns = naics_tags_4d).\
            set_index("msa").sum(axis = 0).reset_index()

usa_6d = pd.DataFrame(empleo["USA"]["datos"]["scian-6-digitos"]["2019"][:], columns = naics_tags_6d).\
            set_index("msa").sum(axis = 0).reset_index()

usa_3d.columns = ["subsector","empleo"]
usa_4d.columns = ["rama","empleo"]
usa_6d.columns = ["clase","empleo"]

# Cargamos datos de empleo
occ_6d = pd.read_excel(os.path.join(DATA_PATH, "nat5d_6d_M2017_dl.xlsx"), sheet_name = "nat5d_dl")
occ_6d = occ_6d.query("OCC_CODE!='00-0000'")

occ_4d = pd.read_excel(os.path.join(DATA_PATH, "nat4d_M2017_dl.xlsx"), sheet_name = "nat4d_dl_1")
occ_4d = occ_4d.query("OCC_CODE!='00-0000'")
occ_4d = occ_4d.query("OCC_GROUP=='detailed'")
occ_6d = occ_6d.query("OCC_GROUP=='detailed'")

coinciden_occ_6d = list(set(todas_naics).intersection([str(i) for i in occ_6d.NAICS.unique()]))

# Generamos diccionario de correspondencias actividades naics 4 digitos y naics 6 digitos
naics_4d_to_6d = {i : [] for i in usa_4d.rama.unique()}

for k,v in naics_4d_to_6d.items():
    for clase in usa_6d.clase.unique():
        if clase.startswith(k):
            v.append(clase)

# En los datos de tipo de ocupación para 4 dígitos hay sectores que necesitan ser agregados a 3 dígitos
occ_4d["NAICS"] = occ_4d.NAICS.apply(lambda x: x[:3] if "A" in x else x[:4])

# Generamos un mapeo subsector-rama para posteriormente quitar las ramas
naics_3d_4d = {i:[] for i in occ_4d["NAICS"].unique() if len(i)==3}

for k,v in naics_3d_4d.items():
    for j in occ_4d["NAICS"].unique():
        if len(j)!=3:
            if j.startswith(k):
                v.append(j[:4])

for k,v in naics_3d_4d.items():
    ramas_compara = [i for i in usa_4d.rama.unique() if i.startswith(k)]
    naics_3d_4d[k] = list(set(ramas_compara) - set(v))

# Del mapeo subsector-rama creamos un mapeo subsector clase 
naics_3d_6d = {i:[] for i in naics_3d_4d}

for k,v in naics_3d_4d.items():
    acumula_clases = []
    for rama in v:
        for naics_clase in todas_naics:
            if naics_clase.startswith(k):
                acumula_clases.append(naics_clase)
    naics_3d_6d[k] = list(set(acumula_clases) - set(coinciden_occ_6d))

### Generamos dataframes con los ponderadores de rama a clase y subsector a clase

#-- Subsector a clase
acumula_3d_6d = []

for subsector, sub_clases in naics_3d_6d.items():
    df_parcial = usa_6d[usa_6d.clase.isin(sub_clases)].reset_index(drop=True)
    df_parcial["share"] = df_parcial["empleo"]/df_parcial["empleo"].sum()
    occ_4d_parcial = occ_4d.query(f"NAICS =='{subsector}'")[["NAICS","OCC_CODE", "TOT_EMP"]]
    occ_4d_parcial_cross = occ_4d_parcial.merge(right = df_parcial, how = "cross")
    acumula_3d_6d.append(occ_4d_parcial_cross)

acumula_3d_6d = pd.concat(acumula_3d_6d, ignore_index = True)
acumula_3d_6d = acumula_3d_6d.query("TOT_EMP!='**'")
acumula_3d_6d["occ_empleo"] = (acumula_3d_6d["TOT_EMP"]*acumula_3d_6d["share"]).astype(int)

#-- Rama a clase
acumula_4d_6d = []

for subsector, sub_clases in naics_4d_to_6d.items():
    df_parcial = usa_6d[usa_6d.clase.isin(sub_clases)].reset_index(drop=True)
    df_parcial["share"] = df_parcial["empleo"]/df_parcial["empleo"].sum()
    occ_4d_parcial = occ_4d.query(f"NAICS =='{subsector}'")[["NAICS","OCC_CODE", "TOT_EMP"]]
    occ_4d_parcial_cross = occ_4d_parcial.merge(right = df_parcial, how = "cross")
    acumula_4d_6d.append(occ_4d_parcial_cross)

acumula_4d_6d = pd.concat(acumula_4d_6d, ignore_index = True)
acumula_4d_6d = acumula_4d_6d.query("TOT_EMP!='**'")
acumula_4d_6d.share = acumula_4d_6d.share.replace(np.nan, 0.0)
acumula_4d_6d["occ_empleo"] = (acumula_4d_6d["TOT_EMP"]*acumula_4d_6d["share"]).astype(int)

#-- Clase a clase
acumula_6d_6d = occ_6d[occ_6d.NAICS.isin([int(i) for i in coinciden_occ_6d])][["NAICS","OCC_CODE", "TOT_EMP"]].copy()
acumula_6d_6d.columns = ["clase", "OCC_CODE", "occ_empleo"]
acumula_6d_6d = acumula_6d_6d.query("occ_empleo!='**'")

occ_empleo_total = pd.concat([acumula_3d_6d[["clase","OCC_CODE", "occ_empleo"]],
                              acumula_4d_6d[["clase","OCC_CODE", "occ_empleo"]],
                              acumula_6d_6d], 
                              ignore_index=True)

### Reclasificamos a CIIU-Rev 4 recodificado
occ_empleo_total = occ_empleo_total.drop_duplicates(subset = ["clase", "OCC_CODE"])
occ_empleo_total = occ_empleo_total.pivot(index = ["OCC_CODE"], columns = ["clase"], values = ["occ_empleo"]).reset_index()
occ_empleo_total = occ_empleo_total.replace(np.nan, 0)
occ_empleo_total.columns = ['OCC_CODE'] + [i[1] for i in occ_empleo_total.columns[1:]]

ciiu_occ_empleo_total = occ_empleo_total[["OCC_CODE"]]

for k,v in isic_4_to_naics_2017.items():
    coinciden_columnas = list(set(occ_empleo_total.columns).intersection(v))

    if coinciden_columnas:
        ciiu_occ_empleo_total[k] = occ_empleo_total[coinciden_columnas].sum(axis = 1)
    else:
        ciiu_occ_empleo_total[k] = 0

ciiu_occ_empleo_total_long = ciiu_occ_empleo_total.melt(id_vars = ["OCC_CODE"])
ciiu_occ_empleo_total_long.columns = ["occ_code", "ciiu", "coempleo"]
ciiu_occ_empleo_total_long["anio"] = 2017
ciiu_occ_empleo_total_long = ciiu_occ_empleo_total_long[["anio"]+["occ_code", "ciiu", "coempleo"]]

## Guardamos los datos
ciiu_occ_empleo_total_long.to_csv(os.path.join(OUTPUT_PATH, "usa_ciiu_occ_empleo.csv"), index = False)

