import reflex as rx

from ...backend.feature_flow_state import FeatureFlowState

def ml_spec_data_list() -> rx.Component:
    return(
        rx.card(
            rx.data_list.root(
                rx.data_list.item(
                    rx.data_list.label("ML Problem Type"),
                    rx.data_list.value(
                        rx.badge(
                            FeatureFlowState.ml_problem_type,
                            variant="soft",
                            radius="full",
                        )
                    ),
                    align="center",
                ),
                rx.data_list.item(
                    rx.data_list.label("Prediction Target"),
                    rx.data_list.value(FeatureFlowState.target_var),
                ),
                rx.data_list.item(
                    rx.data_list.label("Evaluation Metric"),
                    rx.data_list.value(FeatureFlowState.evaluation_metric),
                    align="center",
                ),
                rx.data_list.item(
                    rx.data_list.label("Training Framework"),
                    # rx.data_list.value("XGBoost"),
                    rx.data_list.value(FeatureFlowState.training_framework),

                ),
                
            ),
        ),
    )