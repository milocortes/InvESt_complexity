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

# Definimos variables
anio_inicio = 2013
anio_final = 2022

# Generamos las matrices para los tres paises en conjunto
guarda_dfs = {}

for anio in range(anio_inicio, anio_final+1):
    # Consultamos la información para cada año en específico
    mex = pd.DataFrame(empleo["MEX"]["datos"]["zm"]["ciiu"][str(anio)][11,:,:], columns = ciiu_recod).astype(int)
    usa = pd.DataFrame(empleo["USA"]["datos"]["ciiu"][str(anio)][:], columns = ciiu_recod).astype(int)
    slv = pd.DataFrame(empleo["SLV"]["datos"]["ciiu-recodificado"]["2013-2022"][:], columns = ciiu_recod).astype(int)
    slv = slv.query(f"zm == {anio}")
    slv["zm"] = "SLV"

    # Renombramos las zonas metropolitanas para MEX y USA
    mex["zm"] = mex["zm"].apply(lambda x: f"{x:05}-MEX")
    usa["zm"] = usa["zm"].apply(lambda x: f"{x:05}-USA")

    matrices_paises = pd.concat([mex, usa, slv], ignore_index = True)
    guarda_dfs[anio] = matrices_paises.copy() 
    matrices_paises.to_csv(os.path.join(OUTPUT_PATH, "matrices_laborales", f"matriz_laboral_{anio}_usa-mex-slv.csv"))


### Usamos el paquete ecomplexity para hacer pruebas de las métricas de complejidad
from ecomplexity import proximity, ecomplexity

### Obtenemos datos sólo para un año 
anio = 2019

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

## Creamos una función que genera los datos de acuerdo al área geográfica y clasificador
def get_datos(pais :str, geografia : str, clasificador: str, industrias_filtro : list = [], industrias_agregacion : bool = False, agrega_slv : bool = False):
    # Realizamos consulta en el hdf5

    if pais == 'MEX':
        datos_empleo = pd.DataFrame(empleo[pais]["datos"][geografia][clasificador][str(anio)][11,:,:], columns = clasificadores_dict[clasificador]).astype(int)
        id_columna_region = datos_empleo.columns[0]
    elif pais == 'USA':
        if clasificador == "ciiu":
            datos_empleo = pd.DataFrame(empleo[pais]["datos"][clasificador][str(anio)][:], columns = clasificadores_dict[clasificador]).astype(int)
            id_columna_region = datos_empleo.columns[0]
            datos_empleo = datos_empleo[datos_empleo[id_columna_region].isin(msa_usa["CBSA Code"].to_list())].reset_index(drop=True)
        elif clasificador == 'naics':
            datos_empleo = pd.DataFrame(empleo[pais]["datos"]['scian-6-digitos'][str(anio)][:], columns = clasificadores_dict[clasificador]).astype(int)
            id_columna_region = datos_empleo.columns[0]
            datos_empleo = datos_empleo[datos_empleo[id_columna_region].isin(msa_usa["CBSA Code"].to_list())].reset_index(drop=True)

    if agrega_slv:
        slv = pd.DataFrame(empleo["SLV"]["datos"]["ciiu-recodificado"]["2013-2022"][:], columns = ciiu_recod).astype(int)
        slv = slv.query(f"zm == {anio}")
        slv["zm"] = "SLV"
        slv = slv.rename(columns = {slv.columns[0] : datos_empleo.columns[0]})
        columnas_no_ceros = list(datos_empleo.set_index("zm").sum()[datos_empleo.set_index("zm").sum() > 0].index)

        #usa = pd.DataFrame(empleo["USA"]["datos"]["ciiu"][str(anio)][:], columns = ciiu_recod).astype(int)
        #usa = usa.rename(columns = {usa.columns[0] : id_columna_region})
        #usa[id_columna_region] = usa[id_columna_region].apply(lambda x: f"{x}-USA") 
        #datos_empleo[id_columna_region] = datos_empleo[id_columna_region].apply(lambda x : f"{x}-MEX")
        datos_empleo = pd.concat([datos_empleo, slv], ignore_index = True)
        datos_empleo = datos_empleo[[id_columna_region]+columnas_no_ceros]
        
    datos_empleo = pd.melt(datos_empleo, id_vars=[id_columna_region])

    # Nos quedamos sólo con manufactura, construcción y servicios públicos
    if industrias_filtro:
        if industrias_agregacion:
            datos_empleo = datos_empleo[datos_empleo["variable"].apply(lambda x: any(x.startswith(f"{i}") for i in industrias_filtro))].reset_index(drop = True)
        else:
            datos_empleo = datos_empleo[datos_empleo["variable"].isin(industrias_filtro)].reset_index(drop = True)

    datos_empleo = pd.concat([
        pd.DataFrame({"anio" : [anio]*datos_empleo.shape[0]}),
        datos_empleo
    ], axis = 1)

    trade_cols = {'time':'anio', 'loc':id_columna_region, 'prod':'variable', 'val':'value'}

    cdata_datos_empleo = ecomplexity(datos_empleo, trade_cols)

    cdata_datos_empleo = cdata_datos_empleo.sort_values(by="eci", ascending=False)
    
    return cdata_datos_empleo

# Zonas Metropolitanas
cdata_mex_zm_imss = get_datos(pais = "MEX", geografia = "zm", clasificador = "imss", industrias_filtro = [2,3,4,5], industrias_agregacion = True)
cdata_mex_zm_imss["zm_nombre"] = cdata_mex_zm_imss["cve_ent"].replace(zm_mex_nombres_zm_cw)
cdata_mex_zm_imss["variable"] = cdata_mex_zm_imss["variable"].astype(int)
cdata_mex_zm_imss["nombre_actividad"] = cdata_mex_zm_imss["variable"].replace(actividades_imss)

{i:j for i,j in cdata_mex_zm_imss[["zm_nombre", "eci"]].to_records(index = False)}

# Entidades

cdata_mex_entidad_imss = get_datos(pais = "MEX", geografia = "entidad", clasificador = "imss", industrias_filtro = [2,3,4,5], industrias_agregacion = True)

cdata_mex_entidad_imss["entidad_nombre"] = cdata_mex_entidad_imss["cve_ent"].replace(zm_mex_nombres_entidad_cw)
cdata_mex_entidad_imss["variable"] = cdata_mex_entidad_imss["variable"].astype(int)
cdata_mex_entidad_imss["nombre_actividad"] = cdata_mex_entidad_imss["variable"].replace(actividades_imss)

{i:j for i,j in cdata_mex_entidad_imss[["entidad_nombre", "eci"]].to_records(index = False)}

## CLASIFICACIÓN SCIAN
# ZM
cdata_mex_zm_scian = get_datos("MEX", "zm", "scian")
cdata_mex_zm_scian["zm_nombre"] = cdata_mex_zm_scian["zm"].replace(zm_mex_nombres_zm_cw)
{i:round(j,3) for i,j in cdata_mex_zm_scian[~cdata_mex_zm_scian.duplicated(subset=["eci", "zm_nombre"], keep="first")].iloc[:70][["zm_nombre", "eci"]].to_records(index = False)}

# Entidad
cdata_mex_entidad_scian = get_datos("MEX", "entidad", "scian")
cdata_mex_entidad_scian["entidad_nombre"] = cdata_mex_entidad_scian["zm"].replace(zm_mex_nombres_entidad_cw)
{i:round(j,3) for i,j in cdata_mex_entidad_scian[~cdata_mex_entidad_scian.duplicated(subset=["eci", "entidad_nombre"], keep="first")].iloc[:32][["entidad_nombre", "eci"]].to_records(index = False)}

## CLASIFICACIÓN CIIU
# ZM
cdata_mex_zm_ciiu = get_datos("MEX", "zm", "ciiu")
cdata_mex_zm_ciiu["zm_nombre"] = cdata_mex_zm_ciiu["zm"].replace(zm_mex_nombres_zm_cw)
{i:round(j,3) for i,j in cdata_mex_zm_ciiu[~cdata_mex_zm_ciiu.duplicated(subset=["eci", "zm_nombre"], keep="first")].iloc[:70][["zm_nombre", "eci"]].to_records(index = False)}

# Entidad
cdata_mex_entidad_ciiu = get_datos("MEX", "entidad", "ciiu")
cdata_mex_entidad_ciiu["entidad_nombre"] = cdata_mex_entidad_ciiu["zm"].replace(zm_mex_nombres_entidad_cw)
{i:round(j,3) for i,j in cdata_mex_entidad_ciiu[~cdata_mex_entidad_ciiu.duplicated(subset=["eci", "entidad_nombre"], keep="first")].iloc[:32][["entidad_nombre", "eci"]].to_records(index = False)}

## CLASIFICACIÓN CIIU (Sólo transables)
transables = pd.read_csv("razon_transables_total_ciiu_usa_2014.csv")\
               .query("razon_transable_total==1.0")\
               ["ciiu"].to_list()

# ZM
cdata_mex_zm_ciiu = get_datos("MEX", "zm", "ciiu", transables, agrega_slv = True)
cdata_mex_zm_ciiu["zm_nombre"] = cdata_mex_zm_ciiu["zm"].replace(zm_mex_nombres_zm_cw)
{i:round(j,3) for i,j in cdata_mex_zm_ciiu[~cdata_mex_zm_ciiu.duplicated(subset=["eci", "zm_nombre"], keep="first")].iloc[:70][["zm_nombre", "eci"]].to_records(index = False)}

# Entidad
cdata_mex_entidad_ciiu = get_datos("MEX", "entidad", "ciiu", transables)
cdata_mex_entidad_ciiu["entidad_nombre"] = cdata_mex_entidad_ciiu["zm"].replace(zm_mex_nombres_entidad_cw)
{i:round(j,3) for i,j in cdata_mex_entidad_ciiu[~cdata_mex_entidad_ciiu.duplicated(subset=["eci", "entidad_nombre"], keep="first")].iloc[:32][["entidad_nombre", "eci"]].to_records(index = False)}


## CLASIFICACIÓN CIIU agregando a El Salvador
# ZM
cdata_mex_zm_ciiu = get_datos("MEX", "zm", "ciiu", agrega_slv = True)
cdata_mex_zm_ciiu["zm_nombre"] = cdata_mex_zm_ciiu["zm"].replace(zm_mex_nombres_zm_cw)
{i:round(j,3) for i,j in cdata_mex_zm_ciiu[~cdata_mex_zm_ciiu.duplicated(subset=["eci", "zm_nombre"], keep="first")].iloc[:len(cdata_mex_zm_ciiu["zm"].unique())][["zm_nombre", "eci"]].to_records(index = False)}

# Entidad
cdata_mex_entidad_ciiu = get_datos("MEX", "entidad", "ciiu", agrega_slv = True)
cdata_mex_entidad_ciiu["entidad_nombre"] = cdata_mex_entidad_ciiu["zm"].replace(zm_mex_nombres_entidad_cw)
{i:round(j,3) for i,j in cdata_mex_entidad_ciiu[~cdata_mex_entidad_ciiu.duplicated(subset=["eci", "entidad_nombre"], keep="first")].iloc[:33][["entidad_nombre", "eci"]].to_records(index = False)}

#### Hacemos ejercicio para USA
msa_usa = pd.read_csv(os.path.join(DICT_PATH, "zonas_metropolitanas", "USA", "msa_usa.csv"))
msa_usa = msa_usa[msa_usa["Metropolitan/Micropolitan Statistical Area"]=="Metropolitan Statistical Area"].reset_index(drop=True)

zm_usa_nombres_msa_cw = {int(i):j for i,j in msa_usa[["CBSA Code", "CBSA Title"]].to_records(index = False)}

## Zona metro y micro politana. Clasificación CIIU
cdata_usa_zm_ciiu = get_datos("USA", "zm", "ciiu")
cdata_usa_zm_ciiu["msa_nombre"] = cdata_usa_zm_ciiu["zm"].replace(zm_usa_nombres_msa_cw)
{i:round(j,3) for i,j in cdata_usa_zm_ciiu[~cdata_usa_zm_ciiu.duplicated(subset=["eci", "msa_nombre"], keep="first")].iloc[:len(cdata_usa_zm_ciiu["msa_nombre"].unique())][["msa_nombre", "eci"]].to_records(index = False)}

## Zona metro y micro politana. Clasificación SCIAN
cdata_usa_zm_naics = get_datos("USA", "zm", "naics")
cdata_usa_zm_naics["msa_nombre"] = cdata_usa_zm_naics["msa"].replace(zm_usa_nombres_msa_cw)
{i:round(j,3) for i,j in cdata_usa_zm_naics[~cdata_usa_zm_naics.duplicated(subset=["eci", "msa_nombre"], keep="first")].iloc[:len(cdata_usa_zm_naics["msa_nombre"].unique())][["msa_nombre", "eci"]].to_records(index = False)}

## Zona metro y micro politana. Clasificación CIIU agregando a El Salvador
cdata_usa_zm_ciiu = get_datos("USA", "estado", "ciiu",agrega_slv = True)
cdata_usa_zm_ciiu["msa_nombre"] = cdata_usa_zm_ciiu["zm"].replace(zm_usa_nombres_msa_cw)
{i:j for i,j in cdata_usa_zm_ciiu[~cdata_usa_zm_ciiu.duplicated(subset=["eci", "msa_nombre"], keep="first")].iloc[:len(cdata_usa_zm_ciiu["msa_nombre"].unique())][["msa_nombre", "eci"]].to_records(index = False)}


##### Reunimos los datos para MEX, USA, SLV
acumula_datos = []

for anio in range(anio_inicio, anio_final):
    print(anio)
    ## Mexico 
    # ZM
    mex = pd.DataFrame(empleo["MEX"]["datos"]["zm"]["ciiu"][str(anio)][11,:,:], columns = ciiu_recod).astype(int)
    # Estado
    mex_estado = pd.DataFrame(empleo["MEX"]["datos"]["entidad"]["ciiu"][str(anio)][11,:,:], columns = ciiu_recod).astype(int)

    usa = pd.DataFrame(empleo["USA"]["datos"]["ciiu"][str(anio)][:], columns = ciiu_recod).astype(int)
    slv = pd.DataFrame(empleo["SLV"]["datos"]["ciiu-recodificado"]["2013-2022"][:], columns = ciiu_recod).astype(int)
    slv = slv.query(f"zm == {anio}")
    slv["zm"] = "SLV"
    slv["pais"] = "SLV"
    slv["tipo_area"] = "Pais"

    ### Agregamos los nombres de las zonas metropolitanas 
    # Mex
    mex["zm_nombre"] = mex["zm"].replace(zm_mex_nombres_zm_cw)
    mex["pais"] = "MEX"
    mex["tipo_area"] = mex["zm_nombre"].apply(lambda x : " ".join(x.split()[:2]))

    mex_estado["zm_nombre"] = mex_estado["zm"].replace(zm_mex_nombres_entidad_cw)
    mex_estado["pais"] = "MEX"
    mex_estado["tipo_area"] = "Estado"
    # USA
    msa_usa = pd.read_csv(os.path.join(DICT_PATH, "zonas_metropolitanas", "USA", "msa_usa.csv"))
    msa_usa = msa_usa[~msa_usa.duplicated(subset="CBSA Code", keep="first")].reset_index(drop=True)
    usa = usa.merge(right = msa_usa[["CBSA Code", "CBSA Title", "Metropolitan/Micropolitan Statistical Area", "FIPS State Code"]],
            how = "inner",
            left_on = "zm",
            right_on = "CBSA Code"
            )
    usa["pais"] = "USA"

    # Agrupampos por estado
    usa_estado = usa[["FIPS State Code"] + list(usa.columns[1:-5])]
    usa_estado = usa_estado.groupby("FIPS State Code").sum().reset_index()
    usa_estado = usa_estado.rename(columns={"FIPS State Code":"zm"})

    usa_id_estados = pd.read_csv(os.path.join(DICT_PATH, "estados", "USA", "output", "usa_id_estados.csv"))
    usa_estado["zm_nombre"] = usa_estado["zm"].replace({i:j for i,j in usa_id_estados.to_records(index = False)})
    usa_estado["pais"] = "USA"
    usa_estado["tipo_area"] = "Estado"

    # Hacemos reshape a los datos
    usa_estado = usa_estado.melt(id_vars = ["zm", "zm_nombre", "pais", "tipo_area"])
    mex_estado = mex_estado.melt(id_vars = ["zm", "zm_nombre", "pais", "tipo_area"])
    mex = mex.melt(id_vars = ["zm", "zm_nombre", "pais", "tipo_area"])
    usa = usa.drop(columns = ["FIPS State Code", "CBSA Code"])
    usa = usa.melt(id_vars = ["zm", "CBSA Title", "pais","Metropolitan/Micropolitan Statistical Area"])
    usa.columns = ["id_area", "nombre_area", "pais_area","tipo_area", "ciiu", "valor"]
    slv["zm_nombre"] = "El Salvador"
    slv = slv.melt(id_vars=["zm", "zm_nombre","pais", "tipo_area"])

    usa_estado.columns = ["id_area", "nombre_area", "pais_area","tipo_area", "ciiu", "valor"]
    mex_estado.columns = ["id_area", "nombre_area", "pais_area","tipo_area", "ciiu", "valor"]
    mex.columns = ["id_area", "nombre_area", "pais_area","tipo_area", "ciiu", "valor"]
    slv.columns = ["id_area", "nombre_area", "pais_area","tipo_area", "ciiu", "valor"]

    # Reunimos todos los datos
    datos_empleo = pd.concat([usa, mex, slv, usa_estado, mex_estado], ignore_index = True)

    # Concatenamos datos de transables
    transables = pd.read_csv("razon_transables_total_ciiu_usa_2014.csv")
    datos_empleo = datos_empleo.merge(right=transables[["ciiu", "razon_transable_total"]], how = "left", on = "ciiu")
    datos_empleo["ciiu_nombre"] = datos_empleo["ciiu"].replace(ciiu_recod_nombres_cw)
    datos_empleo = datos_empleo[["id_area", "nombre_area", "pais_area", "tipo_area", "ciiu", "ciiu_nombre", "razon_transable_total", "valor"]] 
    datos_empleo = pd.concat([pd.DataFrame({"anio" : [anio]*datos_empleo.shape[0]}), datos_empleo], axis = 1)

    datos_empleo["censo"] = 0

    if anio == 2019:
        mex_zm_censo_ciiu = pd.DataFrame(empleo["MEX"]["datos"]["zm"]["ciiu_censo"][str(anio)][11,:,:], columns = ciiu_recod).astype(int)
        mex_zm_censo_scian = pd.DataFrame(empleo["MEX"]["datos"]["zm"]["scian_censo"][str(anio)][11,:,:], columns = scian_tags).astype(int)

        mex_entidad_censo_ciiu = pd.DataFrame(empleo["MEX"]["datos"]["entidad"]["ciiu_censo"][str(anio)][11,:,:], columns = ciiu_recod).astype(int)
        mex_entidad_censo_scian = pd.DataFrame(empleo["MEX"]["datos"]["entidad"]["scian_censo"][str(anio)][11,:,:], columns = scian_tags).astype(int)

        for datos_mexico in [mex_zm_censo_ciiu, mex_zm_censo_scian, mex_entidad_censo_ciiu, mex_entidad_censo_scian]:
            datos_mexico["zm_nombre"] = datos_mexico["zm"].copy()
            datos_mexico["zm_nombre"] = datos_mexico["zm_nombre"].replace(zm_mex_nombres_zm_cw)
            datos_mexico["zm_nombre"] = datos_mexico["zm_nombre"].replace(zm_mex_nombres_entidad_cw)
            datos_mexico["pais"] = "MEX"
            datos_mexico["tipo_area"] = datos_mexico["zm_nombre"].apply(lambda x : " ".join(x.split()[:2] ))

        mex_entidad_censo_ciiu["tipo_area"] = "Estado"
        mex_entidad_censo_scian["tipo_area"] = "Estado"

        mex_entidad_censo_ciiu = mex_entidad_censo_ciiu.melt(id_vars = ["zm", "zm_nombre", "pais", "tipo_area"])
        mex_entidad_censo_scian = mex_entidad_censo_scian.melt(id_vars = ["zm", "zm_nombre", "pais", "tipo_area"])

        mex_zm_censo_ciiu = mex_zm_censo_ciiu.melt(id_vars = ["zm", "zm_nombre", "pais", "tipo_area"])
        mex_zm_censo_scian = mex_zm_censo_scian.melt(id_vars = ["zm", "zm_nombre", "pais", "tipo_area"])

        mex_entidad_censo_ciiu.columns = ["id_area", "nombre_area", "pais_area","tipo_area", "ciiu", "valor"]
        mex_entidad_censo_scian.columns = ["id_area", "nombre_area", "pais_area","tipo_area", "ciiu", "valor"]
        mex_zm_censo_ciiu.columns = ["id_area", "nombre_area", "pais_area","tipo_area", "ciiu", "valor"]
        mex_zm_censo_scian.columns = ["id_area", "nombre_area", "pais_area","tipo_area", "ciiu", "valor"]

        datos_todo_censo_mx = pd.concat([mex_entidad_censo_ciiu,
                                        #mex_entidad_censo_scian,
                                        #mex_zm_censo_scian,
                                        mex_zm_censo_ciiu], ignore_index = True)
        datos_todo_censo_mx = pd.concat([pd.DataFrame({"anio" : [anio]*datos_todo_censo_mx.shape[0]}), datos_todo_censo_mx], axis = 1)    
        datos_todo_censo_mx = datos_todo_censo_mx.merge(right=transables[["ciiu", "razon_transable_total"]], how = "left", on = "ciiu")
        datos_todo_censo_mx["ciiu_nombre"] = datos_todo_censo_mx["ciiu"].replace(ciiu_recod_nombres_cw)
        datos_todo_censo_mx = datos_todo_censo_mx[["anio", "id_area", "nombre_area", "pais_area", "tipo_area", "ciiu", "ciiu_nombre", "razon_transable_total", "valor"]] 
        datos_todo_censo_mx["censo"] = 1    
        
        print()
        datos_empleo = pd.concat([datos_empleo, datos_todo_censo_mx], ignore_index = True)

    acumula_datos.append(datos_empleo)

datos_empleo_todo = pd.concat(acumula_datos, ignore_index = True)

## Test
datos_empleo = datos_empleo_todo.query("anio==2019")
datos_empleo = datos_empleo.query("ciiu_nombre!='CBSA Code'")

### Preguntas: 
### 1) aquí estamos de entrada restringiendo a solo transables, o estamos agregando todo? 

### 2) Una vez que sacamos actividades en las que no hay empleo en Mexico, con cuantas actividades quedamos?
actividades_valor_mexico = list(set(datos_empleo.query("pais_area=='MEX' and tipo_area=='Estado' and valor!=0")["ciiu"]))
actividades_valor_mexico.sort()
print(f"Actividades con empleo en México {len(actividades_valor_mexico)}, de las cuales 71 son transables. En total , hay 135 actividades que son transables")

### 3) Cuantas son estas actividades en las que no hay empleo en Mexico? 
print(len(ciiu_recod) - len(actividades_valor_mexico))

### 4) Que porcentaje del empleo en SLV cae en esas actividades?
actividades_no_mexico = list(set(ciiu_recod) - set(actividades_valor_mexico))
actividades_no_mexico.sort()

actividades_no_mexico_share_slv = datos_empleo[(datos_empleo["id_area"] == "SLV") 
                                    & (datos_empleo["ciiu"].isin(actividades_no_mexico))]\
                                    .query("valor!=0")\
                                    .reset_index(drop=True)

total_empleo_slv = datos_empleo.query("pais_area=='SLV'")["valor"].sum()

actividades_no_mexico_share_slv["razon_empleo_total"] = actividades_no_mexico_share_slv["valor"]/total_empleo_slv

print(f"Porcentaje del empleo en SLV que corresponde a las actividades (transables y no transables) que no están en México : {round(actividades_no_mexico_share_slv['razon_empleo_total'].sum()*100, 2)}%")
print(f"Porcentaje del empleo en SLV que corresponde a las actividades (Sólo transables) que no están en México : {round(actividades_no_mexico_share_slv.query('razon_transable_total!=1')['razon_empleo_total'].sum()*100, 2)}%")


## Todo el empleo
usa_empleo_total_estados = datos_empleo.query("pais_area=='USA' and tipo_area=='Estado'")["valor"].sum()

usa_actividades_mexico = datos_empleo.query("pais_area=='USA' and tipo_area=='Estado'")
usa_actividades_mexico = usa_actividades_mexico[usa_actividades_mexico["ciiu"].isin(actividades_valor_mexico)].reset_index(drop=True)
(usa_actividades_mexico["valor"]/usa_empleo_total_estados).sum()

slv_empleo_total = datos_empleo.query("pais_area=='SLV'")["valor"].sum()
slv_actividades_mexico = datos_empleo.query("pais_area=='SLV'")
slv_actividades_mexico = slv_actividades_mexico[slv_actividades_mexico["ciiu"].isin(actividades_valor_mexico)].reset_index(drop=True)
(slv_actividades_mexico["valor"]/slv_empleo_total).sum()

## Sólo transables EN MEXICO
### De las actividades para las que sólo hay información en México, cual es el peso en SLV y USA?
actividades_valor_mexico = list(set(datos_empleo.query("pais_area=='MEX' and tipo_area=='Estado' and valor!=0 and razon_transable_total==1")["ciiu"]))
actividades_valor_mexico.sort()

usa_empleo_total_estados = datos_empleo.query("pais_area=='USA' and tipo_area=='Estado'")["valor"].sum()

usa_actividades_mexico = datos_empleo.query("pais_area=='USA' and tipo_area=='Estado'")
usa_actividades_mexico = usa_actividades_mexico[usa_actividades_mexico["ciiu"].isin(actividades_valor_mexico)].reset_index(drop=True)
(usa_actividades_mexico["valor"]/usa_empleo_total_estados).sum()

slv_empleo_total = datos_empleo.query("pais_area=='SLV'")["valor"].sum()
slv_actividades_mexico = datos_empleo.query("pais_area=='SLV'")
slv_actividades_mexico = slv_actividades_mexico[slv_actividades_mexico["ciiu"].isin(actividades_valor_mexico)].reset_index(drop=True)
(slv_actividades_mexico["valor"]/slv_empleo_total).sum()

mex_empleo_total = datos_empleo.query("pais_area=='MEX' and tipo_area=='Estado'")["valor"].sum()
mex_actividades_mexico = datos_empleo.query("pais_area=='MEX' and tipo_area=='Estado' and razon_transable_total==1")
mex_actividades_mexico = mex_actividades_mexico[mex_actividades_mexico["ciiu"].isin(actividades_valor_mexico)].reset_index(drop=True)
(mex_actividades_mexico["valor"]/mex_empleo_total).sum()

## Todas las actividades transables 
todas_transables = list(set(datos_empleo.query("razon_transable_total==1")["ciiu"]))
todas_transables.sort()

usa_empleo_total_estados = datos_empleo.query("pais_area=='USA' and tipo_area=='Estado'")["valor"].sum()

usa_actividades_mexico = datos_empleo.query("pais_area=='USA' and tipo_area=='Estado'")
usa_actividades_mexico = usa_actividades_mexico[usa_actividades_mexico["ciiu"].isin(todas_transables)].reset_index(drop=True)
(usa_actividades_mexico["valor"]/usa_empleo_total_estados).sum()

slv_empleo_total = datos_empleo.query("pais_area=='SLV'")["valor"].sum()
slv_actividades_mexico = datos_empleo.query("pais_area=='SLV'")
slv_actividades_mexico = slv_actividades_mexico[slv_actividades_mexico["ciiu"].isin(todas_transables)].reset_index(drop=True)
(slv_actividades_mexico["valor"]/slv_empleo_total).sum()

mex_empleo_total = datos_empleo.query("pais_area=='MEX' and tipo_area=='Estado'")["valor"].sum()
mex_actividades_mexico = datos_empleo.query("pais_area=='MEX' and tipo_area=='Estado'")
mex_actividades_mexico = mex_actividades_mexico[mex_actividades_mexico["ciiu"].isin(todas_transables)].reset_index(drop=True)
(mex_actividades_mexico["valor"]/mex_empleo_total).sum()

##### EJERCICIO DE COMPLEJIDAD
#datos_empleo_complexity = datos_empleo[datos_empleo.ciiu.isin(todas_transables)].query("tipo_area=='Estado' or tipo_area=='Pais'")
#datos_empleo_complexity = datos_empleo_complexity.query("pais_area=='USA'")
actividades_valor_usa = list(set(datos_empleo.query("pais_area=='USA' and tipo_area=='Estado' and razon_transable_total==1")["ciiu"]))
actividades_valor_usa.sort()

datos_empleo_complexity = datos_empleo.query("tipo_area=='Estado' and pais_area=='USA'")
datos_empleo_complexity = datos_empleo_complexity[datos_empleo.ciiu.isin(actividades_valor_usa)]
trade_cols = {'time':'anio', 'loc': "nombre_area", 'prod':'ciiu', 'val':'valor'}

cdata_datos_empleo = ecomplexity(datos_empleo_complexity, trade_cols)

cdata_datos_empleo = cdata_datos_empleo.sort_values(by="eci", ascending=False)

{i:j for i,j in cdata_datos_empleo[~cdata_datos_empleo.duplicated(subset=["eci", "nombre_area"], keep="first")].iloc[:len(cdata_datos_empleo["nombre_area"].unique())][["nombre_area", "eci"]].to_records(index = False)}

### 5) Dado que en el ranking salía USA por delante de todos los otros, pensaría que puede que hayan industrias con data en usa que estén en 0 en SLV o Mex?

# Renombramos las zonas metropolitanas para MEX y USA
mex["zm"] = mex["zm"].apply(lambda x: f"{x:05}-MEX")
usa["zm"] = usa["zm"].apply(lambda x: f"{x:05}-USA")


### Métricas de complejidad
from complexity_measures import *

complexity_data = pd.melt(matrices_paises, id_vars='zm')

value_col_name = "value"
activiy_col_name = "variable"
place_col_name = "zm"

sum_cp_X_cp = complexity_data[[value_col_name]].sum().values[0]
sum_c_X_cp = complexity_data[[activiy_col_name, value_col_name]].groupby(activiy_col_name).sum()

values_RCA = {"df" : complexity_data, 
            "value_col_name" : value_col_name, 
            "activiy_col_name" : activiy_col_name, 
            "sum_cp_X_cp" : sum_cp_X_cp, 
            "sum_c_X_cp" : sum_c_X_cp}

zm_RCA = pd.concat([RCA(**values_RCA, place=p) for p in complexity_data.zm.unique()], ignore_index = True)
zm_RCA = zm_RCA.query("value >= 1.0")
zm_RCA

#####
### Usamos el paquete ecomplexity para hacer pruebas de las métricas de complejidad
from ecomplexity import proximity, ecomplexity
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd 

### Obtenemos datos sólo para un año 
anio = 2019
datos_empleo = pd.read_csv("empleo-SLV-MEX-USA.csv")
actividades_agricolas = [i for i in datos_empleo.ciiu.unique() if i.startswith("0")]
actividades_agricolas_nombres = {i:j for i,j in datos_empleo[datos_empleo.ciiu.isin(actividades_agricolas)][["ciiu", "ciiu_nombre"]].to_records(index=False)}
entidades_mexicanas = ['Ciudad de México']
complemento_entidades_mexicanas = list(set(datos_empleo.query("tipo_area=='Estado' and pais_area=='MEX'").nombre_area.unique()) - set(entidades_mexicanas))

datos_empleo_complexity = datos_empleo.query(f"(tipo_area=='Estado' and censo==0 and anio=={anio} and razon_transable_total==1) or (tipo_area=='Estado' and pais_area=='USA'  and anio=={anio} and razon_transable_total==1) ")
datos_empleo_complexity = datos_empleo_complexity[~datos_empleo_complexity.ciiu.isin(actividades_agricolas)].reset_index(drop=True)
datos_empleo_complexity = datos_empleo_complexity[~datos_empleo_complexity.isin(complemento_entidades_mexicanas)]

trade_cols = {'time':'anio', 'loc': "nombre_area", 'prod':'ciiu', 'val':'valor'}

cdata_datos_empleo = ecomplexity(datos_empleo_complexity, trade_cols)

cdata_datos_empleo = cdata_datos_empleo.sort_values(by="eci", ascending=False)

{i:j for i,j in cdata_datos_empleo[~cdata_datos_empleo.duplicated(subset=["eci", "nombre_area"], keep="first")].iloc[:len(cdata_datos_empleo["nombre_area"].unique())][["nombre_area", "eci"]].to_records(index = False)}

glue = datos_empleo_complexity.pivot(index = 'nombre_area', columns = 'ciiu', values = 'valor')
sns.heatmap(glue)
plt.show()

### Entidades mexicanas y el salvador
