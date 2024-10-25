

import reflex as rx
from ..backend.feature_flow_state import FeatureFlowState

class MLConfigState(rx.State):
    problem_type: str = "Classification"
    prediction_target: str = "brand"
    evaluation_metric: str = "R-Squared"
    training_framework: str = "XGBoost"

 

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
                ["Classification", "Regression"],
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
            rx.select(
                ["brand", "model", "model_year", "milage", "fuel_type", "engine", "transmission", "price"],
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
                rx.icon("chevrons-right-left",  color="#6439FF"),
                rx.heading("Evaluation Metric", size="5"),
                align="center",
            ),
            rx.select(
                ["Accuracy", "F1 Score","R-sqared", "Log Loss", "Precision", "ROC/AUC", "MSE", "MAE"],
                placeholder="Evaluation Metric",
                label="Evaluation Metric",
                value=FeatureFlowState.evaluation_metric,
                on_change=FeatureFlowState.set_evaluation_metric,
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
                ["XGBoost", "LightGBM", "Scikit-learn", "Random Forest"],
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
        rx.text(
            FeatureFlowState.get_ml_options,
        ),
        spacing="4",
        width="100%",

    )

