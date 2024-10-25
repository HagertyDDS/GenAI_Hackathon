import reflex as rx
import pandas as pd
import os
from .button_stuff import default_class_name, variant_styles, get_variant_class
from ..backend.feature_flow_state import FeatureFlowState




class LoadFeatures(rx.ComponentState):
    path: str = "data.csv"
    csv_data: list = []
    error_message: str = ""
    df: pd.DataFrame

    async def load_csv(self):
        
        feature_flow_state = await self.get_state(FeatureFlowState)
        df = await feature_flow_state.get_final_dataset_head(20)

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