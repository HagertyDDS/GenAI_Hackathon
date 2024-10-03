
import pandas as pd

def transform_clean_title(df, column_name):
    if not isinstance(df, pd.DataFrame) or column_name not in df.columns:
        raise ValueError('Invalid input')
    df[column_name] = df[column_name].apply(lambda x: 1 if x == 'yes' or x == 'true' else 0)
    return df

import re

def parse_engine(engine):
    horsepower = None
    displacement = None
    num_cylinders = None

    # Match the patterns for horsepower, displacement, and number of cylinders
    hp_match = re.search('(\d+\.?\d*)\s*HP', engine)
    disp_match = re.search('(\d+\.?\d*)\s*L', engine)
    cyl_match = re.search('(\d+)\s*Cylinder', engine)

    if hp_match:
        horsepower = float(hp_match.group(1))
    if disp_match:
        displacement = float(disp_match.group(1))
    if cyl_match:
        num_cylinders = int(cyl_match.group(1))

    return {
        'horsepower': horsepower,
        'displacement': displacement,
        'num_cylinders': num_cylinders
    }
