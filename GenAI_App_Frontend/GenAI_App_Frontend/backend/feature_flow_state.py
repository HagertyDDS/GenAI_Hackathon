
import reflex as rx
from typing import Union, List
import csv
import pandas as pd 



class Feature(rx.Base):
    """The Feature object."""

    feature_name: str
    description: str
    


class FeatureFlowState(rx.State):
    """The state class."""

    # Datasets 
    base_dataset: pd.DataFrame
    final_dataset: pd.DataFrame

    # Features
    features: List[Feature] = []

    # ML Options 
    ml_problem_type: str 
    target_var: str 
    evaluation_metric: str 
    training_framework: str


    def add_feature(self, feature_name: str, description: str):
        """Adds a new Feature to the features list."""
        print("Calling add feature in backend...")
        new_feature = Feature(feature_name=feature_name, description=description)
        self.features.append(new_feature)

        print(feature_name)
        print(description)
        print("self.features:")
        print(self.features)
        # Optionally, you could add a return statement if you want to return the updated list
        return self.features




    
