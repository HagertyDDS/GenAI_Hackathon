

import pandas as pd

def transform_clean_title_to_boolean(DF):
    """
    This function takes a dataframe and transforms the 'clean_title' column into a boolean.
    """
    # Check if 'clean_title' column exists in the dataframe
    if 'clean_title' not in DF.columns:
        raise ValueError("'clean_title' column not found in the dataframe.")
    
    # Transform 'clean_title' column to boolean
    DF['clean_title'] = DF['clean_title'].map({'yes': True, 'no': False})
    
    # Handle edge cases where 'clean_title' is neither 'yes' nor 'no'
    DF['clean_title'].fillna(False, inplace=True)
    
    return pd.DataFrame(DF['clean_title'])


import pandas as pd
import numpy as np

def extract_engine_specs(DF):
    def parse_engine(engine):
        try:
            horsepower = float(engine.split('HP')[0].strip())
            displacement = float(engine.split('HP')[1].split('L')[0].strip())
            num_cylinders = int(engine.split('Cylinder')[0].split()[-1])
            return pd.Series([horsepower, displacement, num_cylinders])
        except:
            return pd.Series([np.nan, np.nan, np.nan])
    
    DF[['horsepower', 'displacement', 'num_cylinders']] = DF['engine'].apply(parse_engine)
    return DF[['horsepower', 'displacement', 'num_cylinders']]
