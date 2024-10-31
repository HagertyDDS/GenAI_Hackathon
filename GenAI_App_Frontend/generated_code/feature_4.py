

import pandas as pd
import numpy as np

def num_cylinders(DF):
    def extract_cylinders(engine_str):
        if pd.isna(engine_str):
            return np.nan
        if 'Cylinder' in engine_str:
            parts = engine_str.split()
            for part in parts:
                if part.isdigit():
                    return int(part)
        return np.nan

    return DF['engine'].apply(extract_cylinders).to_frame(name='num_cylinders')
