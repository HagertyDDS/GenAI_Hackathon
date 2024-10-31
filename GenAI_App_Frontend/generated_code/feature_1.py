

import pandas as pd

def clean_title_bool(DF: pd.DataFrame) -> pd.DataFrame:
    if 'clean_title' not in DF.columns:
        raise ValueError("DataFrame must contain 'clean_title' column")
    
    return DF[['clean_title']].apply(lambda x: x.str.strip().str.lower() == 'yes').astype(bool)
