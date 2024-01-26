import pandas as pd 
import os 

FILE_PATH = os.getcwd()
DATA_PATH = os.path.abspath(os.path.join(FILE_PATH, "..", "datos"))
OUTPUT_PATH = os.path.abspath(os.path.join(FILE_PATH, "..", "output"))

zm = pd.read_excel(os.path.join(DATA_PATH, "mpios_en_metropoli.xlsx"), sheet_name = "real")

zm = zm[~zm.duplicated(subset=["CVE_ZONA"])]

zm["CVE_ZONA"] = zm["CVE_ZONA"].apply(lambda x : x.replace(".",""))

zm.to_csv(os.path.join(OUTPUT_PATH, "zonas_metropolitanas_MEX.csv"), index = False)
