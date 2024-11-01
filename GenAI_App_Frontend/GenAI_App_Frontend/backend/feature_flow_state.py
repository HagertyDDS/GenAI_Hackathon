
import reflex as rx
from typing import Union, List
import csv
import pandas as pd
from flaml import AutoML
from pprint import pprint
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    mean_squared_error, accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, 
    r2_score, mean_absolute_error, mean_absolute_percentage_error
)
import importlib.util
import os
import joblib
import random
import concurrent.futures
import time
import sys
import re
from typing import Any
# Backend imports 

from .feature_code_gen import CODE_GEN_CHAIN
from .feature_code_gen_v2 import CODE_GEN_CHAIN_V2
from .feature_code_gen_v3 import CODE_GEN_CHAIN_V3

from databricks import sql

import re
from dotenv import load_dotenv

load_dotenv()
DATABRICKS_TOKEN = os.environ.get("DATABRICKS_TOKEN")

MAX_RETRIES = 3





def split_column_metadata(column_metadata):
    """
    Splits column metadata into two dictionaries: one for data types and another for descriptions.

    Parameters:
        column_metadata (list of tuples): List containing tuples of column metadata.
                                          Each tuple should be (column_name, data_type, comment).

    Returns:
        tuple: A tuple containing two dictionaries:
               - data_types_dict: Dictionary with column names as keys and data types as values.
               - descriptions_dict: Dictionary with column names as keys and descriptions as values.
    """
    data_types_dict = {}
    descriptions_dict = {}
    
    for column_name, data_type, comment in column_metadata:
        data_types_dict[column_name] = data_type
        descriptions_dict[column_name] = comment if comment else "No comment provided."

    return data_types_dict, descriptions_dict






def column_metadata_to_dict(column_metadata):
    """
    Converts column metadata into a dictionary with column names as keys
    and a string of data type and description as values.

    Parameters:
        column_metadata (list of tuples): List containing tuples of column metadata.
                                          Each tuple should be (column_name, data_type, comment).

    Returns:
        dict: A dictionary where each key is a column name and each value is a formatted string
              with data type and description.
    """
    metadata_dict = {}
    for column_name, data_type, comment in column_metadata:
        # Format data type and description into a single string
        metadata_dict[column_name] = f"Data Type: {data_type}, Description: {comment if comment else 'No comment provided.'}"
    
    return metadata_dict


def column_metadata_to_nested_dict(column_metadata):
    """
    Converts column metadata into a nested dictionary with column names as top-level keys
    and data type and description as keys in a nested dictionary.

    Parameters:
        column_metadata (list of tuples): List containing tuples of column metadata.
                                          Each tuple should be (column_name, data_type, comment).

    Returns:
        dict: A nested dictionary where each key is a column name, and the value is a dictionary
              with 'data_type' and 'description' keys.
    """
    metadata_dict = {}
    for column_name, data_type, comment in column_metadata:
        # Nest data type and description within each column name key
        metadata_dict[column_name] = {
            "data_type": data_type,
            "description": comment if comment else "No comment provided."
        }
    
    return metadata_dict





def format_column_metadata_for_llm(column_metadata):
    """
    Formats column metadata into a string suitable for LLM input.

    Parameters:
        column_metadata (list of tuples): List containing tuples of column metadata.
                                          Each tuple should be (column_name, data_type, comment).

    Returns:
        str: A formatted string describing the columns, types, and comments.
    """
    metadata_description = "Table Schema:\n\n"
    for column_name, data_type, comment in column_metadata:
        # Add description for each column
        metadata_description += f"Column Name: {column_name}\n"
        metadata_description += f"Data Type: {data_type}\n"
        metadata_description += f"Description: {comment if comment else 'No comment provided.'}\n"
        metadata_description += "-" * 50 + "\n"  # Separator line for readability

    return metadata_description


def df_to_list_of_lists(df: pd.DataFrame) -> list[list]:
    """
    Converts a DataFrame into a list of lists, where each inner list represents a row.
    """
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            df[col] = df[col].fillna(0)  # or another placeholder for numeric columns
        else:
            df[col] = df[col].fillna("")  # or any placeholder for non-numeric columns


    return df.values.tolist()

def get_df_columns_spec(df: pd.DataFrame) -> list[dict[str, str]]:
    """
    Converts DataFrame columns into a list of dictionaries with title and type for each column.
    """
    column_list = []
    for col in df.columns:
        col_type = str(df[col].dtype)
        if "int" in col_type:
            dtype = "int"
        elif "float" in col_type:
            dtype = "float"
        elif "bool" in col_type:
            dtype = "bool"
        else:
            dtype = "str"
        
        column_list.append({
            "title": col,
            "type": dtype
        })
    return column_list





def extract_code_from_content_v2(output):
    """
    Extracts code from a content string that may include markdown code fences.

    Parameters:
        content (str): The content string containing code within markdown code fences.

    Returns:
        str: The extracted code without the markdown code fences.
    """
    content = output.content
    # Use regular expressions to remove code fences
    code = content.strip()

    # Remove triple backticks and optional language specifier (e.g., ```python)
    code = re.sub(r'^```(?:python)?\n', '', code)
    code = re.sub(r'\n```$', '', code)

    return code.strip()


def extract_code_from_content_v3(output: str) -> str:
    """
    Extracts Python code from the output content between ```python and ```.
    
    Parameters:
        output (str): The output content containing the generated Python code.
    
    Returns:
        str: The extracted Python code as a string.
    """
    # Use regex to match code between ```python and ```
    match = re.search(r"```python\n(.*?)\n```", output, re.DOTALL)
    if match:
        code = match.group(1)
        return code.strip()  # Remove any leading/trailing whitespace
    else:
        print("No code block found in the output.")
        return ""



def read_file_to_string(file_path):
    """
    Reads the contents of a text file and returns it as a single string.
    
    Parameters:
        file_path (str): The path to the text file.

    Returns:
        str: The content of the file as a single string.
    """
    try:
        with open(file_path, 'r') as file:
            content = file.read()
        return content
    except FileNotFoundError:
        return "File not found."
    except IOError:
        return "An error occurred while reading the file."

# Example usage
# content = read_file_to_string('your_file.txt')
# print(content)


def df_sampler(df):
    # Select the first 10 rows
    subset = df.head(10)
    
    # Convert each row to a string format for easier interpretation by a language model
    rows = []
    for _, row in subset.iterrows():
        # Convert row to a dictionary and format it as a string
        row_str = "{ " + ", ".join(f"{col}: {repr(val)}" for col, val in row.items()) + " }"
        rows.append(row_str)
    
    # Join each row with a newline for readability
    return "\n".join(rows)


def load_all_functions(file_path: str = "auto_generated_functions.py"):
    print("Starting load all functions...")
    """Dynamically load all functions from the saved Python file."""
    spec = importlib.util.spec_from_file_location("auto_generated_functions", file_path)
    generated_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(generated_module)
    
    # Retrieve all functions defined in the module
    functions = [getattr(generated_module, func) for func in dir(generated_module) if callable(getattr(generated_module, func))]
    
    print("\n LOAD_ALL_FUNCTIONS, FUNCTION: ")
    print(functions)

    return functions



def execute_functions_on_df(functions, df: pd.DataFrame, target_var: str):
    print("\n EXECUTE_FUNCTIONS_ON_DF...")
    print("Function:", functions)

    """Execute all functions on the dataframe and combine the results."""
    combined_df = pd.DataFrame()

    # Extract and remove the target variable column
    target_column = df[target_var]
    df = df.drop(columns=[target_var])

    for func in functions:
        print(f"Executing function: {func.__name__}")
        result = func(df)  # Each function is expected to return a single-column dataframe
        combined_df = pd.concat([combined_df, result], axis=1)  # Combine each column

    # Concatenate the target variable back to the end of the combined DataFrame
    combined_df = pd.concat([combined_df, target_column], axis=1)

    return combined_df




def remove_duplicate_columns(df, combined_results):
    duplicate_columns = combined_results.columns.intersection(df.columns)
    if not duplicate_columns.empty:
        print(f"Removing duplicate columns from combined_results: {duplicate_columns.tolist()}")
        combined_results = combined_results.drop(columns=duplicate_columns)
    return combined_results



# null imputation function
def handle_null_imputation(df, imputation_choices):
    for column, method in imputation_choices.items():
        if method == 'Mean':

            df[column].fillna(df[column].mean(), inplace=True)
        elif method == 'Median':
            df[column].fillna(df[column].median(), inplace=True)
        elif method == 'Mode':
            df[column].fillna(df[column].mode()[0], inplace=True)
        # elif method == 'Custom':
        #     df[column].fillna(custom_value, inplace=True)
            

    return df


def train_and_compare_automl(base_df: pd.DataFrame, revised_df: pd.DataFrame, problem_type: str, target: str, training_framework: str):
    """
    Trains and compares two machine learning models (base dataset vs revised dataset) using FLAML AutoML.
    
    Parameters:
        base_df (pd.DataFrame): The base dataset for training the first model.
        revised_df (pd.DataFrame): The revised dataset for training the second model.
        problem_type (str): Type of ML problem ('classification' or 'regression').
        target (str): The name of the target column in both datasets.
        training_framework (str): The ML framework to prioritize (e.g., 'xgboost', 'lightgbm', 'rf').
        
    Returns:
        dict: A dictionary containing evaluation metrics for both models.
    """
    
    def prepare_data(df, target):
        """Helper function to split the dataset into features (X) and target (y)."""
        X = df.drop(columns=[target])
        y = df[target]


        # # Ensure y is a Series
        # if isinstance(y, pd.DataFrame):
        #     y = y.squeeze()  # Convert single-column DataFrame to Series

        # # Convert categorical columns in X to one-hot encoded numeric columns
        # X = pd.get_dummies(X, drop_first=True)  # One-hot encode and drop the first category to avoid multicollinearity


        print("X shape:", X.shape)
        print("y shape:", y.shape)

        # print("X columns:", X.columns.tolist())
        # print("y columns:", y.columns.tolist() if isinstance(y, pd.DataFrame) else y.name)

        print("X head:", X.head(10))
        print("y head:", y.head(10))

        print(type(X))
        print(type(y))

        return X, y
    
    def train_automl(X_train, y_train, X_test, y_test, problem_type, training_framework):
        """Helper function to train a model using FLAML AutoML."""
        automl = AutoML()
        automl_settings = {
            "task": problem_type,  # Either 'classification' or 'regression'
            "metric": "accuracy" if problem_type == "classification" else "rmse",
            "time_budget": 60,  # Allow up to 60 seconds for each model
            "estimator_list": [training_framework],  # Set the training framework (XGBoost, LightGBM, etc.)
            "verbose": 0,  # Suppress detailed output
        }
        automl.fit(X_train=X_train, y_train=y_train, X_val=X_test, y_val=y_test, **automl_settings)
        return automl
    
    # Print the columns of both datasets
    print("Base Dataset Columns:")
    print(base_df.columns.tolist())
    
    print("Revised Dataset Columns:")
    print(revised_df.columns.tolist())
    
    # Prepare datasets for training
    X_base, y_base = prepare_data(base_df, target)
    X_revised, y_revised = prepare_data(revised_df, target)
    
    # Split the datasets into train/test sets
    X_base_train, X_base_test, y_base_train, y_base_test = train_test_split(X_base, y_base, test_size=0.2, random_state=42)
    X_revised_train, X_revised_test, y_revised_train, y_revised_test = train_test_split(X_revised, y_revised, test_size=0.2, random_state=42)
    
    # Train models on both datasets
    print(f"Training model on the base dataset with {training_framework}...")
    base_automl = train_automl(X_base_train, y_base_train, X_base_test, y_base_test, problem_type, training_framework)
    
    print(f"Training model on the revised dataset with {training_framework}...")
    revised_automl = train_automl(X_revised_train, y_revised_train, X_revised_test, y_revised_test, problem_type, training_framework)
    
    # Save models to files
    joblib.dump(base_automl, "models/base_model.pkl")
    joblib.dump(revised_automl, "models/revised_model.pkl")
    print("Models saved as 'base_model.pkl' and 'revised_model.pkl'.")

    # Predict and evaluate the models
    if problem_type == "classification":
        y_base_pred = base_automl.predict(X_base_test)
        y_revised_pred = revised_automl.predict(X_revised_test)
        
        base_metrics = {
            "accuracy": accuracy_score(y_base_test, y_base_pred),
            "precision": precision_score(y_base_test, y_base_pred, average='weighted'),
            "recall": recall_score(y_base_test, y_base_pred, average='weighted'),
            "f1_score": f1_score(y_base_test, y_base_pred, average='weighted'),
            "confusion_matrix": confusion_matrix(y_base_test, y_base_pred).tolist(),
        }
        
        revised_metrics = {
            "accuracy": accuracy_score(y_revised_test, y_revised_pred),
            "precision": precision_score(y_revised_test, y_revised_pred, average='weighted'),
            "recall": recall_score(y_revised_test, y_revised_pred, average='weighted'),
            "f1_score": f1_score(y_revised_test, y_revised_pred, average='weighted'),
            "confusion_matrix": confusion_matrix(y_revised_test, y_revised_pred).tolist(),
        }
        
        metrics = {
            "base_model_metrics": base_metrics,
            "revised_model_metrics": revised_metrics,
        }

    elif problem_type == "regression":
        y_base_pred = base_automl.predict(X_base_test)
        y_revised_pred = revised_automl.predict(X_revised_test)
        
        base_metrics = {
            "rmse": mean_squared_error(y_base_test, y_base_pred, squared=False),
            "mae": mean_absolute_error(y_base_test, y_base_pred),
            "r2": r2_score(y_base_test, y_base_pred),
            "mape": mean_absolute_percentage_error(y_base_test, y_base_pred),
        }
        
        revised_metrics = {
            "rmse": mean_squared_error(y_revised_test, y_revised_pred, squared=False),
            "mae": mean_absolute_error(y_revised_test, y_revised_pred),
            "r2": r2_score(y_revised_test, y_revised_pred),
            "mape": mean_absolute_percentage_error(y_revised_test, y_revised_pred),
        }
        
        metrics = {
            "base_model_metrics": base_metrics,
            "revised_model_metrics": revised_metrics,
        }
    
    # Print results
    print("Base Model Metrics:", base_metrics)
    print("Revised Model Metrics:", revised_metrics)
    
    return metrics


def clean_json_output(output: str) -> str:
    """Clean the model's output to ensure it's valid JSON."""
    try:
        # Find where the JSON begins
        start = output.find("{")
        # Find where the JSON ends
        end = output.rfind("}") + 1
        # Extract only the valid JSON
        cleaned_output = output[start:end]
        return cleaned_output
    except Exception as e:
        print(f"Error cleaning output: {e}")
        return output 





# New Resiliant Process Funcs ---------------------------------------------
    



# def execute_single_function(func, df: pd.DataFrame):
#     """Attempt to execute a single function on the DataFrame."""
#     try:
#         print(f"Executing function: {func.__name__}")
#         result = func(df)  # Expected to return a single-column dataframe
#         return result
#     except Exception as e:
#         print(f"Error executing function {func.__name__}: {e}")
#         return None

def execute_single_function(func, df: pd.DataFrame):
    """Attempt to execute a single function on the DataFrame."""
    try:
        print(f"Executing function: {func.__name__}")
        result = func(df)  # Expected to return a single-column dataframe
        
        # Check for null percentage in the result
        null_percentage = result.isnull().mean().iloc[0] * 100  # Calculate % of nulls in the column
        print(f"Null percentage for {func.__name__}: {null_percentage:.2f}%")
        
        if null_percentage > 80:
            print(f"Function {func.__name__} returned over 80% null values. Discarding result.")
            return None

        return result
    except Exception as e:
        print(f"Error executing function {func.__name__}: {e}")
        return None


# def load_single_function(file_path: str, function_name: str):
#     """Load a specific function from the saved Python file."""
#     spec = importlib.util.spec_from_file_location("auto_generated_functions", file_path)
#     generated_module = importlib.util.module_from_spec(spec)
#     spec.loader.exec_module(generated_module)
#     return getattr(generated_module, function_name, None)

# def save_generated_code(code: str, file_path: str = "auto_generated_functions.py"):
#     """Clear previous contents and save new generated code to a Python file."""
#     if os.path.exists(file_path):
#         open(file_path, "w").close()  # Clear file contents
#     with open(file_path, "a") as f:
#         f.write(f"\n\n{code}\n")
#     print(f"Generated code saved to {file_path}")
    

def save_generated_code(code: str, file_path: str):
    """Clear previous contents and save new generated code to a specified Python file path."""
    # Ensure the directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Clear contents if the file already exists
    if os.path.exists(file_path):
        open(file_path, "w").close()
    
    # Write the new code to the specified file
    with open(file_path, "a") as f:
        f.write(f"\n\n{code}\n")
    print(f"Generated code saved to {file_path}")



def load_single_function(file_path: str, function_name: str):
    """Load a specific function from the specified Python file using a unique module name."""
    module_name = f"generated_module_{os.path.basename(file_path).replace('.py', '')}"

    # Remove the module from sys.modules if it was previously loaded
    if module_name in sys.modules:
        del sys.modules[module_name]
    
    # Load the module dynamically from the file path
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    generated_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(generated_module)

    # Return the requested function or None if not found
    return getattr(generated_module, function_name, None)



# ---------------------------------------------


class FeatureV2(rx.Base):
    """The Feature object."""

    id: int
    name: str = ""
    description: str = ""

    code: str = ""
    


class Feature(rx.Base):
    """The Feature object."""

    id: int
    feature_name: str
    description: str
    


class FeatureFlowState(rx.State):
    """The state class."""


    # Datasets 
    base_dataset: pd.DataFrame = None 
    final_dataset: pd.DataFrame = None 

    # Column lists 
    base_dataset_cols: List[str] = []
    final_dataset_cols: List[str] = []

    # Imputation Choices 
    base_imputation_choices: dict = {}
    final_imputation_choices: dict = {}

    # All Docs obj 
    all_docs: pd.DataFrame

    # Features
    features: List[Feature] = []

    # LLM Options 
    llm_to_use: str = "gpt-4o-mini"

    # ML Options 
    ml_problem_type: str 
    target_var: str 
    evaluation_metric: str 
    training_framework: str

    # Auto Eval 
    auto_ml_metrics_dic: dict = {}
    base_model_metrics_dic: dict = {}
    revised_model_metrics_dic: dict = {}


    # Databricks Connection 
    server_hostname: str 
    http_path: str
    catalog: str 
    schema: str 
    db_table: str
    db_table_comments: str
    db_table_comments_dict: dict 
    db_table_data_type_dict: dict 
    db_table_descriptions_dict: dict


    # New Feature System
    features_v2: List[FeatureV2] = []

    # Combined results df for null handling 
    combined_results: pd.DataFrame = None


    # Regression Metrics
    rmse: float = 0.0
    mae: float = 0.0
    mape: float = 0.0
    r2: float = 0.0



    # --------------------------------------------
    # In testing code 

    def create_new_feature(self):
        # Find the highest id in the features_v2 list
        if self.features_v2:
            max_id = max(feature.id for feature in self.features_v2)
        else:
            max_id = 0  # If the list is empty, start with ID 1
        
        # Set new feature ID as max_id + 1
        new_id = max_id + 1
        new_code = f"print('Hello, world! {new_id}')"

        # Create a new FeatureV2 instance with the new ID
        #new_feature = FeatureV2(id=new_id, code=new_code)

        new_feature = FeatureV2(id=new_id)


        # Add the new feature to the list
        self.features_v2.append(new_feature)

        # Return the new feature's data as a dictionary
        return new_feature.__dict__


    def remove_feature_by_id(self, feature_id) -> bool:
        # Look for the feature with the given ID
        for feature in self.features_v2:
            if feature.id == feature_id:
                # Remove the feature from the list
                self.features_v2.remove(feature)
                return True
        
        # If the feature was not found
        return False
    
    def save_feature_by_id(self, feature_id, feature_name, feature_description):
        # Look for the feature with the given ID
        print("save_feature_by_id running...")

        for feature in self.features_v2:
            if feature.id == feature_id:
                # Set the name and description
                feature.name = feature_name
                feature.description = feature_description
                break
            
        
        for feature in self.features_v2:
            print(feature.name)
            print(feature.description)
            print(feature.code)
            print("\n")

        # If the feature was not found
        return 
    
    def save_feature_code(self, id: int, code: str) -> bool:
        """Finds the feature by id and updates its code."""
        # Iterate over the features to find the one with the matching id
        for feature in self.features_v2:
            if feature.id == id:
                feature.code = code
                print(f"Feature with ID {id} updated with code.")
                return True
        print(f"No feature found with ID {id}.")
        return False

    def remove_all_features_v2(self): 
        self.features_v2 = []

    # --------------------------------------------
    @rx.var
    def get_ml_eval_met(self) -> str:
        if self.ml_problem_type == 'classification': 
            return 'accuracy'
        elif self.ml_problem_type == 'regression':
            return 'r2'


    def set_ml_problem_type(self, val: str): 
        self.ml_problem_type = val

        if self.ml_problem_type == 'classification': 
            self.evaluation_metric = 'accuracy'
        elif self.ml_problem_type == 'regression':
            self.evaluation_metric = 'r2'


        print("self.evaluation_metric set as:", self.evaluation_metric)

    def set_target_var(self, val: str): 
        self.target_var = val

    def set_evaluation_metric(self, val: str): 
        self.evaluation_metric = val

    def set_training_framework(self, val: str):
        self.training_framework = val


    async def set_base_dataset(self, path: str) -> bool: 
        print("set_base_dataset path:", path)
        self.base_dataset = pd.read_csv(path)

        return True 
    
    async def set_base_dataset_from_databricks(self, table) -> bool: 

        self.db_table = table

        connection = sql.connect(
            server_hostname=self.server_hostname,
            http_path=self.http_path,
            access_token=DATABRICKS_TOKEN
        )

        # Query to get data and convert to pandas DataFrame

        sql_query = f"SELECT * FROM {self.catalog}.{self.schema}.{table}"

        with connection.cursor() as cursor:
            cursor.execute(sql_query)
            columns = [desc[0] for desc in cursor.description]  # Get column names
            result = cursor.fetchall()

        # Convert to DataFrame
        train_df = pd.DataFrame(result, columns=columns)
        self.base_dataset = train_df




        # Query to get column names, data types, and comments
        query_columns = f"""
        SELECT column_name, data_type, comment
        FROM {self.catalog}.information_schema.columns
        WHERE table_schema = '{self.schema}' AND table_name = '{table}'
        """

        # Execute the query to get column metadata
        column_metadata = []
        with connection.cursor() as cursor:
            cursor.execute(query_columns)
            column_metadata = cursor.fetchall()  # Fetch all metadata at once

        self.db_table_comments = format_column_metadata_for_llm(column_metadata)
        self.db_table_comments_dict = column_metadata_to_dict(column_metadata)

        data_types_dict, descriptions_dict = split_column_metadata(column_metadata)
        self.db_table_data_type_dict = data_types_dict
        self.db_table_descriptions_dict = descriptions_dict


        # Close the connection
        connection.close()

        return True
    
    def get_table_options_from_databricks(self) -> list[str]:

        connection = sql.connect(
            server_hostname=self.server_hostname,
            http_path=self.http_path,
            access_token=DATABRICKS_TOKEN
        )

        query = f"""
        SELECT table_name 
        FROM {self.catalog}.information_schema.tables
        WHERE table_schema = '{self.schema}'
        """

        tables: list[str] = ['Failed to find tables...']

        # Execute the query and fetch table names
        with connection.cursor() as cursor:
            cursor.execute(query)
            tables = cursor.fetchall()

        connection.close()
    
        return tables

    @rx.var 
    def base_dataset_set(self) -> bool:
        return self.base_dataset is not None
    
    @rx.var 
    def final_dataset_set(self) -> bool:
        return self.final_dataset is not None



    async def base_dataset_col_spec(self) -> list[Any]: 
        if self.base_dataset is not None: 
            return get_df_columns_spec(self.base_dataset)
        return []
    
    
    async def base_dataset_list_list(self) -> list[list[Any]]: 
        if self.base_dataset is not None: 
            return df_to_list_of_lists(self.base_dataset.head(50))
        return []

    
    async def final_dataset_col_spec(self) -> list[Any]: 
        if self.final_dataset is not None: 
            return get_df_columns_spec(self.final_dataset)
        return []
    
    
    async def final_dataset_list_list(self) -> list[list[Any]]: 
        if self.final_dataset is not None: 
            return df_to_list_of_lists(self.final_dataset.head(50))
        return []


    @rx.var 
    def get_base_dataset_cols(self) -> List[str]: 
        if self.base_dataset is not None: 
            return self.base_dataset.columns.tolist()

        return []
    
    def set_base_imputation_choices(self, val: dict): 
        print("backend: Setting base imputation choices...")
        self.base_imputation_choices = val

        null_handled_df = handle_null_imputation(self.base_dataset, self.base_imputation_choices)
        self.base_dataset = null_handled_df


    def set_final_imputation_choices(self, val: dict): 
        self.final_imputation_choices = val

        null_handled_df = handle_null_imputation(self.final_dataset, self.final_imputation_choices)
        self.final_dataset = null_handled_df

    
    @rx.var
    def get_ml_options(self) -> str:
        """
        Return a formatted string containing the ML options.
        """
        # return f"ML Problem Type: {self.ml_problem_type}, Target Variable: {self.target_var}, Evaluation Metric: {self.evaluation_metric}, Training Framework: {self.training_framework}"
        return f"ML Problem Type: {self.ml_problem_type}, Target Variable: {self.target_var}, Training Framework: {self.training_framework}"


    @rx.var 
    def get_base_ml_metrics(self) -> str: 
        if len(self.auto_ml_metrics_dic) >= 2: 
            base_metrics = self.auto_ml_metrics_dic["base_model_metrics"]
            print("get_base_ml_metrics:")
            print(str(base_metrics))
            return str(base_metrics)

        return "AutoML not run..."
    
    @rx.var 
    def get_revised_ml_metrics(self) -> str: 
        if len(self.auto_ml_metrics_dic) >= 2: 
            base_metrics = self.auto_ml_metrics_dic["revised_model_metrics"]
            print("get_revised_ml_metrics:")
            print(str(base_metrics))
            return str(base_metrics)

        return "AutoML not run..."
    

    @rx.var
    def get_main_base_ml_metric(self) -> str: 
        if len(self.auto_ml_metrics_dic) >= 2: 
            metrics = self.auto_ml_metrics_dic["base_model_metrics"]
            
            if self.ml_problem_type == 'classification':
                return f"{metrics['accuracy']:.3f}"
            elif self.ml_problem_type == 'regression':
                return f"{metrics['r2']:.3f}"
        
        return "..."

    @rx.var
    def get_main_revised_ml_metric(self) -> str: 
        if len(self.auto_ml_metrics_dic) >= 2: 
            metrics = self.auto_ml_metrics_dic["revised_model_metrics"]
            
            if self.ml_problem_type == 'classification':
                return f"{metrics['accuracy']:.3f}"
            elif self.ml_problem_type == 'regression':
                return f"{metrics['r2']:.3f}"
        
        return "..."
    

    @rx.var 
    def get_base_rmse(self) -> str:
        if len(self.auto_ml_metrics_dic) >= 2: 
            metrics = self.auto_ml_metrics_dic["base_model_metrics"]
            return f"{metrics['rmse']:.3f}"
        
        return "..."
    
    @rx.var
    def get_revised_rmse(self) -> str:
        if len(self.auto_ml_metrics_dic) >= 2: 
            metrics = self.auto_ml_metrics_dic["revised_model_metrics"]
            return f"{metrics['rmse']:.3f}"
        
        return "..."
    
    @rx.var
    def get_base_mae(self) -> str:
        if len(self.auto_ml_metrics_dic) >= 2: 
            metrics = self.auto_ml_metrics_dic["base_model_metrics"]
            return f"{metrics['mae']:.3f}"
        
        return "..."
    
    @rx.var
    def get_revised_mae(self) -> str:
        if len(self.auto_ml_metrics_dic) >= 2: 
            metrics = self.auto_ml_metrics_dic["revised_model_metrics"]
            return f"{metrics['mae']:.3f}"
        
        return "..."
    
    @rx.var
    def get_base_mape(self) -> str:
        if len(self.auto_ml_metrics_dic) >= 2: 
            metrics = self.auto_ml_metrics_dic["base_model_metrics"]
            return f"{metrics['mape']:.3f}"
        
        return "..."
    
    @rx.var
    def get_revised_mape(self) -> str:
        if len(self.auto_ml_metrics_dic) >= 2: 
            metrics = self.auto_ml_metrics_dic["revised_model_metrics"]
            return f"{metrics['mape']:.3f}"
        
        return "..."


    async def get_final_dataset_head(self, num: int) -> pd.DataFrame: 
        head_df = self.final_dataset.head(num)

        # Convert boolean values (True/False) to string representations ("True"/"False")
        head_df = head_df.applymap(lambda x: str(x) if isinstance(x, bool) else x)

        return head_df
    
    async def get_combined_results_head(self, num: int) -> pd.DataFrame: 
        # head_df = self.final_dataset.head(num)

        head_df = self.combined_results.head(num)

        # Convert boolean values (True/False) to string representations ("True"/"False")
        head_df = head_df.applymap(lambda x: str(x) if isinstance(x, bool) else x)

        return head_df
    
    def get_base_dataset_head(self, num: int) -> pd.DataFrame: 
        head_df = self.base_dataset.head(num)
        return head_df

    def get_new_feature_id(self) -> int:
        """Retrieves the greatest id value and increments it to generate a new id."""
        if not self.features:
            return 1  # If no features exist, start with ID 1
        # Find the maximum id in the current features list and increment it
        max_id = max(feature.id for feature in self.features)
        return max_id + 1
    

    def add_feature(self, feature_name: str = "", description: str = "") -> int:
        """Adds a new Feature to the features list."""
        print("Calling add feature in backend...")
        
        # Get a new ID for the feature
        new_id = self.get_new_feature_id()
        
        # Create the new feature with the generated ID
        new_feature = Feature(id=new_id, feature_name=feature_name, description=description)
        
        # Add the new feature to the features list
        self.features.append(new_feature)

        print(f"New Feature Added: {feature_name}, ID: {new_id}")
        print(description)
        print("Current features list:")
        print(self.features)

        return new_id
    
    def save_feature(self, id: int, feature_name: str, description: str) -> bool:
        """Finds the feature by id and updates its name and description."""
        # Iterate over the features to find the one with the matching id
        for feature in self.features:
            if feature.id == id:
                feature.feature_name = feature_name
                feature.description = description
                print(f"Feature with ID {id} updated: Name: {feature_name}, Description: {description}")
                return True
        print(f"No feature found with ID {id}.")
        return False
    

    def remove_feature(self, id: int) -> bool:
        """Removes a feature from the features list by id."""
        # Find the feature by id and remove it
        for feature in self.features:
            if feature.id == id:
                self.features.remove(feature)
                print(f"Feature with ID {id} removed.")
                return True
        print(f"No feature found with ID {id}.")
        return False
    

    def remove_all_features(self): 
        self.features = []


    def get_features(self):
        return self.features
    

    def run_feature_generation(self):
        print("Running Feature Generation")



    def run_test_auto_ml_values(self):
        print("Running AutoML Test")
        self.base_dataset = pd.read_csv('csvs/base_dataset_1000_missing_values.csv')
        self.final_dataset = pd.read_csv('csvs/base_dataset.csv')
        print("- Loaded csvs")
        # ML Options 
            # ml_problem_type: str 
            # target_var: str 
            # evaluation_metric: str 
            # training_framework: str
        self.target_var = 'price'

        self.run_auto_ml_process()
        print("Done")

    

    async def run_auto_ml_process(self): 
        print("- Starting AutoML training")

        """
        ['xgboost', 'xgb_limitdepth', 'rf', 'lgbm', 
        'lgbm_spark', 'rf_spark', 'lrl1', 'lrl2', 'catboost', 'extra_tree', 'kneighbor', 'transformer', 'transformer_ms', 'histgb', 
        'svc', 'sgd', 'nb_spark', 'enet', 'lassolars', 'glr_spark', 'lr_spark', 'svc_spark', 'gbt_spark', 'aft_spark']
        """

        results = train_and_compare_automl(
            base_df=self.base_dataset,
            revised_df=self.final_dataset,
            problem_type=self.ml_problem_type,  
            target=self.target_var, 
            training_framework=self.training_framework,  
        )


        self.auto_ml_metrics_dic = results

        print("Comparison Results:", results)

        return 


    def save_generated_code(self, code: str, file_path: str = "auto_generated_functions.py"):
        """Save the generated code to a Python file. If the file exists, delete its contents first."""
        
        
        # Now append the generated code
        print("FILE PATH:", file_path)
        with open(file_path, "a") as f:
            f.write(f"\n\n{code}\n")
        
        print(f"Generated code saved to {file_path}")


    def clear_current_generated_code(self, file_path: str = "auto_generated_functions.py"):
        # Delete the file if it exists (optional, removes the file)
        if os.path.exists(file_path):
            # Open in write mode ('w') to clear the file contents
            with open(file_path, "w") as f:
                pass  # This clears the file by overwriting with an empty file



    def test_code_gen_chain(self): 
        print("Testing code gen chain...")
        requests = [
        ("clean_title", "Give me a function that takes the `clean_title` column from my dataframe and transforms it into a boolean"),
        ("engine", """Give me a function that takes the `engine` column and outputs the following new columns: `horsepower`, `displacement`, `num_cylinders`. If you can't identify a value for each column, output a null. The expected values for our columns in this example are as follows: `horsepower` = `172`, `displacement` = `1.6`, `num_cylinders` = `4`""")
        ]

        ALL_DOCS = pd.read_csv('csvs/all_docs.csv')

        self.remove_all_features()
        self.add_feature("clean_title", "Give me a function that takes the `clean_title` column from my dataframe and transforms it into a boolean")
        self.add_feature("engine", """Give me a function that takes the `engine` column and outputs the following new columns: `horsepower`, `displacement`, `num_cylinders`. If you can't identify a value for each column, output a null. The expected values for our columns in this example are as follows: `horsepower` = `172`, `displacement` = `1.6`, `num_cylinders` = `4`""")

        #Clear out previousely generated code
        self.clear_current_generated_code()

        for feature in self.features:
            print("Feature CODE GEN CHAIN INPUT:")
            print(feature.feature_name)
            print(feature.description)
            output = CODE_GEN_CHAIN.invoke({
                "docs": ALL_DOCS,
                "col": feature.feature_name, 
                "request": feature.description
            })


            ########
            pprint(output)
            output = clean_json_output(output)


            
            # Save the generated code to a file
            if "code" in output:
                print("Generated code:\n", output["code"])
                gen_code = output["code"]
                self.save_generated_code(code=gen_code)




                
    

    
    def run_code_gen_and_execution_v2(self):
        print("Running code generation and execution...")

        self.clear_current_generated_code()  # Clear previously generated code file


        target_column = self.base_dataset[self.target_var]

        df = self.base_dataset.drop(columns=[self.target_var])
        
        # CODE_GEN vars 
        df_sample = df_sampler(df)        
        
        successful_functions = []
        combined_results = pd.DataFrame()

        for feature in self.features:
            retries = 0
            success = False

            while retries < MAX_RETRIES and not success:
                print("Feature:", feature.description)
                print("Try number:", retries)

                
                output = CODE_GEN_CHAIN_V2.invoke({
                    "feature_name": feature.feature_name,
                    "request": feature.description,
                    "documentation": self.db_table_comments,
                    "table_sample": df_sample,
                })
                

                print()
                print()
                print("code gen chain output:")
                print(output)
                print()
                print()

                code = extract_code_from_content_v2(output)

                print()
                print("Extracted code:")
                print(code)
                print()


                if not code:
                    print(f"Retrying Feature {feature.feature_name} due to missing code.")
                    retries += 1 
                    continue # No code generated; skip this feature

                save_generated_code(code=code)  # Save the latest code to file

                func = load_single_function("auto_generated_functions.py", feature.feature_name)
                if func:
                    # result = execute_single_function(func, df)
                    result = execute_single_function(func, df.copy())

                    if result is not None:  # If function succeeded
                        combined_results = pd.concat([combined_results, result], axis=1)
                        successful_functions.append(feature.feature_name)
                        success = True
                    else:
                        retries += 1
                        print(f"Retry {retries} for feature {feature.feature_name}")

                else: # Function not loaded
                    print(f"Function {feature.feature_name} could not be loaded.")
                    break

        combined_results = remove_duplicate_columns(df, combined_results)

        final_result_df = pd.concat([df, combined_results, target_column], axis=1)


        print("COMBINED RESULTS DF cols:")
        print(combined_results.columns.tolist())

        print("DF COL LIST:")
        print(df.columns.tolist())

        print("Final results columns:")
        print(final_result_df.columns.tolist())


        return final_result_df
            

    

    



    def run_code_gen_and_execution_v3(self):
        print("Running code generation and execution...")

        self.clear_current_generated_code()  # Clear previously generated code file


        print("BASE DATASET COLS:")
        print(self.base_dataset.columns.tolist())

        target_column = self.base_dataset[self.target_var]

        df = self.base_dataset.drop(columns=[self.target_var])

        print("DF AT BEGINNING COLS:")
        print(df.columns.tolist())
        
        # CODE_GEN vars 
        df_sample = df_sampler(df)        
        
        successful_functions = []
        combined_results = pd.DataFrame()

        for feature in self.features:
            retries = 0
            success = False

            while retries < MAX_RETRIES and not success:
                print("Feature:", feature.description)
                print("Try number:", retries)

                
                output = CODE_GEN_CHAIN_V3.invoke(
                    {
                    "feature_name": feature.feature_name,
                    "request": feature.description,
                    "documentation": self.db_table_comments,
                    "table_sample": df_sample,
                    },
                    model=self.llm_to_use
                )



                print()
                print()
                print("V3 code gen chain output:")
                print(output)
                print()
                print()

                #break

                
                code = extract_code_from_content_v3(output)

                print()
                print("Extracted code:")
                print(code)
                print()


                if not code:
                    print(f"Trying again with feature {feature.feature_name} due to missing code.")
                    retries += 1 
                    continue
                    #break  # No code generated; skip this feature

                save_generated_code(code=code)  # Save the latest code to file

                func = load_single_function("auto_generated_functions.py", feature.feature_name)
                if func:
                    #result = execute_single_function(func, df)
                    result = execute_single_function(func, df.copy())

                    if result is not None:  # If function succeeded
                        combined_results = pd.concat([combined_results, result], axis=1)
                        successful_functions.append(feature.feature_name)
                        success = True
                    else:
                        retries += 1
                        print(f"Retry {retries} for feature {feature.feature_name}")

                else: # Function not loaded
                    print(f"Function {feature.feature_name} could not be loaded.")
                    break


        combined_results = remove_duplicate_columns(df, combined_results)

        final_result_df = pd.concat([df, combined_results, target_column], axis=1)

        print("COMBINED RESULTS DF cols:")
        print(combined_results.columns.tolist())

        print("DF COL LIST:")
        print(df.columns.tolist())

        print("Final results columns:")
        print(final_result_df.columns.tolist())


        return final_result_df
    


    


    def generate_single_feature_code(self, feature_id: int) -> str:

        feature: FeatureV2 = None 

        for f in self.features_v2:
            if f.id == feature_id:
                feature = f
                break

        if feature is None:
            print("ERROR: Feature not found in generate_single_feature_code")
            return


        print("generate_single_feature_code for feature:", feature.name)

        type = 'v2'

        if self.llm_to_use == 'gpt-4o-mini':
            # final_result_df = self.run_code_gen_and_execution_v2()
            type = 'v2'
        else:
            #final_result_df = self.run_code_gen_and_execution_v3()
            type = 'v3'

        df = self.base_dataset.drop(columns=[self.target_var])

        df_sample = df_sampler(df)

        # Define a unique save path for each feature
        save_path = f"generated_code/feature_{feature.id}.py"


        retries = 0
        success = False

        code = "Code not set in generate_single_feature_code..."

        while retries < MAX_RETRIES and not success:
            print("Feature:", feature.description)
            print("Try number:", retries)

            # Invoke the code generation chain based on the specified type
            if type == 'v2':
                output = CODE_GEN_CHAIN_V2.invoke({
                    "feature_name": feature.name,
                    "request": feature.description,
                    "documentation": self.db_table_comments,
                    "table_sample": df_sample,
                })
            else: 
                output = CODE_GEN_CHAIN_V3.invoke(
                    {
                        "feature_name": feature.name,
                        "request": feature.description,
                        "documentation": self.db_table_comments,
                        "table_sample": df_sample,
                    },
                    model=self.llm_to_use
                )

            print("\n\ncode gen chain output:")
            print(output)

            # Extract code based on the chain version
            code = extract_code_from_content_v2(output) if type == 'v2' else extract_code_from_content_v3(output)
            print("\nExtracted code:")
            print(code)

            if not code:
                print(f"Retrying Feature {feature.name} due to missing code.")
                retries += 1 
                continue  # Retry if no code was generated

            # Save the code to the unique file path for this feature
            save_generated_code(code=code, file_path=save_path)

            # Load and execute the function from the unique file path
            func = load_single_function(save_path, feature.name)
            if func:
                result = execute_single_function(func, df.copy())
                if result is not None:  # If function succeeded
                    
                    feature.code = code
                    # combined_results = pd.concat([combined_results, result], axis=1)
                    # successful_functions.append(feature.feature_name)
                    success = True
                else:
                    retries += 1
                    print(f"Retry {retries} for feature {feature.name}")
            else:
                print(f"Function {feature.name} could not be loaded.")
                break

        return code 

    

    def run_all_feature_functions(self): 
        print("Running all feature functions...")

        target_column = self.base_dataset[self.target_var]
        df = self.base_dataset.drop(columns=[self.target_var])
        
        successful_functions = []
        combined_results = pd.DataFrame()


        for feature in self.features_v2:

            save_path = f"generated_code/feature_{feature.id}.py"


            # Load and execute the function from the unique file path
            func = load_single_function(save_path, feature.name)
            if func:
                result = execute_single_function(func, df.copy())
                if result is not None:  # If function succeeded
                    combined_results = pd.concat([combined_results, result], axis=1)
                    successful_functions.append(feature.name)

        # Remove duplicate columns and concatenate the final result
        combined_results = remove_duplicate_columns(df, combined_results)

        final_result_df = pd.concat([df, combined_results, target_column], axis=1)

        self.combined_results = combined_results


        print("COMBINED RESULTS DF cols:", combined_results.columns.tolist())
        print("DF COL LIST:", df.columns.tolist())
        print("Final results columns:", final_result_df.columns.tolist())

        return final_result_df


    def run_all_feature_functions_parent(self):
        """Parent function to try V3 first with a timeout, and fall back to V2 if necessary."""

        final_result_df = None

        final_result_df = self.run_all_feature_functions()


        # Set the final dataset in the parent function
        if final_result_df is not None:
            # Save final DataFrame
            final_result_df.to_csv('features_generated.csv', index=False)
            print("Final DataFrame saved to 'features_generated.csv'.")
            self.final_dataset = final_result_df
            print("Final DataFrame set in parent function.")
            print("Model Used: ", self.llm_to_use)
        else:
            print("No final DataFrame generated.")


    # def generate_all_features(self, type):
    #     print("Running code generation and execution...")

    #     self.clear_current_generated_code()  # Clear previously generated code file


    #     target_column = self.base_dataset[self.target_var]

    #     df = self.base_dataset.drop(columns=[self.target_var])
        
    #     # CODE_GEN vars 
    #     df_sample = df_sampler(df)        
        
    #     successful_functions = []
    #     combined_results = pd.DataFrame()

    #     for feature in self.features:
    #         retries = 0
    #         success = False

    #         save_path = f"generated_code/{feature.id}.py"

    #         while retries < MAX_RETRIES and not success:
    #             print("Feature:", feature.description)
    #             print("Try number:", retries)

                
    #             if type == 'v2':
    #                 output = CODE_GEN_CHAIN_V2.invoke({
    #                     "feature_name": feature.feature_name,
    #                     "request": feature.description,
    #                     "documentation": self.db_table_comments,
    #                     "table_sample": df_sample,
    #                 })
    #             else: 
    #                 output = CODE_GEN_CHAIN_V3.invoke(
    #                     {
    #                     "feature_name": feature.feature_name,
    #                     "request": feature.description,
    #                     "documentation": self.db_table_comments,
    #                     "table_sample": df_sample,
    #                     },
    #                     model=self.llm_to_use
    #                 )

                

    #             print()
    #             print()
    #             print("code gen chain output:")
    #             print(output)
    #             print()
    #             print()

    #             if type == 'v2':
    #                 code = extract_code_from_content_v2(output)
    #             else: 
    #                 code = extract_code_from_content_v3(output)

    #             print()
    #             print("Extracted code:")
    #             print(code)
    #             print()


    #             if not code:
    #                 print(f"Retrying Feature {feature.feature_name} due to missing code.")
    #                 retries += 1 
    #                 continue # No code generated; skip this feature

    #             save_generated_code(code=code)  # Save the latest code to file

    #             func = load_single_function("auto_generated_functions.py", feature.feature_name)
    #             if func:
    #                 # result = execute_single_function(func, df)
    #                 result = execute_single_function(func, df.copy())

    #                 if result is not None:  # If function succeeded
    #                     combined_results = pd.concat([combined_results, result], axis=1)
    #                     successful_functions.append(feature.feature_name)
    #                     success = True
    #                 else:
    #                     retries += 1
    #                     print(f"Retry {retries} for feature {feature.feature_name}")

    #             else: # Function not loaded
    #                 print(f"Function {feature.feature_name} could not be loaded.")
    #                 break

    #     combined_results = remove_duplicate_columns(df, combined_results)

    #     final_result_df = pd.concat([df, combined_results, target_column], axis=1)


    #     print("COMBINED RESULTS DF cols:")
    #     print(combined_results.columns.tolist())

    #     print("DF COL LIST:")
    #     print(df.columns.tolist())

    #     print("Final results columns:")
    #     print(final_result_df.columns.tolist())


    #     return final_result_df
            

    def generate_all_features(self, type):
        print("Running code generation and execution...")

        self.clear_current_generated_code()  # Clear previously generated code file

        target_column = self.base_dataset[self.target_var]
        df = self.base_dataset.drop(columns=[self.target_var])
        
        # CODE_GEN vars 
        df_sample = df_sampler(df)        
        successful_functions = []
        combined_results = pd.DataFrame()

        for feature in self.features:
            retries = 0
            success = False

            # Define a unique save path for each feature
            save_path = f"generated_code/feature_{feature.id}.py"

            while retries < MAX_RETRIES and not success:
                print("Feature:", feature.description)
                print("Try number:", retries)

                # Invoke the code generation chain based on the specified type
                if type == 'v2':
                    output = CODE_GEN_CHAIN_V2.invoke({
                        "feature_name": feature.feature_name,
                        "request": feature.description,
                        "documentation": self.db_table_comments,
                        "table_sample": df_sample,
                    })
                else: 
                    output = CODE_GEN_CHAIN_V3.invoke(
                        {
                            "feature_name": feature.feature_name,
                            "request": feature.description,
                            "documentation": self.db_table_comments,
                            "table_sample": df_sample,
                        },
                        model=self.llm_to_use
                    )

                print("\n\ncode gen chain output:")
                print(output)

                # Extract code based on the chain version
                code = extract_code_from_content_v2(output) if type == 'v2' else extract_code_from_content_v3(output)
                print("\nExtracted code:")
                print(code)

                if not code:
                    print(f"Retrying Feature {feature.feature_name} due to missing code.")
                    retries += 1 
                    continue  # Retry if no code was generated

                # Save the code to the unique file path for this feature
                save_generated_code(code=code, file_path=save_path)

                # Load and execute the function from the unique file path
                func = load_single_function(save_path, feature.feature_name)
                if func:
                    result = execute_single_function(func, df.copy())
                    if result is not None:  # If function succeeded
                        combined_results = pd.concat([combined_results, result], axis=1)
                        successful_functions.append(feature.feature_name)
                        success = True
                    else:
                        retries += 1
                        print(f"Retry {retries} for feature {feature.feature_name}")
                else:
                    print(f"Function {feature.feature_name} could not be loaded.")
                    break

        # Remove duplicate columns and concatenate the final result
        combined_results = remove_duplicate_columns(df, combined_results)
        final_result_df = pd.concat([df, combined_results, target_column], axis=1)
        self.combined_results = combined_results

        print("COMBINED RESULTS DF cols:", combined_results.columns.tolist())
        print("DF COL LIST:", df.columns.tolist())
        print("Final results columns:", final_result_df.columns.tolist())

        return final_result_df



    
    def run_code_gen_and_execution_parent(self):
        """Parent function to try V3 first with a timeout, and fall back to V2 if necessary."""

        final_result_df = None

        print("Using LLM:", self.llm_to_use)

        type = 'v2'

        if self.llm_to_use == 'gpt-4o-mini':
            # final_result_df = self.run_code_gen_and_execution_v2()
            type = 'v2'
        else:
            #final_result_df = self.run_code_gen_and_execution_v3()
            type = 'v3'

        final_result_df = self.generate_all_features(type=type)


        # Set the final dataset in the parent function
        if final_result_df is not None:
            # Save final DataFrame
            final_result_df.to_csv('features_generated.csv', index=False)
            print("Final DataFrame saved to 'features_generated.csv'.")
            self.final_dataset = final_result_df
            print("Final DataFrame set in parent function.")
            print("Model Used: ", self.llm_to_use)
        else:
            print("No final DataFrame generated.")



    async def test_code_gen_and_execution(self): 
        self.remove_all_features()

        self.add_feature("clean_title_bool", "Give me a function that takes the `clean_title` column from my dataframe and transforms it into a boolean")
        self.add_feature("horsepower", """Give me a function that takes the `engine` column and outputs the following new columns: `horsepower`. If you can't identify a value for the column, output a null. The expected values for the column in this example are as follows: `horsepower` = `172`""")
        self.add_feature("displacement", """Give me a function that takes the `engine` column and outputs the following new columns: `displacement`. If you can't identify a value for the column, output a null. The expected values for the column in this example are as follows: `displacement` = `1.6`""")
        self.add_feature("num_cylinders", """Give me a function that takes the `engine` column and outputs the following new columns: `num_cylinders`. If you can't identify a value for the column, output a null. The expected values for the column in this example are as follows: `num_cylinders` = `4`""")
        self.add_feature("mileage_over_10000", """Give me a field that indicates True when the vehicle has more than 10000 miles on it. Use the mileage field.""")
        self.add_feature("american_brand", """Create a field to indicate that a vehicle was made by an American company""")

        self.run_code_gen_and_execution_parent()
        

        return True 

    




 # def run_code_gen_and_execution(self):
    #     print("Running code gen execution...")

    #     """Run the code generation, save the functions, load them, and execute them."""
    #     self.run_code_gen_chain()

    #     print("Code gen chain DONE ")
   
    #     df = self.base_dataset
    #     target_var = self.target_var

    #     # Drop the target column from the base dataset
    #     df_without_target = df.drop(columns=[target_var])

    #     # Dynamically load and execute all generated functions
    #     functions = load_all_functions()  # Load all generated functions from the saved file
    #     result_df = execute_functions_on_df(functions, df, target_var)  # Execute functions and combine results

    #     # Remove duplicate columns from df_without_target
    #     df_without_target = remove_duplicate_columns(df_without_target, result_df)


    #     # Concatenate the original (minus target) with the generated features
    #     result_df = pd.concat([df_without_target.reset_index(drop=True), result_df.reset_index(drop=True)], axis=1)

        
    #     # Display the final dataframe
    #     print("Final DataFrame with all generated feature columns:")
    #     print(result_df)


    #     # Save the final DataFrame to a CSV file
    #     result_df.to_csv('features_generated.csv', index=False)
    #     print("Final DataFrame saved to 'features_generated.csv'.")


    #     self.final_dataset = result_df



    

    # def test_code_gen_and_execution(self):
    #     print("Running code generation and execution...")

    #     # SHOULD BE ONLY DIFFERENT between test and run 
    #     self.remove_all_features()
    #     self.add_feature("clean_title_bool", "Give me a function that takes the `clean_title` column from my dataframe and transforms it into a boolean")
    #     self.add_feature("horsepower", """Give me a function that takes the `engine` column and outputs the following new columns: `horsepower`. If you can't identify a value for the column, output a null. The expected values for the column in this example are as follows: `horsepower` = `172`""")
    #     self.add_feature("displacement", """Give me a function that takes the `engine` column and outputs the following new columns: `displacement`. If you can't identify a value for the column, output a null. The expected values for the column in this example are as follows: `displacement` = `1.6`""")
    #     self.add_feature("num_cylinders", """Give me a function that takes the `engine` column and outputs the following new columns: `num_cylinders`. If you can't identify a value for the column, output a null. The expected values for the column in this example are as follows: `num_cylinders` = `4`""")

    #     self.add_feature("mileage_over_10000", """Give me a field that indicates True when the vehicle has more than 10000 miles on it. Use the mileage field.""")
    #     self.add_feature("american_brand", """Create a field to indicate that a vehicle was made by an American company""")

    #     self.run_code_gen_and_execution()

        # self.clear_current_generated_code()  # Clear previously generated code file

        # target_column = self.base_dataset[self.target_var]

        # df = self.base_dataset.drop(columns=[self.target_var])
        
        # # CODE_GEN vars 
        # df_sample = df_sampler(df)
        # df_docs = read_file_to_string('train_docs_text.txt')
        
        


        # successful_functions = []
        # combined_results = pd.DataFrame()

        # for feature in self.features:
        #     retries = 0
        #     success = False

        #     while retries < MAX_RETRIES and not success:
        #         print("Feature:", feature.description)
        #         print("Try number:", retries)

                
        #         output = CODE_GEN_CHAIN_V2.invoke({
        #             "feature_name": feature.feature_name,
        #             "request": feature.description,
        #             "documentation": df_docs,
        #             "table_sample": df_sample,
        #         })

        #         print()
        #         print()
        #         print("code gen chain output:")
        #         print(output)
        #         print()
        #         print()

        #         code = extract_code_from_content(output)

        #         print()
        #         print("Extracted code:")
        #         print(code)
        #         print()


        #         if not code:
        #             print(f"Skipping feature {feature.feature_name} due to missing code.")
        #             break  # No code generated; skip this feature

        #         save_generated_code(code=code)  # Save the latest code to file

        #         func = load_single_function("auto_generated_functions.py", feature.feature_name)
        #         if func:
        #             result = execute_single_function(func, df)
        #             if result is not None:  # If function succeeded
        #                 combined_results = pd.concat([combined_results, result], axis=1)
        #                 successful_functions.append(feature.feature_name)
        #                 success = True
        #             else:
        #                 retries += 1
        #                 print(f"Retry {retries} for feature {feature.feature_name}")

        #         else: # Function not loaded
        #             print(f"Function {feature.feature_name} could not be loaded.")
        #             break


        # # print("Combined results columns:")
        # # print(combined_results.columns.tolist())
                    
        # # Append the target column back to the combined_results DataFrame
        # # combined_results = pd.concat([combined_results, target_column], axis=1)

        # # print("Combined results columns after concat with target_col:")
        # # print(combined_results.columns.tolist())


        # # print("DF columns:")
        # # print(df.columns.tolist())

        
        # # # Combine the original dataframe (minus target column) with generated features
        # # final_result_df = pd.concat([df.reset_index(drop=True), combined_results.reset_index(drop=True)], axis=1)


        # final_result_df = pd.concat([df, target_column], axis=1)

        # print("Final results columns:")
        # print(final_result_df.columns.tolist())


        # # Save final DataFrame
        # final_result_df.to_csv('features_generated.csv', index=False)
        # print("Final DataFrame saved to 'features_generated.csv'.")
        # self.final_dataset = final_result_df

        # print(f"Successfully generated features: {successful_functions}")
        # if len(successful_functions) < len(self.features):
        #     print("Some features could not be generated.")





# def run_code_gen_chain(self):
    #     print("-  Running code gen chain...")


    #     ALL_DOCS = pd.read_csv('csvs/all_docs.csv')

    #     #Clear out previousely generated code
    #     self.clear_current_generated_code()


    #     for feature in self.features:
    #         print("Feature CODE GEN CHAIN INPUT:")
    #         print(feature.feature_name)
    #         print(feature.description)
    #         output = CODE_GEN_CHAIN.invoke({
    #             "docs": ALL_DOCS,
    #             "col": feature.feature_name, 
    #             "request": feature.description
    #         })

    #         ########
    #         pprint(output)
    #         output = clean_json_output(output)

    #         # Save the generated code to a file
    #         if "code" in output:
    #             print("Generated code:\n", output["code"])
    #             gen_code = output["code"]
    #             self.save_generated_code(code=gen_code)




    # def test_code_gen_and_execution_REMOVETHISPART(self):
    #     print("Testing code gen execution...")


    #     # SHOULD BE ONLY DIFFERENT between test and run 
    #     self.remove_all_features()
    #     self.add_feature("clean_title", "Give me a function that takes the `clean_title` column from my dataframe and transforms it into a boolean")
    #     self.add_feature("engine", """Give me a function that takes the `engine` column and outputs the following new columns: `horsepower`, `displacement`, `num_cylinders`. If you can't identify a value for each column, output a null. The expected values for our columns in this example are as follows: `horsepower` = `172`, `displacement` = `1.6`, `num_cylinders` = `4`""")


    #     """Run the code generation, save the functions, load them, and execute them."""
    #     self.run_code_gen_chain()

    #     print("Test code gen chain DONE ")

    #     df = self.base_dataset
    #     target_var = self.target_var
        
    #     # Drop the target column from the base dataset
    #     df_without_target = df.drop(columns=[target_var])


    #     # Dynamically load and execute all generated functions
    #     functions = load_all_functions()  # Load all generated functions from the saved file
    #     result_df = execute_functions_on_df(functions, df, target_var)  # Execute functions and combine results

    #     # Remove duplicate columns from df_without_target
    #     df_without_target = remove_duplicate_columns(df_without_target, result_df)

    #     # Concatenate the original (minus target) with the generated features
    #     result_df = pd.concat([df_without_target.reset_index(drop=True), result_df.reset_index(drop=True)], axis=1)


    #     # Display the final dataframe
    #     print("Final DataFrame with all generated feature columns:")
    #     print(result_df)

    #     # Save the final DataFrame to a CSV file
    #     result_df.to_csv('features_generated.csv', index=False)
    #     print("Final DataFrame saved to 'features_generated.csv'.")


    #     self.final_dataset = result_df
