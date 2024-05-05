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

ciiu_recod = [str(i, encoding = "UTF-8") for i in empleo["SLV"]["tags"]["ciiu-original"][:]]


slv_empleo = pd.DataFrame(empleo["SLV"]["datos"]["ciiu-original"]["2013-2022"], columns = ciiu_recod).query("anio==2019")
slv_empleo = slv_empleo[slv_empleo.columns[1:]]

cw = pd.read_csv(os.path.join(CW_PATH, "ciiu-recodificacion-dario-diodato", "output", "recodificacion_ciiu-rev-4.csv"))

guarda = {}
no_tiene = []

for ciiu_lab in [i for i in cw.ciiu_nueva_cod if "-" in i]:


    ciiu_code = cw.query(f"ciiu_nueva_cod=='{ciiu_lab}'").actividades_ciiu_integra.values[0].split(",")
    ciiu_nombre = cw.query(f"ciiu_nueva_cod=='{ciiu_lab}'").descripcion_codigo_nuevo.values[0].split("/-/")

    minimo = 0
    
    ciiu_actividad = None

    for i,j in zip(ciiu_code, ciiu_nombre):

        

        if i in list(slv_empleo.columns):
            compara_valor = slv_empleo[i].values[0]

            if compara_valor > minimo:
                ciiu_actividad = i 
                ciiu_actividad_nombre = j



    if ciiu_actividad:
        guarda[ciiu_lab] = (ciiu_lab, ciiu_actividad, ciiu_actividad_nombre)
    else: 
        no_tiene.append(ciiu_lab)
    
    
ciiu_slv_actividades = pd.DataFrame([i for i in guarda.values()], columns = ["ciiu_recodificado", "ciiu_original", "ciiu_original_nombre"])
ciiu_no_tiene = cw[cw.ciiu_nueva_cod.isin(no_tiene)]

ciiu_slv_actividades.to_csv("ciiu_slv_actividades_importantes.csv", index = False)
ciiu_no_tiene.to_csv("ciiu_slv_actividades_no_tiene_empleo.csv", index = False)
