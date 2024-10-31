

import pandas as pd

def mileage_over_10000(DF: pd.DataFrame) -> pd.DataFrame:
    if 'milage' not in DF.columns:
        raise ValueError("DataFrame must contain a 'milage' column")
    
    return pd.DataFrame(DF['milage'] > 10000)
