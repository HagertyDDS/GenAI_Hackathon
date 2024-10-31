import reflex as rx

from ...backend.feature_flow_state import FeatureFlowState

def ml_base_results_data_list() -> rx.Component:
    return(
        rx.card(
            rx.data_list.root(
                rx.data_list.item(
                    rx.data_list.label("RMSE"),
                    rx.data_list.value(FeatureFlowState.get_base_rmse),
                ),
                rx.data_list.item(
                    rx.data_list.label("MAE"),
                    rx.data_list.value(FeatureFlowState.get_base_mae),
                ),
                rx.data_list.item(
                    rx.data_list.label("MAPE"),
                    rx.data_list.value(FeatureFlowState.get_base_mape),
                    #align="center",
                ),
                # rx.data_list.item(
                #     rx.data_list.label("Training Framework"),
                #     rx.data_list.value(FeatureFlowState.training_framework),

                # ),
                
            ),
        ),
    )