

import reflex as rx 
from typing import Any
from .button_stuff import default_class_name, variant_styles, get_variant_class
import os
import pandas as pd



from ..backend.feature_flow_state import FeatureFlowState
from ..views.column_null_options import BaseListState



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

    async def load_dataset(self): 
        feature_flow_state = await self.get_state(FeatureFlowState)

        if feature_flow_state.final_dataset_set: 

            lst = await feature_flow_state.final_dataset_list_list()

            self.base_df = lst

            self.base_cols = await feature_flow_state.final_dataset_col_spec()

            self.row_count = len(self.base_df)

            self.loaded = True

            print()
            print("BASE COLS:", self.base_cols)
            print()
            print("BASE DF:", self.base_df)
            print()
            print("BASE DF type ", type(self.base_df))



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



                    lst = await feature_flow_state.base_dataset_list_list()

                    self.base_df = lst

                    self.base_cols = await feature_flow_state.base_dataset_col_spec()

                    self.row_count = len(self.base_df)

                    self.loaded = True

                    

                    self.df = df
                    self.error_message = ""

                    print("load_csv() done...")

                else: 
                    print("ERROR: Failed to set Base Dataset in backedn, did not return TRUE ")
            else:
                self.error_message = f"File not found: {self.path}"
        except Exception as e:
            self.error_message = f"Error reading CSV: {str(e)}"


def base_datatable_v2():
    return rx.vstack(
            rx.heading("Select Dataset"),
            rx.divider(width="100%"),
            rx.hstack(
                rx.input(
                    value=DataEditorState.path,
                    on_change=DataEditorState.set_path,
                    placeholder="Enter CSV path",
                    width="100%",
                ),
                rx.button(
                    "Load", 
                    on_click=DataEditorState.load_csv,
                    class_name=default_class_name
                    + " "
                    + variant_styles["primary"]["class_name"]
                    + " "
                    + get_variant_class("indigo"),

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
                    width=1200
                    
                ),
                rx.text("Please have dataset first"),
            ),
       
             
       
            width="100%",
            spacing="4",
        )
