

import pandas as pd

def clean_title_bool(DF: pd.DataFrame) -> pd.DataFrame:
    if 'clean_title' not in DF.columns:
        raise ValueError("DataFrame must contain a 'clean_title' column")
    
    return DF['clean_title'].str.strip().str.lower().map({'yes': True, 'no': False}).fillna(False).astype(bool).to_frame(name='clean_title_bool')
