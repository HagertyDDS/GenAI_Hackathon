
import reflex as rx

from ..templates import template

from ..views.data_lists.ml_spec_data_list import ml_spec_data_list
from ..views.data_lists.ml_base_results_data_list import ml_base_results_data_list
from ..views.data_lists.ml_final_results_data_list import ml_final_results_data_list

from ..views.button_stuff import default_class_name, variant_styles, get_variant_class, button_style



from .. import styles

from ..backend.feature_flow_state import FeatureFlowState



def results_view() -> rx.Component:
    """The last page.

    Returns:
        The UI for the results page.
    """

    return rx.vstack(

        rx.heading("Models"),
        rx.divider(),

        


        rx.hstack(

            rx.box(
                rx.vstack(
                    rx.heading("Base Dataset"),
                    rx.heading(FeatureFlowState.get_main_base_ml_metric),
                    # rx.heading(FeatureFlowState.get_ml_eval_met),

                    rx.heading('r2'),
                    # rx.progress(value=55),

                    # rx.hstack(
                    #     rx.heading("55%"),
                    #     rx.heading("55%"),
                    #     rx.heading("55%"),
                    # ),
                    rx.button(
                        "Export",
                        on_click=rx.download(
                            url="/models/base_model.pkl",
                        ),
                        style=button_style,
                    ),

                    rx.hstack(
                        ml_spec_data_list(),
                        ml_base_results_data_list(),
                    ),
                    

                    align="center",



                ), 
                # background_color=rx.color("gray", 2),
                background_color='#F5EFFF',
                border_bottom=styles.border,
                border_top=styles.border,
                border_left=styles.border,
                border_right=styles.border,
                border_radius="20px",
                padding="30px",

                    
            ),
            rx.box(
                rx.vstack(
                    rx.heading("FeatureFlow Dataset"),
                    rx.heading(FeatureFlowState.get_main_revised_ml_metric),
                    # rx.heading(FeatureFlowState.get_ml_eval_met),
                    rx.heading('r2'),
                    
                    # rx.progress(value=87),

                    # rx.hstack(
                    #     rx.heading("55%"),
                    #     rx.heading("55%"),
                    #     rx.heading("55%"),
                    # ),
                    rx.button(
                        "Export",
                        on_click=rx.download(
                            url="/models/revised_model.pkl",
                        ),
                        style=button_style,
                    ),

                    rx.hstack(
                        ml_spec_data_list(),
                        ml_final_results_data_list(),
                    ),

                    align="center",
                ),
                # background_color=rx.color("gray", 2),

                background_color='#F5EFFF',
                border_bottom=styles.border,
                border_top=styles.border,
                border_left=styles.border,
                border_right=styles.border,
                border_radius="20px",
                padding="30px",
                border_color="#6439FF"

            ),

        justify="center",
        align="center",
        spacing="4",
        #height="100vh",
        width="100%",
        margin_top="50px",
        
        ),

        # rx.box(
        #         rx.vstack(
        #             rx.text("Base Model Metrics: "),
        #             rx.text(
        #                 FeatureFlowState.get_base_ml_metrics
        #             ),
        #             margin_bottom="15px",
        #         ),
        #         rx.vstack(
        #             rx.text("Revised Model Metrics: "),
        #             rx.text(
        #                 FeatureFlowState.get_revised_ml_metrics
        #             ),
        #             margin_bottom="15px",
        #         ),
        # ),

        
        padding="40px",
    )