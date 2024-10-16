import pandas as pd
from postgres_load_data import get_car_sales_regression_data_from_postgres


DF = get_car_sales_regression_data_from_postgres()


#### Replace with the file you are importing Python functions from if different
import auto_generated_code as generated_functions
# List all function names in generated_functions.py
function_names = [func for func in dir(generated_functions) if callable(getattr(generated_functions, func))]


# Create an empty dictionary to hold the feature columns
feature_columns = {}

# Execute each function and store the result in the dictionary
for func_name in function_names:
    func = getattr(generated_functions, func_name)
    feature_result = func(DF)
    feature_columns.update(feature_result)



# Combine the feature columns into a single DataFrame
FeatureDF = pd.DataFrame(feature_columns)

print("Feature DF:")
print(FeatureDF.head(30))