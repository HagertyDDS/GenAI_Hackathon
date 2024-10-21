
import reflex as rx
from .button_stuff import default_class_name, variant_styles, get_variant_class
from ..backend.feature_flow_state import FeatureFlowState

class MLConfigState(rx.State):
    problem_type: str = "Classification"
    prediction_target: str = "brand"
    evaluation_metric: str = "R-Squared"
    training_framework: str = "XGBoost"



# Assuming you've already handled the imports
# Assuming 'FeatureFlowState' is already defined in your backend

class create_feature_card(rx.ComponentState):
    # State for the input fields
    feature_name_input: str = "this is a feature name"
    description_input: str = "this is a feature desc"


    def add_feature(self):
        print("calling add feature...")
        all_features = FeatureFlowState.add_feature(self.feature_name_input, self.description_input)
        print("all feats")
        print(all_features)



    @classmethod
    def get_component(cls, **props):
        return rx.card(
            rx.flex(
                # Input for Feature Name
                rx.input(
                    value = cls.feature_name_input,
                    placeholder="Feature Name", 
                    on_change= cls.set_feature_name_input,  # Store input in feature_name_input state
                ),
                
                # Text area for Feature Description
                rx.text_area(
                    placeholder="Describe your feature…",
                    on_change=cls.set_description_input,  # Store input in description_input state
                ),

                # Grid for buttons
                rx.grid(
                    rx.button(
                        "Remove", 
                        # variant="surface",
                        class_name=default_class_name
                        + " "
                        + variant_styles["destructive"]["class_name"]
                        + " "
                        + get_variant_class("red"),
                    ),
                    rx.button( 
                        "Create",
                        class_name=default_class_name
                        + " "
                        + variant_styles["primary"]["class_name"]
                        + " "
                        + get_variant_class("indigo"),
                        on_click=cls.add_feature
                    ),  # Calls add_feature on Create button click
                ),
                    columns="2",
                    spacing="2",
            ),
                direction="column",
                spacing="3",
        )

feature_card = create_feature_card.create 

def feature_list_view() -> rx.Component:
    return rx.vstack(
        rx.heading("Create your features"),
        rx.divider(width="100%"),

        # rx.card(
        #     rx.flex(
        #         rx.input(
        #             placeholder="Feature Name"
        #             on_change=feature_name_input.set_value,
        #         ),

        #         rx.text_area(placeholder="Describe your feature…"),
             
        #         rx.grid(
        #             rx.button(
        #                 "Remove", 
        #                 # variant="surface",
        #                 class_name=default_class_name
        #                 + " "
        #                 + variant_styles["destructive"]["class_name"]
        #                 + " "
        #                 + get_variant_class("red"),
        #             ),
        #             rx.button( 
        #                 "Create",
        #                 class_name=default_class_name
        #                 + " "
        #                 + variant_styles["primary"]["class_name"]
        #                 + " "
        #                 + get_variant_class("indigo"),
                              
        #             ),
        #             columns="2",
        #             spacing="2",
        #         ),
        #         direction="column",
        #         spacing="3",
        #     ),
        #     width="50%",
        # ),
        feature_card(),
        rx.card(
            rx.flex(
                rx.input(placeholder="Feature Name"),

                rx.text_area(placeholder="Describe your feature…"),
                rx.flex(
                    rx.text("Attach screenshot?", size="2"),
                    rx.switch(size="1", default_checked=True),
                    justify="between",
                ),
                rx.grid(
                    rx.button(
                        "Remove", 
                        # variant="surface",
                        class_name=default_class_name
                        + " "
                        + variant_styles["destructive"]["class_name"]
                        + " "
                        + get_variant_class("red"),
                    ),
                    rx.button( 
                        "Create",
                        class_name=default_class_name
                        + " "
                        + variant_styles["primary"]["class_name"]
                        + " "
                        + get_variant_class("indigo"),
                              
                    ),
                    columns="2",
                    spacing="2",
                ),
                direction="column",
                spacing="3",
            ),
            width="50%",
        ),
        rx.button(
            "+",
            class_name=default_class_name
            + " "
            + variant_styles["success"]["class_name"]
            + " "
            + get_variant_class("green"),
                              
        ),

        

        spacing="4",
        width="100%",

    )

