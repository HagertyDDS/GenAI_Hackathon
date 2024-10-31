

import pandas as pd
import numpy as np

def horsepower(DF):
    DF['horsepower'] = DF['engine'].str.extract(r'(\d+\.?\d*)HP')[0]
    DF['horsepower'] = pd.to_numeric(DF['horsepower'], errors='coerce')
    return DF[['horsepower']]
