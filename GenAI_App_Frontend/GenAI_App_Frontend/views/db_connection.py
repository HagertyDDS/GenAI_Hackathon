# Database connection compoenent 

# Host 
# Port 
# Database Name 
# User 
# Password 
# CONNECT BUTTON


import reflex as rx
import time

from .button_stuff import default_class_name, variant_styles, get_variant_class, button_style
from ..backend.feature_flow_state import FeatureFlowState


from .input_path_v3 import DataEditorState

from .page_1_state import Page1State



class DatabaseConnectionForm(rx.ComponentState):
    host: str = ""
    port: str = ""
    database: str = ""
    user: str = ""
    password: str = ""

    server_hostname: str = "dbc-bfc39191-ad8d.cloud.databricks.com"
    http_path: str = "/sql/1.0/warehouses/baca4ffdcd37d0b8"
    catalog: str = "workspace"
    schema: str = "default"

    connect_loading: bool = False


    loaded: bool = False

    def set_loading(self): 
        self.connect_loading = True

    async def connect(self):
        # Implement your database connection logic here
        # self.connect_loading = True 

        feature_flow_state = await self.get_state(FeatureFlowState)
        feature_flow_state.set_server_hostname(self.server_hostname)
        feature_flow_state.set_http_path(self.http_path)
        feature_flow_state.set_catalog(self.catalog)
        feature_flow_state.set_schema(self.schema)

        feature_flow_state2 = await self.get_state(FeatureFlowState)
        tables = feature_flow_state2.get_table_options_from_databricks()

        data_editor_state = await self.get_state(DataEditorState)
        data_editor_state.set_tables(tables)
        data_editor_state.set_tables_ready(True)

        # time.sleep(5)

        page_1_state = await self.get_state(Page1State)
        page_1_state.set_database_conn_loaded(True)

        self.connect_loading = False
        return 

        

    @classmethod
    def get_component(cls, **props):
        return rx.vstack(

            rx.hstack(
                rx.text("Server Hostname"),
                rx.input(
                    on_change=cls.set_server_hostname,
                    value=cls.server_hostname,
                ),
                align="center",
                justify="between",
                width="100%",
            ),
            rx.hstack(
                rx.text("HTTP Path"),
                rx.input(
                    on_change=cls.set_http_path,
                    value=cls.http_path,
                ),
                align="center",
                justify="between",
                width="100%",
            ),
            rx.hstack(
                rx.text("Catalog"),
                rx.input(
                    on_change=cls.set_catalog,
                    value=cls.catalog,
                ),
                align="center",
                justify="between",
                width="100%",
            ),
            rx.hstack(
                rx.text("Schema"),
                rx.input(
                    on_change=cls.set_schema,
                    value=cls.schema,
                ),
                align="center",
                justify="between",
                width="100%",
            ),
            
            rx.button(
                "Connect", 
                on_click=[cls.set_loading, cls.connect],
                loading=cls.connect_loading,
                disabled=cls.connect_loading,
                
                style=button_style,

                margin_top="10px",
                
                
                
            ),
            **props
        )
    
#     <!-- HTML !-->
# <button class="button-34" role="button">Button 34</button>

# /* CSS */
# .button-34 {
#   background: #5E5DF0;
#   border-radius: 999px;
#   box-shadow: #5E5DF0 0 10px 20px -10px;
#   box-sizing: border-box;
#   color: #FFFFFF;
#   cursor: pointer;
#   font-family: Inter,Helvetica,"Apple Color Emoji","Segoe UI Emoji",NotoColorEmoji,"Noto Color Emoji","Segoe UI Symbol","Android Emoji",EmojiSymbols,-apple-system,system-ui,"Segoe UI",Roboto,"Helvetica Neue","Noto Sans",sans-serif;
#   font-size: 16px;
#   font-weight: 700;
#   line-height: 24px;
#   opacity: 1;
#   outline: 0 solid transparent;
#   padding: 8px 18px;
#   user-select: none;
#   -webkit-user-select: none;
#   touch-action: manipulation;
#   width: fit-content;
#   word-break: break-word;
#   border: 0;
# }
    

def database_connection() -> rx.Component:
    return rx.vstack(
        rx.heading("Databricks Unity Catalog Connection"),
        rx.divider(width="100%"),
        DatabaseConnectionForm.create(),

        padding="40px",
    )