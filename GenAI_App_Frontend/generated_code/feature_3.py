

import pandas as pd
import numpy as np

def displacement(DF):
    def extract_displacement(engine_str):
        if pd.isna(engine_str):
            return np.nan
        parts = engine_str.split()
        for part in parts:
            if 'L' in part:
                return part.replace('L', '')
        return np.nan

    DF['displacement'] = DF['engine'].apply(extract_displacement)
    return DF[['displacement']]
