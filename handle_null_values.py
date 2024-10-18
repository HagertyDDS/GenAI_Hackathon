import pandas as pd
import psycopg2
from sqlalchemy import create_engine
import numpy as np

# PostgreSQL connection details
def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="template1",
        user="postgres",
        password="postgres123"
    )

# Load table names from PostgreSQL
def load_table_names():
    conn = get_connection()
    query = "SELECT table_name FROM information_schema.tables WHERE table_schema='public';"
    df = pd.read_sql(query, conn)
    conn.close()
    return df['table_name'].tolist()

# Load the data from the selected table
def load_table_data(table_name):
    conn = get_connection()
    query = f"SELECT * FROM {table_name};"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# null imputation function
def handle_null_imputation(df, imputation_choices):
    for column, (method, custom_value) in imputation_choices.items():
        if method == 'Mean':
            df[column].fillna(df[column].mean(), inplace=True)
        elif method == 'Median':
            df[column].fillna(df[column].median(), inplace=True)
        elif method == 'Mode':
            df[column].fillna(df[column].mode()[0], inplace=True)
        elif method == 'Custom':
            df[column].fillna(custom_value, inplace=True)
    return df

# Function to determine which imputation methods to show based on column type
def get_imputation_methods_for_column(column_dtype):
    if pd.api.types.is_numeric_dtype(column_dtype):
        # Show Mean, Median, Mode, and Custom for numeric columns
        return ['None', 'Mean', 'Median', 'Mode', 'Custom Value']
    elif pd.api.types.is_categorical_dtype(column_dtype) or pd.api.types.is_object_dtype(column_dtype):
        # Show only Mode and Custom for categorical columns
        return ['None', 'Mode', 'Custom Value']
    else:
        # Only allow Custom for other types
        return ['None', 'Custom Value']

if __name__ == "__main__":
    print("Loading table names...")
    table_names = load_table_names()
    print("Available tables:")
    for i, table in enumerate(table_names, start=1):
        print(f"{i}. {table}")

    # User selects a table
    table_choice = int(input("Select a table by entering the corresponding number: ")) - 1
    table_name = table_names[table_choice]
    print(f"Loading data from '{table_name}'...")

    # Load the data
    df = load_table_data(table_name)
    print(f"Columns in '{table_name}':")
    print(df.columns)

    df = df.replace('nan', np.nan)

    # Check for missing values
    if df.isnull().sum().sum() == 0:
        print("No missing values found in the table.")
        print(len(df))
    else:
        print(f"Columns in '{table_name}':")
        print(df.columns)

    # Dictionary to store imputation choices
    imputation_methods = ['None', 'Mean', 'Median', 'Mode', 'Custom Value']  #Option to look at the column and come up with Chris
    imputation_choices = {}

    # Iterate through columns to handle null values
    for column in df.columns:
        if df[column].isnull().sum() > 0:
            print(f"Column '{column}' has {df[column].isnull().sum()} missing values.")
            # Get valid imputation methods for this column's data type
            column_dtype = df[column].dtype
            valid_methods = get_imputation_methods_for_column(column_dtype)
            print(f"Choose an imputation method for column '{column}' (type: {column_dtype}):")
            for i, method in enumerate(valid_methods, start=1):
                print(f"{i}. {method}")

            # User chooses an imputation method
            choice = int(input(f"Select imputation method for '{column}': ")) - 1
            method = valid_methods[choice]

            # Handle custom value imputation
            if method == 'Custom Value':
                custom_value = input(f"Enter the custom value to impute for '{column}': ")
                imputation_choices[column] = ('Custom', custom_value)
            elif method == 'None':
                continue
            else:
                imputation_choices[column] = (method, None)

    # Perform the imputation
    print("Performing null value imputation...")
    imputed_df = handle_null_imputation(df, imputation_choices)
    print("Imputation Complete...")
    print("Imputed Data:")
    print(imputed_df.head())


