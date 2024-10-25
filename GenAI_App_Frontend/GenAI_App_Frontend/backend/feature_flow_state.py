
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

# Backend imports 

from .feature_code_gen import CODE_GEN_CHAIN


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

def execute_functions_on_df(functions, df: pd.DataFrame):
    print("\n EXECUTE_FUNCTIONS_ON_DF...")
    print("Function:", functions)

    """Execute all functions on the dataframe and combine the results."""
    combined_df = pd.DataFrame()

    for func in functions:
        print(f"Executing function: {func.__name__}")
        result = func(df)  # Each function is expected to return a single-column dataframe
        combined_df = pd.concat([combined_df, result], axis=1)  # Combine each column

    return combined_df




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


class Feature(rx.Base):
    """The Feature object."""

    id: int
    feature_name: str
    description: str
    


class FeatureFlowState(rx.State):
    """The state class."""


    # Datasets 
    base_dataset: pd.DataFrame
    final_dataset: pd.DataFrame

    # All Docs obj 
    all_docs: pd.DataFrame

    # Features
    features: List[Feature] = []

    # ML Options 
    ml_problem_type: str 
    target_var: str 
    evaluation_metric: str 
    training_framework: str

    # Auto Eval 
    auto_ml_metrics_dic: dict = {}
    base_model_metrics_dic: dict = {}
    revised_model_metrics_dic: dict = {}

    def set_ml_problem_type(self, val: str): 
        self.ml_problem_type = val

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


    @rx.var
    def get_ml_options(self) -> str:
        """
        Return a formatted string containing the ML options.
        """
        return f"ML Problem Type: {self.ml_problem_type}, Target Variable: {self.target_var}, Evaluation Metric: {self.evaluation_metric}, Training Framework: {self.training_framework}"
    

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


    async def get_final_dataset_head(self, num: int) -> pd.DataFrame: 
        head_df = self.final_dataset.head(num)

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
        self.ml_problem_type = 'regression'
        self.target_var = 'price'
        self.training_framework= 'xgb_limitdepth'

        self.run_auto_ml_process()
        print("Done")

    

    def run_auto_ml_process(self): 
        print("- Starting AutoML training")

        results = train_and_compare_automl(
            base_df=self.base_dataset,
            revised_df=self.final_dataset,
            problem_type=self.ml_problem_type,  
            target=self.target_var, 
            training_framework=self.training_framework,  
        )
        self.auto_ml_metrics_dic = results

        print("Comparison Results:", results)


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

        # Test the entire pipeline
                

    def run_code_gen_chain(self):
        print("-  Running code gen chain...")


        ALL_DOCS = pd.read_csv('csvs/all_docs.csv')

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




    def test_code_gen_and_execution(self):
        print("Testing code gen execution...")

        self.base_dataset = pd.read_csv('csvs/train.csv')

        """Test the code generation, save the functions, load them, and execute them."""
        self.test_code_gen_chain()  # Run the code generation and save the code

        print("Test code gen chain DONE ")
        # # Simulate your dataframe
        # data = {
        #     'clean_title': ['yes', 'no', 'yes'],
        #     'engine': ['1.6L 4cyl', '2.0L 6cyl', '1.8L 4cyl']
        # }
        # df = pd.DataFrame(data)
        df = self.base_dataset


        # Dynamically load and execute all generated functions
        functions = load_all_functions()  # Load all generated functions from the saved file
        result_df = execute_functions_on_df(functions, df)  # Execute functions and combine results

        # Display the final dataframe
        print("Final DataFrame with all generated feature columns:")
        print(result_df)

        # Save the final DataFrame to a CSV file
        result_df.to_csv('features_generated.csv', index=False)
        print("Final DataFrame saved to 'features_generated.csv'.")


        self.final_dataset = result_df




    def run_code_gen_and_execution(self):
        print("Running code gen execution...")

        self.base_dataset = pd.read_csv('csvs/train.csv')

        """Test the code generation, save the functions, load them, and execute them."""
        # self.test_code_gen_chain()  # Run the code generation and save the code
        self.run_code_gen_chain()

        print("Code gen chain DONE ")
        # Simulate your dataframe
        # data = {
        #     'clean_title': ['yes', 'no', 'yes'],
        #     'engine': ['1.6L 4cyl', '2.0L 6cyl', '1.8L 4cyl']
        # }
        df = self.base_dataset

        # Dynamically load and execute all generated functions
        functions = load_all_functions()  # Load all generated functions from the saved file
        result_df = execute_functions_on_df(functions, df)  # Execute functions and combine results

        # Display the final dataframe
        print("Final DataFrame with all generated feature columns:")
        print(result_df)

        # Save the final DataFrame to a CSV file
        result_df.to_csv('features_generated.csv', index=False)
        print("Final DataFrame saved to 'features_generated.csv'.")


        self.final_dataset = result_df

    

    # @rx.var
    # def base_dataset_preview(self) -> pd.DataFrame:
    #     print("BASE DATASET C_VAR")
    #     print(self.base_dataset)
    #     return self.base_dataset.head(20)

    # @rx.var
    # def final_dataset_cvar(self) -> pd.DataFrame:
    #     print("FINAL DATESET C_VAR")
    #     print(self.final_dataset)
    #     return self.final_dataset




    
