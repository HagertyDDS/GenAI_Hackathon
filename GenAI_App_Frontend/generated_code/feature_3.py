

import pandas as pd
import numpy as np

def displacement(DF):
    def extract_displacement(engine_str):
        try:
            # Split the engine string and find the displacement value
            parts = engine_str.split()
            for part in parts:
                if 'L' in part:
                    return float(part.replace('L', ''))  # Return the numeric value of displacement
            return np.nan  # Return NaN if no displacement found
        except Exception:
            return np.nan  # Return NaN in case of any error

    # Apply the extraction function to the engine column
    displacement_values = DF['engine'].apply(extract_displacement)
    
    # Return as a DataFrame
    return pd.DataFrame(displacement_values, columns=['displacement'])
