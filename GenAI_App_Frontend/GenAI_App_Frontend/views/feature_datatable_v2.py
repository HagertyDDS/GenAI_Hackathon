

import reflex as rx 
from typing import Any
from .button_stuff import default_class_name, variant_styles, get_variant_class



from ..backend.feature_flow_state import FeatureFlowState



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
    clicked_data: str = "Cell clicked: "


    final_df: list[list[Any]] 
    final_cols: list[Any]
    loaded: bool = False
    row_count: int 

    async def load_dataset(self): 
        feature_flow_state = await self.get_state(FeatureFlowState)

        if feature_flow_state.final_dataset_set: 

            lst = await feature_flow_state.final_dataset_list_list()

            # bad_row = lst.pop(11)
            # print("BAD ROW:", bad_row)

            self.final_df = lst

            self.final_cols = await feature_flow_state.final_dataset_col_spec()

            self.row_count = len(self.final_df)

            self.loaded = True

            print()
            print("FINAL COLS:", self.final_cols)
            print()
            print("FINAL DF:", self.final_df)
            print()
            print("Final DF type ", type(self.final_df))



def feature_datatable_v2():
    return rx.vstack(
        rx.heading("Generated FeatureFlow Dataset"),
        rx.divider(width="100%"),

        rx.button(
                "Load",
                on_click=DataEditorState.load_dataset,
                class_name=default_class_name
                    + " "
                    + variant_styles["primary"]["class_name"]
                    + " "
                    + get_variant_class("indigo"),
                margin_bottom="60px",
        ),

        rx.cond(
            DataEditorState.loaded,
            rx.data_editor(
                columns=DataEditorState.final_cols,
                #rows=DataEditorState.row_count,
                data=DataEditorState.final_df,

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
    

    )

