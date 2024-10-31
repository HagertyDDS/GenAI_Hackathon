

import pandas as pd

def american_brand(DF):
    american_brands = {'Ford', 'Chevrolet', 'Lincoln', 'GMC', 'Cadillac', 'Dodge', 'Chrysler', 'Jeep', 'Ram', 'Buick', 'Tesla', 'Pontiac', 'Oldsmobile', 'Saturn', 'Mercury', 'Hummer', 'Plymouth'}
    DF['is_american'] = DF['brand'].apply(lambda x: 1 if x in american_brands else 0)
    return DF[['is_american']]
