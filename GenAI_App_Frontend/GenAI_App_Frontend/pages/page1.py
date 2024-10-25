"""The first page."""


from ..templates import template

import reflex as rx
from ..views.color_picker import primary_color_picker, secondary_color_picker
from ..views.radius_picker import radius_picker
from ..views.scaling_picker import scaling_picker
from ..views.csv_upload import csv_upload_view
# from ..views.table import main_table
from ..views.csv_table import main_table
from ..views.upload_and_table import editable_text_example
from ..views.input_path import csv_path_input_example
from ..views.upload_csv import upload_csv
from ..views.pdf_upload import index as pdf_upload
from ..views.automl_settings import ml_config_view as automl_settings
from ..views.db_connection import database_connection
from ..views.feature_list import feature_list_view
from ..views.results_view import results_view

from .landing.index import index as hero

from .. import styles

from ..views.button_stuff import default_class_name, variant_styles, get_variant_class
from ..views.feature_datatable import feature_datatable


# Backend imports 
from ..backend.table_state import TableState
from ..backend.feature_flow_state import FeatureFlowState



class Page1State(rx.State): 

    placeholder: str



@template(route="/", title="Page1")
def page1() -> rx.Component:
    """The first page.

    Returns:
        The UI for the first page.
    """

    return rx.vstack(
        rx.box(
            rx.hstack(
                rx.html(
                    """
                    <iframe src='https://my.spline.design/chips-2f9fd8cec3143149efef3af7a6de074a/' 
                    frameborder='0' width='767px' height='674px'></iframe>
                    """,
                    width="80%",
                    height="100%",
                ),
                
                # Responsive text block with stacked layout
                rx.el.h1(
                    rx.vstack(
                        rx.text(
                            "Gen-AI Powered.",
                            margin_bottom="0px",
                            padding_bottom="0px",
                            line_height="unset",
                        ),
                        rx.text(
                            "Feature Building.",
                            color="#6439FF",
                            margin_top="0px",
                            line_height="unset",
                            font_weight="800",
                        ),
                        rx.text(
                            "For a better ML Model.",
                            line_height="unset",

                        ),
                        spacing="0",

                    ),
                    font_size=["40px", "50px", "60px", "70px"],  # Responsive font sizes
                    class_name="font-xx-large text-blue-500",
                    text_align="left",  # Ensure text is centered
                    justify="left",  # Center horizontally

                ),
                
                justify="left",  # Center horizontally
                align="center",    # Center vertically
                flex_direction=["column", "column", "row"],  # Stack on small screens, horizontal on large screens
                spacing="20px",    # Adjust spacing between elements
            ),
            width="100%",
            padding_bottom="40px",
        ),
        rx.divider(
            width="100%",
            margin_bottom="30px",
            align="center",    # Center vertically
            justify="center",  # Center horizontally


        ),


        ###
        rx.flex(
            rx.image(src="/reflex.png", height="50px"),
            rx.image(src="/box.png", height="50px"),
            rx.image(src="/llamaindex.png", height="50px"),
            rx.image(src="/pinecone.png", height="50px"),
            spacing="2",
            align="center",
            justify="center",
            width="100%",
            margin_bottom="25px"
        ),

        ###

        
        rx.vstack(
            rx.box(
                rx.heading(
                    "Build Your FeatureFlow Model", 
                    size="7",
                    margin_left="20px",
                    margin_right="20px",
                    ),
                background_color=rx.color("gray", 2),
                border_bottom=styles.border,
                border_top=styles.border,
                border_left=styles.border,
                border_right=styles.border,
                


                width="100%",
                padding_top="30px",
                padding_bottom="30px",
                margin_bottom="50px",
                border_radius="20px"

            ),
        
            rx.box(
                database_connection(),
                margin_bottom="60px"
            ),
            rx.box(
                csv_path_input_example(),
                margin_bottom="60px",
            ),
            rx.box(
                automl_settings(),
                margin_bottom="60px",
                width="100%"
            ),
            
            rx.box(
                feature_list_view(),
                margin_bottom="60px",
                width="100%"

            ),
            
            # rx.box(
            #     csv_path_input_example(),
            #     margin_bottom="60px",
            # ),
            

            rx.button(
                "Test AutoML with default vals",
                on_click=FeatureFlowState.run_test_auto_ml_values,
                class_name=default_class_name
                    + " "
                    + variant_styles["primary"]["class_name"]
                    + " "
                    + get_variant_class("indigo"),
                margin_bottom="60px",
            ),
            rx.button(
                "Test Code Gen Chain",
                on_click=FeatureFlowState.test_code_gen_chain,
                class_name=default_class_name
                    + " "
                    + variant_styles["primary"]["class_name"]
                    + " "
                    + get_variant_class("indigo"),
                margin_bottom="60px",
            ),
            rx.button(
                "Test Code Gen Execution",
                on_click=FeatureFlowState.test_code_gen_and_execution,
                class_name=default_class_name
                    + " "
                    + variant_styles["primary"]["class_name"]
                    + " "
                    + get_variant_class("indigo"),
                margin_bottom="60px",
            ),
            rx.box(
                feature_datatable(),
                margin_bottom="60px",
            ),


            rx.button(
                "Run AutoML Process",
                on_click=FeatureFlowState.run_auto_ml_process,
                class_name=default_class_name
                    + " "
                    + variant_styles["primary"]["class_name"]
                    + " "
                    + get_variant_class("indigo"),
                margin_bottom="60px",
            ),
            rx.box(
                rx.vstack(
                    rx.text("Base Model Metrics: "),
                    rx.text(
                        FeatureFlowState.get_base_ml_metrics
                    ),
                    margin_bottom="15px",
                ),
                rx.vstack(
                    rx.text("Revised Model Metrics: "),
                    rx.text(
                        FeatureFlowState.get_revised_ml_metrics
                    ),
                    margin_bottom="15px",
                ),
            ),

            rx.box(
                results_view(),
                margin_bottom="60px",
            ),
          
        ),

        spacing="4",
        #height="100vh",
        width="100%",
    )


