

import reflex as rx 
from typing import List

from ..backend.feature_flow_state import FeatureFlowState
from .button_stuff import default_class_name, variant_styles, get_variant_class, button_style



class BaseListState(rx.State):
    items: List[str] = ["Write Code", "Sleep", "Have Fun"]
    columns: List[str] = []
    column_options: dict = {}

    imputation_choices: dict = {}
    
    new_item: str

    comments_dict: dict = {}

    db_table_data_type_dict: dict = {}
    db_table_descriptions_dict: dict = {}


    @rx.var 
    def columns_set(self) -> bool:
        if len(self.columns) > 0: 
            return True
        return False
    

    def get_column_options(self, col: str): 
        return self.column_options[col]

    def add_item(self):
        self.items += [self.new_item]

    def finish_item(self, item: str):
        self.items = [i for i in self.items if i != item]

    def set_imputation_choice(self, choice: str, item: str): 
        self.imputation_choices[item] = choice 

    @rx.var
    def get_str_imputation_choices(self) -> str: 
        return str(self.imputation_choices)
    
    async def save_imputation_choices(self):
        print("Saving IMPUTATION CHOICES:", self.imputation_choices)
        
        feature_flow_state = await self.get_state(FeatureFlowState)

        feature_flow_state.set_base_imputation_choices(self.imputation_choices)
        



def get_base_item(item):
    return rx.list.item(
        rx.vstack(
        rx.hstack(
            rx.vstack(
                rx.hstack(
                    rx.badge(
                        item, 
                        font_size="1.25em",
                        variant="soft",
                        radius="full",
                    ),
                    rx.cond(
                        BaseListState.db_table_data_type_dict[item] == "LONG",
                        rx.badge(
                            BaseListState. db_table_data_type_dict[item],
                            font_size="1.25em",
                            variant="soft",
                            radius="full",
                            color="orange",
                        ),
                        rx.badge(
                            BaseListState. db_table_data_type_dict[item],
                            font_size="1.25em",
                            variant="soft",
                            radius="full",
                            color="green",
                        ),

                    ),
                
                ),
                rx.text(
                    BaseListState.db_table_descriptions_dict[item]
                ),
            ),
            rx.select(
                ['None', 'Mean', 'Median', 'Mode'],
   
                placeholder="Imputation Method",
                label="Imputation Method",
                # default_value="None",
                on_change=lambda value: BaseListState.set_imputation_choice(value, item),
                color="#6439FF",
                radius="full",
                width="50%",
            ),
            align="start",
            justify="between",
            width="100%",

        ),
        rx.divider(),
        
        width="100%",
        margin_bottom="15px",
    ))










def base_null_options():
    return rx.cond(
        FeatureFlowState.base_dataset_set & BaseListState.columns_set, 

        rx.vstack(
            rx.heading("Null Value Imputation Options - Base Dataset"),

            rx.divider(),
     
            rx.list(
                rx.foreach(
                    BaseListState.columns,
                    get_base_item,
                ),
                width="100%",
            ),
            rx.button(
                    "Save", 
                    on_click=BaseListState.save_imputation_choices,
                    style=button_style,

            ),
            # rx.text(BaseListState.get_str_imputation_choices),
            # bg="#ededed",
            # padding="1em",
            # border_radius="0.5em",
            # shadow="lg",
            padding="40px",
            width="100%",
        ),
        
    )









class FinalListState(rx.State):
    items: List[str] = ["Write Code", "Sleep", "Have Fun"]
    columns: List[str] = []
    column_options: dict = {}

    imputation_choices: dict = {}
    
    new_item: str



    @rx.var 
    def columns_set(self) -> bool:
        if len(self.columns) > 0: 
            return True
        return False
    

    def get_column_options(self, col: str): 
        return self.column_options[col]

    def add_item(self):
        self.items += [self.new_item]

    def finish_item(self, item: str):
        self.items = [i for i in self.items if i != item]

    def set_imputation_choice(self, choice: str, item: str): 
        self.imputation_choices[item] = choice 

    @rx.var
    def get_str_imputation_choices(self) -> str: 
        return str(self.imputation_choices)
    
    async def save_imputation_choices(self):
        feature_flow_state = await self.get_state(FeatureFlowState)

        feature_flow_state.set_final_imputation_choices(self.imputation_choices)
        



def get_final_item(item):
    return rx.list.item(

        rx.vstack(
        
        rx.hstack(
            rx.badge(
                item, 
                font_size="1.25em",
                variant="soft",
                radius="full",
            ),
            rx.select(
                ['None', 'Mean', 'Median', 'Mode'],
   
                placeholder="Imputation Method",
                label="Imputation Method",
                on_change=lambda value: FinalListState.set_imputation_choice(value, item),
                color="#6439FF",
                radius="full",
                width="50%",
            ),
            align="center",
            justify="between",
            width="100%",

        ),
        rx.divider(),

        width="100%",
        margin_bottom="5px",
    ))










def final_null_options():
    return rx.cond(
        FeatureFlowState.final_dataset_set & FinalListState.columns_set, 

        rx.vstack(
            rx.heading("Null Value Imputation Options - FeatureFLow Dataset"),
            rx.divider(),
            rx.list(
                rx.foreach(
                    FinalListState.columns,
                    get_final_item,
                ),
                width="100%",
            ),
            rx.button(
                    "Save", 
                    on_click=FinalListState.save_imputation_choices,
                    style=button_style,

            ),
            # rx.text(FinalListState.get_str_imputation_choices),
            # bg="#ededed",
            # padding="1em",
            # border_radius="0.5em",
            # shadow="lg",
            width="100%",
            padding="40px",
        ),
        
    )