import reflex as rx
import pandas as pd
import os
from .button_stuff import default_class_name, variant_styles, get_variant_class
from ..backend.feature_flow_state import FeatureFlowState

from ..views.column_null_options import BaseListState


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



class CSVPathInput(rx.ComponentState):
    path: str = ""
    csv_data: list = []
    error_message: str = ""
    df: pd.DataFrame = pd.DataFrame()
    df_not_empty: bool = False


    @rx.var
    def df_is_empty(self) -> bool: 
        if self.df.empty: 
            self.df_not_empty = False
            # self.df_not_empty = self.df_empty 
            print("DF NOT EMPTY:", self.df_not_empty)

            return False
        
        self.df_not_empty = True
        # self.df_empty = self.df_empty 
        print("DF NOT EMPTY:", self.df_not_empty)
        return True

    async def load_csv(self):
        if not self.path:
            self.error_message = "Please enter a CSV path."
            return

        try:
            if os.path.exists(self.path):
                print("SELF.PATH:", self.path)
                feature_flow_state = await self.get_state(FeatureFlowState)
                base_dt_set = await feature_flow_state.set_base_dataset(self.path)

                if base_dt_set: 

                    feature_flow_state2 = await self.get_state(FeatureFlowState)
                    df = feature_flow_state2.get_base_dataset_head(20)

                    base_list_state = await self.get_state(BaseListState)
                    base_list_state.columns = df.columns.tolist()
                    # Initialize imputation_choices as a dictionary with column names as keys and empty strings as values
                    base_list_state.imputation_choices = {col: "" for col in df.columns.tolist()}


                    # Dynamic not used
                    # base_list_state.column_options = get_dataset_null_options(df)

                #df = pd.read_csv(self.path).head(20)

                    self.df = df
                    self.error_message = ""

                    print("load_csv() done...")

                else: 
                    print("ERROR: Failed to set Base Dataset in backedn, did not return TRUE ")
            else:
                self.error_message = f"File not found: {self.path}"
        except Exception as e:
            self.error_message = f"Error reading CSV: {str(e)}"

    @classmethod
    def get_component(cls, **props):
        return rx.vstack(
            rx.hstack(
                rx.input(
                    value=cls.path,
                    on_change=cls.set_path,
                    placeholder="Enter CSV path",
                    width="100%",
                ),
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
  
      
            rx.data_table(
                data=cls.df,
                pagination=True,
                search=False,
                sort=True,
            ),
       
             
       
            width="100%",
            spacing="4",
        )

csv_path_input = CSVPathInput.create

def base_dataset_input():
    return rx.vstack(
        rx.heading("Select Dataset"),
        rx.divider(width="100%"),

        csv_path_input(),
        width="100%",
        spacing="4",
    )