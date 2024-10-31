
import reflex as rx
from .button_stuff import default_class_name, variant_styles, get_variant_class, button_style, button_style_save, button_style_remove
from ..backend.feature_flow_state import FeatureFlowState

# class MLConfigState(rx.State):
#     problem_type: str = "Classification"
#     prediction_target: str = "brand"
#     evaluation_metric: str = "R-Squared"
#     training_framework: str = "XGBoost"



# Assuming you've already handled the imports
# Assuming 'FeatureFlowState' is already defined in your backend

class create_feature_card(rx.ComponentState):

    # For managing frontend component logic 
    component_id: int = 0 

    # State for the input fields
    feature_id: int = None 
    feature_name_input: str = ""
    description_input: str = ""

    # @rx.var
    # async def card_on(self): 
    #     state = await self.get_state(FeatureCardManager)
    #     on = state.card_1_on
    #     return on 

    def set_component_id(self, val: int): 
        self.component_id = val
        print("Setting component id as:", self.component_id)



    async def save_feature(self):
        if self.feature_id == None:
            feature_flow_state = await self.get_state(FeatureFlowState)
            self.feature_id = feature_flow_state.add_feature(self.feature_name_input, self.description_input)

        else: 
            feature_flow_state = await self.get_state(FeatureFlowState)
            saved = feature_flow_state.save_feature(self.feature_id, self.feature_name_input, self.description_input)
            if saved == False: 
                print("--- MISTAKE IN SAVE_FEATURE LOGIC LOOP ---")


    async def remove_feature(self): 
        if self.feature_id != None:
            feature_flow_state = await self.get_state(FeatureFlowState)
            removed = feature_flow_state.remove_feature(self.feature_id)

            if removed: 
                self.feature_id = None 
                self.feature_name_input = ""
                self.description_input = ""



    @classmethod
    def get_component(cls, **props):
        value = props.pop("value", 0)
        # on = props.pop("on", True)        

        cls.set_component_id(value)


        

         
                
        return rx.card(
       
                    rx.flex(
                        rx.input(
                            value = cls.feature_name_input,
                            placeholder="Feature Name", 
                            on_change= cls.set_feature_name_input,  # Store input in feature_name_input state
                        ),
                        
                        # Text area for Feature Description
                        rx.text_area(
                            value = cls.description_input,
                            placeholder="Describe your feature…",
                            on_change=cls.set_description_input,  # Store input in description_input state
                        ),

                        # Grid for buttons
                        rx.grid(
                            rx.button( 
                                "Save",
                                on_click=cls.save_feature,

                                style=button_style_save,
                                # class_name=default_class_name
                                # + " "
                                # + variant_styles["primary"]["class_name"]
                                # + " "
                                # + get_variant_class("indigo"),
                            ),  
                            rx.button(
                                "Remove", 
                                on_click=cls.remove_feature,

                                # variant="surface",

                                style=button_style_remove,
                                # class_name=default_class_name
                                # + " "
                                # + variant_styles["destructive"]["class_name"]
                                # + " "
                                # + get_variant_class("red"),
                            ),
                            
                            columns="2",
                            spacing="2",
                        ),
                        direction="column",
                        spacing="3",

                            
                    ),
                    width="50%",
                    
                )

        


# class FeatureCardManager(rx.State): 
#     card_1_on: bool = True 

#     def turn_card_1_off(self): 
#         self.card_1_on = False

#     @rx.var
#     def get_card_1_on(self) -> bool: 
#         return self.card_1_on
    




feature_card = create_feature_card.create 

feature_card_1 = create_feature_card.create
feature_card_2 = create_feature_card.create 
feature_card_3 = create_feature_card.create 
feature_card_4 = create_feature_card.create 
feature_card_5 = create_feature_card.create 







def feature_list_view() -> rx.Component:

    return rx.vstack(

        

        ########
        rx.heading("Create your features"),
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
        

        
        feature_card_1(),
        feature_card_2(),
        feature_card_3(),
        feature_card_4(),
        feature_card_5(),

        

        rx.button(
            "+",
            style=button_style,
            background="#c2fbd7",
            color="black",
            width="100px"
                              
        ),

        rx.cond(
            FeatureFlowState.features,  # This condition checks if the list is not empty
            rx.vstack(
                rx.foreach(
                    FeatureFlowState.features,
                    lambda feature: rx.text(feature.feature_name + feature.description), 
                )
            ),
            rx.text("No features available")  # This will be displayed if the list is empty
        ),


        rx.button( 
            "Remove all Features",
            on_click=FeatureFlowState.remove_all_features,
            style=button_style_remove,
            # class_name=default_class_name
            # + " "
            # + variant_styles["primary"]["class_name"]
            # + " "
            # + get_variant_class("red"),
                    
        ),
        rx.button(
            "Generate Features",
            on_click=FeatureFlowState.run_code_gen_and_execution_parent,
            style=button_style_save,
            # class_name=default_class_name
            #     + " "
            #     + variant_styles["primary"]["class_name"]
            #     + " "
            #     + get_variant_class("indigo"),
            margin_bottom="60px",
        ),

    
        spacing="4",
        width="100%",

)






















