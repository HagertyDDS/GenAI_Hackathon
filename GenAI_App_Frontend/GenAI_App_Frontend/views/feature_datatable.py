import reflex as rx
import pandas as pd
import os
from .button_stuff import default_class_name, variant_styles, get_variant_class
from ..backend.feature_flow_state import FeatureFlowState

from ..views.column_null_options import FinalListState

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
    

def get_dataset_null_options(df):
    """Get imputation options for each column in the dataset."""
    null_options = {}
    
    # Iterate over each column in the dataset
    for column_name in df.columns:
        column_dtype = df[column_name].dtype
        # Get imputation methods based on column data type
        imputation_methods = get_imputation_methods_for_column(column_dtype)
        # Add column and its imputation methods to the dictionary
        null_options[column_name] = imputation_methods
    
    return null_options

class LoadFeatures(rx.ComponentState):
    path: str = "data.csv"
    csv_data: list = []
    error_message: str = ""
    df: pd.DataFrame

    async def load_csv(self):
        
        feature_flow_state = await self.get_state(FeatureFlowState)
        df = await feature_flow_state.get_final_dataset_head(20)

        final_list_state = await self.get_state(FinalListState)
        final_list_state.columns = df.columns.tolist()
        # Initialize imputation_choices as a dictionary with column names as keys and empty strings as values
        final_list_state.imputation_choices = {col: "" for col in df.columns.tolist()}


        print("DF:")
        print(df)

        self.df = df
        self.error_message = ""
         
 
    @classmethod
    def get_component(cls, **props):
        return rx.vstack(
            rx.hstack(
                # rx.input(
                #     value=cls.path,
                #     on_change=cls.set_path,
                #     placeholder="Enter CSV path",
                #     width="100%",
                # ),
                rx.button(
                    "Load CSV", 
                    on_click=cls.load_csv,
                    class_name=default_class_name
                    + " "
                    + variant_styles["primary"]["class_name"]
                    + " "
                    + get_variant_class("indigo"),

                ),
            ),
            rx.cond(
                cls.error_message != "",
                rx.text(cls.error_message, color="red"),
            ),
            rx.cond(
                cls.csv_data != [],
      
                rx.data_table(
                    data=cls.df,
                    pagination=True,
                    search=True,
                    sort=True,
                ),
             
                rx.text("No CSV data loaded yet.")
            ),
            width="100%",
            spacing="4",
        )

loaded_features = LoadFeatures.create

def feature_datatable():
    return rx.vstack(
        rx.heading("Features"),
        rx.divider(width="100%"),

        loaded_features(),
        width="100%",
        spacing="4",
    )