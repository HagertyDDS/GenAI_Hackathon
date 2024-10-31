"""The first page."""


import reflex as rx
import time 

from ..templates import template
from ..views.color_picker import primary_color_picker, secondary_color_picker
from ..views.radius_picker import radius_picker
from ..views.scaling_picker import scaling_picker
from ..views.csv_upload import csv_upload_view
# from ..views.table import main_table
from ..views.csv_table import main_table
from ..views.upload_and_table import editable_text_example
from ..views.upload_csv import upload_csv
from ..views.pdf_upload import index as pdf_upload
from ..views.automl_settings import ml_config_view as automl_settings
from ..views.db_connection import database_connection
from ..views.feature_list import feature_list_view
from ..views.results_view import results_view
from ..views.column_null_options import base_null_options, final_null_options

from .landing.index import index as hero

from .. import styles


from ..views.input_path import base_dataset_input
from ..views.input_path_v2 import base_datatable_v2
from ..views.input_path_v3 import base_datatable_v3

from ..views.button_stuff import default_class_name, variant_styles, get_variant_class, button_style, button_style_save
from ..views.feature_datatable import feature_datatable
from ..views.feature_datatable_v2 import feature_datatable_v2

from ..views.feature_list_v2 import feature_list_v2




# Backend imports 
from ..backend.feature_flow_state import FeatureFlowState


# state 
from ..views.page_1_state import Page1State





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
                            "Gen-AI",
                            margin_bottom="0px",
                            padding_bottom="0px",
                            line_height="unset",
                        ),
                        rx.text(
                            "Feature Building",
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
                
                background_color=rx.color("gray", 2),
                border_bottom=styles.border,
                border_top=styles.border,
                border_left=styles.border,
                border_right=styles.border,
                width="100%",
                margin_bottom="50px",
                border_radius="20px",
            ),

            rx.cond(
                Page1State.database_conn_loaded,
                rx.box(
                    base_datatable_v3(),

                    background_color=rx.color("gray", 2),
                    border_bottom=styles.border,
                    border_top=styles.border,
                    border_left=styles.border,
                    border_right=styles.border,
                    width="100%",
                    margin_bottom="50px",
                    border_radius="20px",
                ),
            ),

            ######

            rx.box(
                base_null_options(),
                

                background_color=rx.color("gray", 2),
                border_bottom=styles.border,
                border_top=styles.border,
                border_left=styles.border,
                border_right=styles.border,
                width="100%",
                margin_bottom="50px",
                border_radius="20px",
            ), 

            ######


            rx.cond(
                Page1State.base_datatable_loaded,
                rx.box(
                    automl_settings(),
                    background_color=rx.color("gray", 2),
                    border_bottom=styles.border,
                    border_top=styles.border,
                    border_left=styles.border,
                    border_right=styles.border,
                    width="100%",
                    margin_bottom="50px",
                    border_radius="20px",
                ),
            ),

            rx.cond(
                Page1State.base_datatable_loaded,
                rx.box(
                    feature_list_v2(),
                    background_color=rx.color("gray", 2),
                    border_bottom=styles.border,
                    border_top=styles.border,
                    border_left=styles.border,
                    border_right=styles.border,
                    width="100%",
                    margin_bottom="50px",
                    border_radius="20px",
                ),
            ),
            


            


            # rx.cond(
            #     Page1State.base_datatable_loaded,
            #     rx.button(
            #             "Test Generate Features (with set Feature values)",
            #             on_click=[Page1State.set_test_generate_features_loading, Page1State.test_generate_features],
            #             loading=Page1State.test_generate_features_loading,
            #             disabled=Page1State.test_generate_features_loading,
            #             # style=button_style,
            #             style=button_style_save,
            #             background='rgba(51, 51, 51, 0.05)',
            #             color='black'
            #     ),
            # ),

            rx.cond(
                Page1State.features_generated,
                rx.box(
                    feature_datatable_v2(),
                    background_color=rx.color("gray", 2),
                    border_bottom=styles.border,
                    border_top=styles.border,
                    border_left=styles.border,
                    border_right=styles.border,
                    width="100%",
                    margin_bottom="50px",
                    border_radius="20px",
                ),
            ),
            
            ######

            rx.box(
                final_null_options(),
                background_color=rx.color("gray", 2),
                border_bottom=styles.border,
                border_top=styles.border,
                border_left=styles.border,
                border_right=styles.border,
                width="100%",
                margin_bottom="50px",
                border_radius="20px",
            ), 

            ######


            # rx.button(
            #     "Build Model",
            #     on_click=FeatureFlowState.run_auto_ml_process,
            #     style=button_style,

            #     # class_name=default_class_name
            #     #     + " "
            #     #     + variant_styles["primary"]["class_name"]
            #     #     + " "
            #     #     + get_variant_class("indigo"),
            #     margin_bottom="60px",
            #     width="20%",
            # ),
            rx.cond(
                Page1State.features_generated,
                rx.button(
                    "Build Model",
                    on_click=[Page1State.set_auto_ml_loading, Page1State.run_auto_ml],
                    loading=Page1State.auto_ml_loading,
                    style=button_style,

                    # class_name=default_class_name
                    #     + " "
                    #     + variant_styles["primary"]["class_name"]
                    #     + " "
                    #     + get_variant_class("indigo"),
                    margin_bottom="60px",
                    width="20%",
                ),
            ),
            
            rx.cond(
                Page1State.results_loaded,
                rx.box(
                    results_view(),
                    background_color=rx.color("gray", 2),
                    border_bottom=styles.border,
                    border_top=styles.border,
                    border_left=styles.border,
                    border_right=styles.border,
                    width="100%",
                    margin_bottom="50px",
                    border_radius="20px",
                ),
            ),
          width="100%",
        ),

        spacing="4",
        #height="100vh",
        width="100%",
    )


