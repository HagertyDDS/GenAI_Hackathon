

import pandas as pd

def american_brand(DF):
    american_brands = {'Ford', 'Chevrolet', 'GMC', 'Cadillac', 'Buick', 'Chrysler', 'Dodge', 'Jeep', 'Lincoln', 'Ram', 'Tesla', 'Pontiac', 'Oldsmobile', 'Saturn', 'Mercury', 'Hummer', 'Plymouth', 'Packard', 'Studebaker'}
    DF['is_american'] = DF['brand'].apply(lambda x: 1 if x in american_brands else 0)
    return DF[['is_american']]
