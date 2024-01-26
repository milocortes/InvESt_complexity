import pandas as pd 

zm = pd.read_excel("mpios_en_metropoli.xlsx", sheet_name = "real")
zm["NOMGEO"] = zm["NOMGEO"].apply(lambda x: x.split(",")[0])
zm["cve_entidad"] = zm["CVEGEO"].apply(lambda x : str(x)[:-3])

zm["llave"] =  zm["cve_entidad"] + "-"+ zm["NOMGEO"]

imss_muni = pd.read_csv("entidad-municipio-imss.csv")

imss_muni["llave"] = imss_muni["cve_entidad"].apply(lambda x : str(x)) + "-" + imss_muni["descripción municipio"]

zm["llave"] = zm["llave"].str.lower()
imss_muni["llave"] = imss_muni["llave"].str.lower()

zm_nuevo = zm.merge(right=imss_muni, how = "inner", on="llave")
#set(zm_nuevo["llave"]) - set(zm.merge(right=imss_muni, how = "inner", on="llave")["llave"])

# Agrega CDMX

CDMX = pd.DataFrame({"CVE_ZONA" : ["09.1.01"],
"NOM_ZM" : ["Zona metropolitana de la Ciudad de MΘxico"],
"NOMGEO_COR" : ["Ciudad de MΘxico"],
"TIPOMET" : ["Zona metropolitana"],
"CVEGEO" : [15125],
"NOM_ENT" : ["Ciudad de México"],
"NOMGEO" : ["Ciudad de México"],
"cve_entidad_x" : [9],
"llave" : ["9-Ciudad de México"],
"cve_municipio" : ["CDMX"],
"cve_delegacion" : [9],
"cve_entidad_y" : [9],
"descripción entidad" : ["Ciudad de México"],
"descripción municipio" : ["Ciudad de México"]})

zm_nuevo = pd.concat([zm_nuevo, CDMX], ignore_index = True)
zm_nuevo["CLAVE"] = zm_nuevo['cve_entidad_x'].apply(lambda x : str(x)) + "-" + zm_nuevo["cve_municipio"]

zm_minimo = zm_nuevo[["CVE_ZONA", "CLAVE"]]
zm_minimo.to_csv("zm_imss_muni.csv", index = False)