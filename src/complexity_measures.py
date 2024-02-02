import numpy as np
import pandas as pd 
import itertools
from typing import Union

def build_Mcp(pair_array : np.array, 
              all_activities : Union[list, np.array])-> pd.DataFrame:
    
    adj_mat = pd.crosstab(pair_array[:,0],pair_array[:,1])
    
    complete_adj_mat = pd.concat([
        pd.DataFrame(columns=all_activities),
        adj_mat
    ])

    return complete_adj_mat
    
def metrics_diversity_ubiquity(pair_array : np.array, 
                               all_activities : Union[list, np.array], 
                               metric : str)-> dict:
    """
    Recibe un arreglo de numpy 2D donde correspondiente a pares (lugar,producto-sector).

    Regresa un diccionario donde las llaves son los países y los valores el valor de diversity (suma sobre filas de la matriz Mcp) 
    Argumentos de la Function
    ------------------
    - pair_array: arreglo 2D de numpy

    ArgumentosKeyword 
    -----------------
    """

    Mcp = build_Mcp(pair_array, all_activities)

    match metric:
        case "diversity":
            return dict(Mcp.sum(axis=1))
        case "ubiquity":
            return dict(Mcp.sum(axis=0))
    
    #return 

def RCA(df : pd.DataFrame, 
        value_col_name : str, 
        activiy_col_name : str, 
        place_col_name : str,
        place : str, 
        sum_cp_X_cp, 
        sum_c_X_cp):
    """
    Recibe un arreglo de numpy 2D donde correspondiente a pares (lugar,producto-sector).

    Regresa un diccionario donde las llaves son los productos-sectores y los valores el valor de ubiquity(suma sobre columnas de la matriz Mcp) 
    Argumentos de la Function
    ------------------
    - pair_array: arreglo 2D de numpy

    ArgumentosKeyword 
    ---------
    """
    
    X_cp = df.query(f"{place_col_name}=='{place}'")[[activiy_col_name, value_col_name]].set_index(activiy_col_name)
    sum_p_X_cp = X_cp[value_col_name].sum()

    df_RCA = ((X_cp/sum_p_X_cp)/(sum_c_X_cp/sum_cp_X_cp)).reset_index()
    df_RCA["place"] = place

    return df_RCA

def proximity(Mcp_df : pd.DataFrame, col_names : list) -> pd.DataFrame:
    salidas = []
    for par in itertools.product(Mcp_df.columns, Mcp_df.columns):
        prodA, prodB = Mcp_df[par[0]].to_numpy(), Mcp_df[par[1]].to_numpy()
    
        condicional = sum(prodA*prodB)
    
        salidas.append((par[0], par[1],condicional/max(sum(prodA),sum(prodB))))
        
    #return pd.DataFrame(salidas, columns = ["prodA", "prodB", "proximity"])    
    return pd.DataFrame(salidas, columns = col_names)

def distance(place : str, activity : str, Mcp_df : pd.DataFrame, proximity_df : pd.DataFrame) -> pd.DataFrame:
    return (1 - Mcp_df.loc[place]).to_numpy() @ proximity_df[activity].to_numpy()/sum(proximity_df[activity])


def density(place : str, activity : str, Mcp_df : pd.DataFrame, proximity_df : pd.DataFrame) -> pd.DataFrame:
    try:
        return Mcp_df.loc[place].to_numpy() @ proximity_df[activity].to_numpy()/sum(proximity_df[activity])
    except:
        return 0.0
        
def IO_similarity(place : str, activity : str, Mcp_df : pd.DataFrame, proximity_df : pd.DataFrame, tipo : str) -> pd.DataFrame:
    match tipo:
        case "input_similarity":
            try:
                return Mcp_df.loc[place].to_numpy() @ proximity_df[activity].to_numpy()/sum(proximity_df[activity])
            except:
                return 0.0
        case "output_similarity":
            try:
                return Mcp_df.loc[place].to_numpy() @ proximity_df.loc[activity].to_numpy()/sum(proximity_df.loc[activity])
            except:
                return 0.0

        

