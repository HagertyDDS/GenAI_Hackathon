
import reflex as rx 
from ..backend.feature_flow_state import FeatureFlowState
from .button_stuff import default_class_name, variant_styles, get_variant_class, button_style, button_style_save, button_style_remove

from typing import Any 

from .page_1_state import Page1State




class Feature(rx.Base): 
    id: int 
    name: str 
    description: str

    code: str = "none"

    # def __init__(self, id, name, description, code):
    #     self.id = id 
    #     self.name = name 
    #     self.description = description
    #     self.code = code





# feature_1 = Feature(id = 1, name = "Feature 1", description = "This is the first feature", code = "print('Hello World 1')")
# feature_2 = Feature(id = 2, name = "Feature 2", description = "This is the second feature", code = "print('Hello World 2')")
# feature_3 = Feature(id = 3, name = "Feature 3", description = "This is the third feature", code = "print('Hello World 3')")





# feature_1 = Feature(id = 1, name = "Feature 1", description = "This is the first feature", code = "print('Hello World')")
# feature_2 = Feature(id = 2, name = "Feature 2", description = "This is the second feature", code = "print('Hello World')")
# feature_3 = Feature(id = 3, name = "Feature 3", description = "This is the third feature", code = "print('Hello World')")

# Equivalent dictionary representation
# features_dic = [
#     {
#         "id": 1,
#         "name": "Feature 1",
#         "description": "This is the first feature",
#         "code": "print('Hello World')"
#     },
#     {
#         "id": 2,
#         "name": "Feature 2",
#         "description": "This is the second feature",
#         "code": "print('Hello World')"
#     },
#     {
#         "id": 3,
#         "name": "Feature 3",
#         "description": "This is the third feature",
#         "code": "print('Hello World')"
#     }
# ]

# Accessing the data of a specific feature
# print(features_dic[0]["name"])  # Output: Feature 1
# print(features_dic[2]["description"])  # Output: This is the third feature


class FeatureListState(rx.State): 

    placeholder: str

    features: list[Feature] = []
    # features: list[Feature] = [feature_1, feature_2, feature_3]
    # features: list[Any] = features_dic

    llm: str = "LLM"
    
    async def get_llm(self) -> str: 
        #print("GET_FEATURE_1:", self.features[0]['name'])

        feature_flow_state = await self.get_state(FeatureFlowState) 

        self.llm = feature_flow_state.llm_to_use

        
        return self.llm
    

    def print_features(self):
        for feature in self.features:
            print(feature.name)
            print(feature.description)
            print(feature.code)
            print("\n")
    
    async def create_new_feature(self): 
        feature_flow_state = await self.get_state(FeatureFlowState) 
        feat_dic = feature_flow_state.create_new_feature()

        new_feature = Feature(id = feat_dic['id'], name="", description="", code = feat_dic['code'])
        self.features.append(new_feature)


    async def remove_feature(self, feature_id): 
        feature_flow_state = await self.get_state(FeatureFlowState) 

        removed = feature_flow_state.remove_feature_by_id(feature_id)

        if removed: 
            for feature in self.features:
                if feature.id == feature_id:
                    # Remove the feature from the list
                    self.features.remove(feature)



    async def save_feature(self, feature_id): 

        feature_name = ""
        feature_description = ""

        for feature in self.features:
            if feature.id == feature_id:
                feature_name = feature.name
                feature_description = feature.description


        feature_flow_state = await self.get_state(FeatureFlowState) 
        feature_flow_state.save_feature_by_id(feature_id, feature_name, feature_description)



    def set_feature_name(self, feature_id, feature_name): 
        for feature in self.features:
            if feature.id == feature_id:
                feature.name = feature_name


    def set_feature_description(self, feature_id, feature_description):
        for feature in self.features:
            if feature.id == feature_id:
                feature.description = feature_description


    async def remove_all_features(self): 
        feature_flow_state = await self.get_state(FeatureFlowState) 
        feature_flow_state.remove_all_features()

        self.features = []


    async def generate_all_features(self):
        feature_flow_state = await self.get_state(FeatureFlowState) 
        feature_flow_state.run_code_gen_and_execution_parent()


    async def run_all_feature_functions_parent(self):
        feature_flow_state = await self.get_state(FeatureFlowState) 
        feature_flow_state.run_all_feature_functions_parent()

        p1state = await self.get_state(Page1State)
        p1state.set_features_generated(True)


    async def regenerate_feature_code(self, feature_id): 
        feature_flow_state = await self.get_state(FeatureFlowState) 
        new_code = feature_flow_state.generate_single_feature_code(feature_id)

        for feature in self.features:
            if feature.id == feature_id:
                feature.code = new_code


    


                


def render_feature(feature):
    return rx.hstack(
        rx.card(
            rx.flex(
                rx.input(
                    placeholder="Feature Name", 
                    value=feature.name,
                    on_change=lambda text: FeatureListState.set_feature_name(feature.id, text),
                ),
                
                rx.text_area(
                    placeholder="Describe your feature…",
                    value=feature.description,
                    on_change=lambda text: FeatureListState.set_feature_description(feature.id, text),
                    height="100%",  # Expand to take available height
                    min_height="150px"  # Set a minimum height if needed
                ),

                rx.grid(
                    rx.button( 
                        "Save",
                        on_click=FeatureListState.save_feature(feature.id),
                        style=button_style_save,
                    ),  
                    rx.button(
                        "Delete", 
                        on_click=FeatureListState.remove_feature(feature.id),
                        style=button_style_remove,
                    ),
                    columns="2",
                    spacing="2",
                ),
                direction="column",
                spacing="3",
                height="100%",  # Flex container height
            ),
            width="50%", 
            height="100%",  # Card height to fill available space
        ),

        rx.card(
            rx.flex(
                rx.code_block(
                    feature.code,
                    language="python",
                    show_line_numbers=True,
                ),
                rx.grid(
                    rx.button( 
                        rx.icon(tag="refresh-ccw", color="#24292E"),
                        on_click=FeatureListState.regenerate_feature_code(feature.id),
                        style=button_style_save,
                        background='rgba(51, 51, 51, 0.05)',
                    ),  
                    columns="1",
                    spacing="2",
                ),
                direction="column",
                spacing="3",
                height="100%",  # Flex container height
            ),
            width="50%",
            height="100%",  # Card height to fill available space
        ),
        width="100%",
        height="100%",  # HStack height
        align="stretch",  # Stretch children to fill the stack height
    )



def feature_list_v2():
    return rx.vstack(
        rx.heading("Generate Features"),
        rx.divider(width="100%"),

        rx.vstack(
            rx.hstack(
                rx.icon("codesandbox", color="#6439FF"),
                rx.heading("Databricks Model Serving Endpoint", size="5"),
                align="center",
            ),
            rx.select(
                [
                    "databricks-meta-llama-3-1-70b-instruct", 
                    "databricks-meta-llama-3-1-405b-instruct",
                    "databricks-gte-large-en",
                    "databricks-dbrx-instruct",
                    "databricks-mixtral-8x7b-instruct",
                ],
                placeholder="Select Model Serving Endpoint",
                label="Select Model Serving Endpoint",
                #value=FeatureFlowState.ml_problem_type,
                on_change=FeatureFlowState.set_llm_to_use,
                color="#6439FF",
                radius="full",
                width="50%",
                # variant="soft",

            ),
            width="100%",
            margin_bottom="30px"
        ),

        rx.divider(width="50%"),

        rx.foreach(
            FeatureListState.features,  # Your list of items
            render_feature
        ),

        rx.button(
            rx.icon(tag="plus"),
            on_click=FeatureListState.create_new_feature,
            style=button_style_save,
            background="#c2fbd7",
            color="black",
            width="100px"
        ),


        # rx.button( 
        #     "Remove all Features",
        #     on_click=FeatureListState.remove_all_features,
        #     style=button_style_remove,
        #     # class_name=default_class_name
        #     # + " "
        #     # + variant_styles["primary"]["class_name"]
        #     # + " "
        #     # + get_variant_class("red"),
                    
        # ),
        rx.button(
            "Generate",
            #on_click=FeatureListState.generate_all_features,
            on_click=FeatureListState.run_all_feature_functions_parent,
            style=button_style,
            # class_name=default_class_name
            #     + " "
            #     + variant_styles["primary"]["class_name"]
            #     + " "
            #     + get_variant_class("indigo"),
            margin_bottom="60px",
            margin_top="60px",
            width="20%",
        ),
        padding="40px",
        width="100%",
    )
    






