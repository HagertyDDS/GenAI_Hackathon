

import reflex as rx
from ..backend.feature_flow_state import FeatureFlowState



class Page1State(rx.State): 

    placeholder: str

    test_generate_features_loading: bool = False
    database_conn_loaded: bool = False

    load_base_dataset_loading: bool = False
    base_datatable_loaded: bool = False

    features_generated: bool = False

    results_loaded: bool = False

    auto_ml_loading: bool = False


    def set_test_generate_features_loading(self): 
        self.test_generate_features_loading = True


    async def test_generate_features(self): 
        
        #result = FeatureFlowState.test_code_gen_and_execution()

        feature_flow_state = await self.get_state(FeatureFlowState)
        result = await feature_flow_state.test_code_gen_and_execution()

        if result: 
            print("Code Gen and Execution Test Passed")

        self.test_generate_features_loading = False 

        self.features_generated = True 

        return 
    
    def set_database_conn_loaded(self, value): 
        self.database_conn_loaded = value

    def set_base_datatable_loaded(self, value): 
        self.base_datatable_loaded = value

    def set_features_generated(self, value): 
        self.features_generated = value

    def set_results_loaded(self, value): 
        self.results_loaded = value


    def set_auto_ml_loading(self): 
        self.auto_ml_loading = True


    async def run_auto_ml(self): 
        feature_flow_state = await self.get_state(FeatureFlowState)
        await feature_flow_state.run_auto_ml_process()

        self.results_loaded = True
        self.auto_ml_loading = False

        return