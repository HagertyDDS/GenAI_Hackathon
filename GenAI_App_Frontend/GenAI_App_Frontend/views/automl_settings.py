

import reflex as rx
from ..backend.feature_flow_state import FeatureFlowState

class MLConfigState(rx.State):
    #problem_type: str = "Classification"
    #prediction_target: str = "brand"
    #evaluation_metric: str = "R-Squared"
    #training_framework: str = "XGBoost"

    columns: list[str] = []

    def set_columns(self, columns: list[str]):
        self.columns = columns


xgboost_options = ['xgboost', 'xgb_limitdepth', 'rf', 'lgbm', 
        'lgbm_spark', 'rf_spark', 'lrl1', 'lrl2', 'catboost', 'extra_tree', 'kneighbor', 'transformer', 'transformer_ms', 'histgb', 
        'svc', 'sgd', 'nb_spark', 'enet', 'lassolars', 'glr_spark', 'lr_spark', 'svc_spark', 'gbt_spark', 'aft_spark']
 

def ml_config_view() -> rx.Component:
    return rx.vstack(
        rx.heading("ML Configuration"),
        rx.divider(width="100%"),

        rx.vstack(
            rx.hstack(
                rx.icon("codesandbox", color="#6439FF"),
                rx.heading("ML Problem Type", size="5"),
                align="center",
            ),
            rx.select(
                ["classification", "regression"],
                placeholder="ML Problem Type",
                label="ML Problem Type",
                value=FeatureFlowState.ml_problem_type,
                on_change=FeatureFlowState.set_ml_problem_type,
                color="#6439FF",
                radius="full",
                width="50%",
                # variant="soft",

            ),
            width="100%",
            margin_bottom="30px"
        ),
        rx.vstack(
            rx.hstack(
                rx.icon("crosshair",  color="#6439FF"),
                rx.heading("Prediction Target", size="5"),
                align="center",
            ),
            # rx.select(
            #     ["brand", "model", "model_year", "milage", "fuel_type", "engine", "transmission", "price"],
            #     #milage	fuel_type	engine	transmission	price
            #     placeholder="Prediction Target",
            #     label="Prediction Target",
            #     value=FeatureFlowState.target_var,
            #     on_change=FeatureFlowState.set_target_var,
            #     default_value="brand",
            #     color="#6439FF",
            #     radius="full",
            #     width="50%",
            # ),
            rx.select(
                MLConfigState.columns,
                #milage	fuel_type	engine	transmission	price
                placeholder="Prediction Target",
                label="Prediction Target",
                value=FeatureFlowState.target_var,
                on_change=FeatureFlowState.set_target_var,
                default_value="brand",
                color="#6439FF",
                radius="full",
                width="50%",
            ),
            width="100%",
            margin_bottom="30px"
        ),

        rx.vstack(
            
            rx.hstack(
                rx.icon("cpu", color="#6439FF"),
                rx.heading("Training Framework", size="5"),
                align="center",
            ),
            rx.select(
                # ["xgboost", "xgb_limitdepth", "lgbm", "rf", "lgbm_spark", "rf_spark"],
                xgboost_options,
   
                placeholder="Training Framework",
                label="Training Framework",
                value=FeatureFlowState.training_framework,
                on_change=FeatureFlowState.set_training_framework,
                color="#6439FF",
                radius="full",
                width="50%",
            ),
            width="100%",
            margin_bottom="30px"

        ),
        # rx.text(
        #     FeatureFlowState.get_ml_options,
        # ),
        spacing="4",
        width="100%",
        padding="40px",

    )

