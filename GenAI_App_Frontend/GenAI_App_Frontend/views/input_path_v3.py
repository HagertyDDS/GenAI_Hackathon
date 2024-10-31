

import reflex as rx 
from typing import Any
from .button_stuff import default_class_name, variant_styles, get_variant_class, button_style
import os
import pandas as pd



from ..backend.feature_flow_state import FeatureFlowState
from ..views.column_null_options import BaseListState
from ..views.automl_settings import MLConfigState
from .page_1_state import Page1State



lightTheme = {
    "accentColor": "#4F81FF",  # Soft blue for accents
    "accentLight": "rgba(79, 129, 255, 0.15)",  # Lighter blue accent for hover effects
    "textDark": "#333333",  # Dark grey for readability
    "textMedium": "#666666",  # Medium grey for subtler text
    "textLight": "#888888",  # Light grey for even subtler text
    "textBubble": "#333333",  # Dark grey for bubble text
    "bgIconHeader": "#e0e0e0",  # Light grey for header icons background
    "fgIconHeader": "#4F81FF",  # Accent color for icon foregrounds
    "textHeader": "#444444",  # Slightly dark grey for headers
    "textHeaderSelected": "#000000",  # Black for selected header text
    "bgCell": "#ffffff",  # White for cell background
    "bgCellMedium": "#f7f7f7",  # Light grey for alternate cell background
    "bgHeader": "#f1f1f1",  # Very light grey for header background
    "bgHeaderHasFocus": "#e8e8e8",  # Slightly darker grey for focused header
    "bgHeaderHovered": "#e0e0e0",  # Hover effect for header
    "bgBubble": "#f1f1f1",  # Light grey for bubble background
    "bgBubbleSelected": "#e0e0e0",  # Slightly darker grey for selected bubbles
    "bgSearchResult": "#fffbcc",  # Soft yellow for search results
    "borderColor": "rgba(0, 0, 0, 0.1)",  # Light border color for a clean separation
    "drilldownBorder": "rgba(0, 0, 0, 0.15)",  # Slightly darker border for drilldown areas
    "linkColor": "#4F81FF",  # Accent color for links
    "headerFontStyle": "bold 14px",  # Bold header font
    "baseFontStyle": "13px",  # Base font style
    #"fontFamily": "Inter, Roboto, -apple-system, BlinkMacSystemFont, Avenir Next, Avenir, Segoe UI, Helvetica Neue, Helvetica, Ubuntu, Noto, Arial, sans-serif",
    "fontFamily": "Instrument Sans",
}


class DataEditorState(rx.State):
    path: str = ""
    csv_data: list = []
    error_message: str = ""
    df: pd.DataFrame = pd.DataFrame()
    df_not_empty: bool = False


    base_df: list[list[Any]] 
    base_cols: list[Any]
    loaded: bool = False
    row_count: int 

    tables: list[str] = []

    tables_ready: bool = False

    chosen_table: str = ""

    loading: bool = False

    def set_loading(self): 
        self.loading = True

    


    def set_chosen_table_var(self, table: list[Any]):
        self.chosen_table = table[0]

    async def load_table(self):
        if not self.chosen_table:
            self.error_message = "Please select a dataset first."
            return

        try:
            
            print("SELF.chosen_table:", self.chosen_table)
            print("chosen_table type", type(self.chosen_table))
            feature_flow_state = await self.get_state(FeatureFlowState)
            base_dt_set = await feature_flow_state.set_base_dataset_from_databricks(self.chosen_table)

            if base_dt_set: 

                feature_flow_state2 = await self.get_state(FeatureFlowState)
                df = feature_flow_state2.get_base_dataset_head(20)

                base_list_state = await self.get_state(BaseListState)
                
                base_list_state.comments_dict = feature_flow_state2.db_table_comments_dict
                
                base_list_state.db_table_data_type_dict = feature_flow_state2.db_table_data_type_dict
                base_list_state.db_table_descriptions_dict = feature_flow_state2.db_table_descriptions_dict

                base_list_state.columns = df.columns.tolist()
                # Initialize imputation_choices as a dictionary with column names as keys and empty strings as values
                base_list_state.imputation_choices = {col: "" for col in df.columns.tolist()}

                mlconfigstate = await self.get_state(MLConfigState)
                mlconfigstate.set_columns(df.columns.tolist())



                lst = await feature_flow_state.base_dataset_list_list()

                self.base_df = lst

                self.base_cols = await feature_flow_state.base_dataset_col_spec()

                self.row_count = len(self.base_df)

                self.loaded = True

                

                self.df = df
                self.error_message = ""

                print("load_csv() done...")
                self.loading = False

                p1state = await self.get_state(Page1State)
                p1state.set_base_datatable_loaded(True)

            else: 
                print("ERROR: Failed to set Base Dataset in backedn, did not return TRUE ")
                self.loading = False
            
        except Exception as e:
            self.error_message = f"Error reading getting table...: {str(e)}"


def base_datatable_v3():
    return rx.vstack(
            rx.heading("Select Dataset"),
            rx.divider(width="100%"),

            rx.select(
                DataEditorState.tables,
                placeholder="Tables",
                label="Tables",
                #value=FeatureFlowState.ml_problem_type,
                on_change=DataEditorState.set_chosen_table_var,
                color="#6439FF",
                radius="full",
                width="50%",
                # variant="soft",

            ),

            rx.hstack(
                # rx.input(
                #     value=DataEditorState.path,
                #     on_change=DataEditorState.set_path,
                #     placeholder="Enter CSV path",
                #     width="100%",
                # ),
                rx.button(
                    "Load", 
                    on_click=[DataEditorState.set_loading, DataEditorState.load_table],
                    loading=DataEditorState.loading,
                    style=button_style,

                ),
            ),
            rx.cond(
                DataEditorState.error_message != "",
                rx.text(DataEditorState.error_message, color="red"),
            ),
  
      
            rx.cond(
                DataEditorState.loaded,
                rx.data_editor(
                    columns=DataEditorState.base_cols,
                    #rows=DataEditorState.row_count,
                    data=DataEditorState.base_df,

                    freeze_columns=1,

                    header_height=120,
                    max_column_width=300,
                    min_column_width=100,
                    row_height=100,
                    smooth_scroll_x=True,
                    overscroll_x=1000,

                    theme=lightTheme,
                    # overscroll_y=100, 
                    smooth_scroll_y=True,
                    height=800,
                    width=1200,

                    border_radius="10px",
                    
                ),
                rx.text("Please select a dataset"),
            ),
       
             

            width="100%",
            spacing="4",
            padding="40px",
        )
