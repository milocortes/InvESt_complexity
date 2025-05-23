import pandas as pd
import matplotlib.pyplot as plt 
import os 
import polars as pl
import re

from utils import HSAData 

### Define paths
def build_path(PATHS):
    return os.path.abspath(os.path.join(*PATHS))

FILE_PATH = os.getcwd()
DATA_PATH = build_path([FILE_PATH,"data"])
OUTPUT_PATH = build_path([FILE_PATH,"output"])

BILATERAL_TRADE_FP = build_path([DATA_PATH, "hs92_country_country_product_year_6_2020_2023.csv"])
UNILATERAL_TRADE_FP = build_path([DATA_PATH, "hs92_country_product_year_4.csv"])
CLASIFICACION_TRADE_FP = build_path([DATA_PATH, "product_hs92.csv"])
ECI_TRADE_FP = build_path([DATA_PATH, "growth_proj_eci_rankings.csv"])

SLV_EXTENSIVO_INTENSIVO = build_path([OUTPUT_PATH, "asia_shares_extensivo_intensivo.csv"])
HS2_SLV_EXTENSIVO_INTENSIVO = build_path([OUTPUT_PATH, "hs2_asia_shares_extensivo_intensivo.csv"])
HS_CORRESPONDENCIAS_FP = build_path([OUTPUT_PATH, "hs_correspondencias.csv"])

# International Trade Data (HS92) (Bilateral Trade, HS92, 6 digit, 2020-2023)
# This dataset contains information about International Trade Data (HS92). It includes data from 2020-2023 and is classified as Bilateral Trade with HS92 classification at the 6-digit level.

q = (
    pl.scan_csv(BILATERAL_TRADE_FP, ignore_errors=True)
    .select(["country_id","country_iso3_code","partner_country_id","partner_iso3_code","product_id","product_hs92_code","year","export_value", "import_value"])
    .filter(
        (pl.col('country_iso3_code') == "USA") 
    )
)

df = q.collect().to_pandas()



# International Trade Data (HS92) (Unilateral Trade, HS92, 4 digit, 1995-2023)
# This dataset contains information about International Trade Data (HS92). It includes data from 1995-2023 and is classified as Unilateral Trade with HS92 classification at the 4-digit level.
pais = "SLV"
uni_trade = pd.read_csv("data/hs92_country_product_year_4.csv").query(f"country_iso3_code=='{pais}'")

## Exportaciones SLV a sus socios
q_slv = (
    pl.scan_csv(BILATERAL_TRADE_FP, ignore_errors=True)
    .select(["country_id","country_iso3_code","partner_country_id","partner_iso3_code","product_id","product_hs92_code","year","export_value", "import_value"])
    .filter(
        (pl.col('country_iso3_code') == pais) 
    )
)

exports_from_slv2usa = q_slv.collect().to_pandas().query("partner_iso3_code=='USA'")
exports_from_slv2usa = exports_from_slv2usa.rename(columns = {"export_value" : "export_value_to_usa"})
exports_from_slv2usa.product_hs92_code = exports_from_slv2usa.product_hs92_code.astype(int).astype(str)
exports_from_slv2usa["product_hs92_code_4d"] = exports_from_slv2usa["product_hs92_code"].apply(lambda x : str(x)[:4])

exports_from_slv2usa = exports_from_slv2usa.groupby(["product_hs92_code_4d", "year"]).agg({"export_value_to_usa" : "sum"}).reset_index()

exports_from_slv2world = q_slv.collect().to_pandas()
exports_from_slv2world.product_hs92_code = exports_from_slv2world.product_hs92_code.astype(str)
exports_from_slv2world["product_hs92_code_4d"] = exports_from_slv2world["product_hs92_code"].apply(lambda x : str(x)[:4])

exports_from_slv2world = exports_from_slv2world.groupby(["product_hs92_code_4d", "year"]).agg({"export_value" : "sum"}).reset_index()

exports_from_slv2usa = exports_from_slv2usa.merge(right=exports_from_slv2world, how = "inner", on = ["year","product_hs92_code_4d"])
exports_from_slv2usa["export_share_to_usa"] = exports_from_slv2usa["export_value_to_usa"]/exports_from_slv2usa["export_value"]


### Agrupados datos de comercio a HS 4 digitos
## Paises a investigar China, Vietnam, Camboya, Malasia, Indonesia
paises = ["CHN", "VNM", "KHM", "MYS", "IDN"]

df["tag"] = "" 
df.loc[df.partner_iso3_code.isin(paises), "tag"] = "paises_interes"
df.loc[~df.partner_iso3_code.isin(paises), "tag"] = "rest_of_world"

df["product_hs92_code_4d"] = df["product_hs92_code"].apply(lambda x : str(x)[:4])

df = df.groupby(["tag", "year", "product_hs92_code_4d"]).agg({"import_value" : "sum"}).reset_index()

df = df.dropna()

### Razón de importaciones con respecto al total que provienen China, Vietnam, Camboya, Malasia, Indonesia
df["share_on_total_imports"] = df["import_value"]  / df.groupby(["product_hs92_code_4d", "year"])['import_value'].transform('sum')

### Nos quedamos con los paises de interés 
df = df.query("tag=='paises_interes'").reset_index(drop=True)

### Combina información de complejidad
columnas = ["country_iso3_code", "year","product_hs92_code", "global_market_share" , "export_value", "export_rca", "distance", "cog", "pci"]
uni_trade = uni_trade[columnas]

#uni_trade = uni_trade.merge(right=df, how = "inner", right_on="product_hs92_code_4d", left_on="product_hs92_code")
uni_trade = df.merge(right=uni_trade, how = "inner", right_on=["product_hs92_code", "year"], left_on=["product_hs92_code_4d", "year"])

### Agrega dato de ECI
eci_paises = pd.read_csv(ECI_TRADE_FP)
eci_paises = eci_paises[["country_iso3_code", "year", "eci_hs92"]]

uni_trade = uni_trade.merge(right=eci_paises, how="inner", on=["country_iso3_code", "year"])

### Agrega nombres de clasificación
hs_dic = pd.read_csv(CLASIFICACION_TRADE_FP)
hs_data = HSAData(hs_dic)

df_hs_correspondencias = hs_data.build_correspondence()
uni_trade = uni_trade.merge(right=df_hs_correspondencias, how = "inner", on="product_hs92_code_4d")
uni_trade = uni_trade.merge(right=exports_from_slv2usa[["year", "product_hs92_code_4d", "export_share_to_usa"]], how = "inner", on = ["year", "product_hs92_code_4d"])

### Guarda datos
uni_trade.to_csv(SLV_EXTENSIVO_INTENSIVO, index = False)
df_hs_correspondencias.to_csv(HS_CORRESPONDENCIAS_FP, index = False)

agg_vals = {"share_on_total_imports" : "mean", "distance" : "mean", "cog" : "mean", "pci" : "mean", "eci_hs92" : "mean", "export_share_to_usa" : "mean", "export_rca" : "mean", "export_value" : "sum"}
cols_vals = ["product_hs92_code_2d", "year", 'product_hs92_name_2d', 'product_hs92_code_1d', 'product_hs92_name_1d']

hs2_uni_trade = uni_trade.groupby(cols_vals).agg(agg_vals).reset_index()
hs2_uni_trade.to_csv(HS2_SLV_EXTENSIVO_INTENSIVO, index=False)
