import pandas as pd
import matplotlib.pyplot as plt 
import os 
import polars as pl
import re

### Define paths
def build_path(PATHS):
    return os.path.abspath(os.path.join(*PATHS))

FILE_PATH = os.getcwd()

## Read Country Trade by Partner and Product data 
q = (
    pl.scan_csv('hs92_country_country_product_year_6_2020_2023.csv', ignore_errors=True)
    .select(["country_id","country_iso3_code","partner_country_id","partner_iso3_code","product_id","product_hs92_code","year","export_value", "import_value"])
    .filter(
        (pl.col('country_iso3_code') == "USA") 
    )
)

df = q.collect().to_pandas()

### Industrias priorizadas INTENSIVO
data_slv = [(3003,"Medicaments, not packaged"),
(3004,"Medicaments, packaged"),
(3006,"Pharmaceutical goods"),
(3208,"Paints and varnishes, nonaqueous"),
(3212,"Pigments, nonaqueous"),
(3215,"Ink"),
(3305,"Hair products"),
(3406,"Candles"),
(3809,"Finishing agents"),
(3810,"Pickling preparations for metal surfaces"),
(3904,"Polymers of vinyl chloride"),
(3920,"Other plates of plastics, noncellular and not reinforced"),
(3921,"Other plastic plates, sheets etc."),
(3926,"Other articles of plastic"),
(4809,"Carbon paper"),
(4811,"Cellulose wadding, coated"),
(4901,"Books, brochures etc."),
(4908,"Transfers (decalcomanias)"),
(4911,"Other printed matter"),
(5503,"Synthetic staple fibers"),
(6810,"Articles of cement, of concrete or of artificial stone"),
(7225,"Flat-rolled products of other alloy steel, width > 600 mm"),
(7226,"Flat-rolled products of other alloy steel, width < 600 mm"),
(7308,"Structures and their parts, of iron or steel"),
(7309,"Tanks etc. > 300 liters, iron or steel"),
(7607,"Aluminum foil < 0.2 mm"),
(8211,"Knife sets"),
(8452,"Sewing machines"),
(8532,"Electrical capacitors"),
(9607,"Slide fasteners")]


data_slv = pd.DataFrame(data_slv, columns = ["hs", "descripcion"])
complexity_data = pd.read_csv("Data-PCI.csv")

complexity_data = complexity_data[complexity_data["HS4 ID"].isin(data_slv.hs)].reset_index(drop = True)
complexity_data["HS4 ID"] = complexity_data["HS4 ID"].astype(str)

### Agrupados datos de comercio a HS 4 digitos
## Paises a investigar China, Vietnam, Camboya, Malasia, Indonesia
paises = ["CHN", "VNM", "KHM", "MYS", "IDN"]

df["tag"] = "" 
df.loc[df.partner_iso3_code.isin(paises), "tag"] = "paises_interes"
df.loc[~df.partner_iso3_code.isin(paises), "tag"] = "rest_of_world"

df["product_hs92_code_4d"] = df["product_hs92_code"].apply(lambda x : str(x)[:4])

df = df.groupby(["tag", "year", "product_hs92_code_4d"]).agg({"import_value" : "sum"}).reset_index()

df = df[df.product_hs92_code_4d.isin(complexity_data["HS4 ID"])]

df = df.dropna()

df["share_on_total_imports"] = df["import_value"]  / df.groupby(["product_hs92_code_4d", "year"])['import_value'].transform('sum')

### Agregamos PCI
complexity_data = complexity_data[['HS4 ID', 'HS4', '2020', '2021', '2022', '2023']]

df = df.merge(right=complexity_data, how="inner", right_on="HS4 ID", left_on="product_hs92_code_4d")
df.to_csv("INTENSIVO_paises_asia_hs_data.csv", index = False)
