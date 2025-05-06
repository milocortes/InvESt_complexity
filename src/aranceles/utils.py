from dataclasses import dataclass
from typing import List
import pandas as pd 

@dataclass
class HSA:
    product_id : int
    product_hs92_code : str
    product_level : int
    product_name : str
    product_name_short : str
    product_parent_id : float
    product_id_hierarchy : str
    show_feasibility : bool
    natural_resource : bool
    green_product : str

class HSAData:

    def __init__(self, df_hsa : pd) -> None:
        self.hsa_list : List[HSA] = self.get_hsa_data(df_hsa)

    def get_hsa_data(self, df_hsa : pd) -> List[HSA]:
        return [HSA(*data) for data in df_hsa.to_records(index=False)]


    def get_data_from_hs92_code(self, code : str) -> HSA:
        for hsa in self.hsa_list:
            if hsa.product_hs92_code==code:
                return hsa

    def get_data_from_product_parent_id(self, product_id : int) -> HSA:
        for hsa in self.hsa_list:
            if hsa.product_id==product_id:
                return hsa

    def build_record(self, code : str) -> List:
        hsa_4d = self.get_data_from_hs92_code(code)
        hsa_2d = self.get_data_from_product_parent_id(hsa_4d.product_parent_id)
        hsa_1d = self.get_data_from_product_parent_id(hsa_2d.product_parent_id)

        data = [
            hsa_4d.product_hs92_code,
            hsa_4d.product_name_short,
            hsa_2d.product_hs92_code,
            hsa_2d.product_name_short,           
            hsa_1d.product_hs92_code,
            hsa_1d.product_name_short,            
        ]

        return data

    def build_correspondence(self) -> pd.DataFrame:
        data = []
        for hs in self.hsa_list:
            if len(hs.product_hs92_code)==4:
                data.append(
                    self.build_record(hs.product_hs92_code)
                )

        return pd.DataFrame(data, columns = ["product_hs92_code_4d", "product_hs92_name_4d", "product_hs92_code_2d", "product_hs92_name_2d", "product_hs92_code_1d", "product_hs92_name_1d"])
