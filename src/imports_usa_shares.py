import pandas as pd
import matplotlib.pyplot as plt 
import os 
import polars as pl
import re

### Define paths
def build_path(PATHS):
    return os.path.abspath(os.path.join(*PATHS))

FILE_PATH = os.getcwd()

CW_DATA_PATH = build_path([FILE_PATH, "..", "datos", "cws", "empleo", "ciiu-recodificacion-dario-diodato", "output"])

CIIU_NAICS_FP = build_path([CW_DATA_PATH, "ciiu_recodificado_naics_2017.csv"])


## Read Country Trade by Partner and Product data 
q = (
    pl.scan_csv('hs92_country_country_product_year_6_2020_2023.csv', ignore_errors=True)
    .select(["country_id","country_iso3_code","partner_country_id","partner_iso3_code","product_id","product_hs92_code","year","export_value", "import_value"])
    .filter(
        (pl.col('country_iso3_code') == "USA") 
    )
)

df = q.collect().to_pandas()

## Read CW NAICS 2017 - HS
naics2hs = pd.read_csv("naics_2017_to_hs.csv")

## Paises a investigar China, Vietnam, Camboya, Malasia, Indonesia
paises = ["CHN", "VNM", "KHM", "MYS", "IDN"]

df["tag"] = "" 
df.loc[df.partner_iso3_code.isin(paises), "tag"] = "paises_interes"
df.loc[~df.partner_iso3_code.isin(paises), "tag"] = "rest_of_world"

## Agrupamos por paises pertenecientes al grupo y el resto de mundo
df = df.groupby(["tag", "year", "product_hs92_code"]).agg({"import_value" : "sum"}).reset_index()
df["product_hs92_code"] = df["product_hs92_code"].astype(int).astype(str)

naics2hs["hs"] = naics2hs["hs"].astype(str)

complete_hs_data = []

for naics in naics2hs["naics_original"].unique():
    print(naics)
    partial_n2h = naics2hs.query(f"naics_original=={naics}")
    hs_data = df[df["product_hs92_code"].isin(partial_n2h.hs)]
    hs_data["weight"] = hs_data["product_hs92_code"]
    hs_data["weight"] = hs_data["weight"].replace({i:j for i,j in partial_n2h[["hs", "weight"]].to_records(index = False)})
    hs_data["naics"] = naics

    complete_hs_data.append(hs_data)


complete_hs_data = pd.concat(complete_hs_data, ignore_index = True)

complete_hs_data["import_weighted_value"] = complete_hs_data["import_value"]*complete_hs_data["weight"]

complete_hs_data = complete_hs_data.groupby(["naics", "tag", "year"]).agg({"import_weighted_value" : "sum"}).reset_index()

### El Salvador Data
df_slv = pd.read_csv("extensivo_slv_multicriteria.csv")
ciiu_naics = pd.read_csv(CIIU_NAICS_FP)
ciiu_naics = ciiu_naics[ciiu_naics.ciiu.isin(df_slv.variable)].reset_index(drop = True)


complete_hs_data = complete_hs_data.merge(right=ciiu_naics, how="inner", left_on="naics", right_on="naics_2017")

ciiu_complete_hs_data = complete_hs_data.groupby(["ciiu", "tag", "year"]).agg({"import_weighted_value" : "sum"}).reset_index()



ciiu_complete_hs_data["share_on_total_imports"] = ciiu_complete_hs_data["import_weighted_value"]  / ciiu_complete_hs_data.groupby(["ciiu", "year"])['import_weighted_value'].transform('sum')

ciiu_complete_hs_data = ciiu_complete_hs_data.merge(right=df_slv[['variable', 'division', 'seccion', 'ciiu_nombre', 'pci', 'cog', 'distance', 'rca']], how = "inner", left_on="ciiu", right_on="variable")

ciiu_complete_hs_data.ciiu_nombre = ciiu_complete_hs_data.ciiu_nombre.apply(lambda x : re.sub("\(.*?\)|\[.*?\]","",x).replace("Fabricación de","").title().split(" /-/")[0])


ciiu_complete_hs_data.division = ciiu_complete_hs_data.division.str.split(";").str[0]
ciiu_complete_hs_data.division = ciiu_complete_hs_data.division.str.replace("Elaboración de ", "")
ciiu_complete_hs_data.division = ciiu_complete_hs_data.division.str.replace("Fabricación de","")
ciiu_complete_hs_data.division = ciiu_complete_hs_data.division.str.replace("Producción de ","")
ciiu_complete_hs_data.division = ciiu_complete_hs_data.division.str.replace("Extracción de ","")
ciiu_complete_hs_data.division = ciiu_complete_hs_data.division.str.title()
ciiu_complete_hs_data.division = ciiu_complete_hs_data.division.str.strip()

ciiu_complete_hs_data.to_csv("paises_asia_ciiu_complete_hs_data.csv", index = False)

"""

para_graficar = ciiu_complete_hs_data.query("year == 2023 and tag == 'paises_interes'")


para_graficar = para_graficar.merge(right=df_slv[['division', 'seccion', 'ciiu_nombre', 'pci', 'cog', 'distance', 'rca']], how = "inner", left_on="ciiu", right_on="variable")

para_graficar.ciiu_nombre = para_graficar.ciiu_nombre.apply(lambda x : re.sub("\(.*?\)|\[.*?\]","",x).replace("Fabricación de","").title().split(" /-/")[0])


fig, ax = plt.subplots()
ax.scatter(para_graficar.distance, para_graficar.share_on_total_imports)


for i, txt in enumerate(para_graficar.ciiu_nombre):
    ax.annotate(txt, (para_graficar.distance[i] - 0.02, para_graficar.share_on_total_imports[i] + 0.01))
plt.xlim([0.6, 1.2]) 
plt.show()



#ciiu_gp = ciiu_naics.groupby("ciiu")
#ciiu_cw = {ciiu : ciiu_naics.iloc[ciiu_gp.groups[ciiu]].naics_2017.to_list() for ciiu in ciiu_gp.indices if  ciiu in set(df.variable)}


### Download hsproducts import-exports values
#data_url = "https://intl-atlas-downloads.s3.amazonaws.com/country_hsproduct4digit_year.csv.zip"
#data = pd.read_csv(data_url, compression="zip", low_memory=False)
#hscomerce = pd.read_csv("country_hsproduct4digit_year.csv")
"""
