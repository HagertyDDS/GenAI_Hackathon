import reflex as rx

class FeatureCardManager(rx.State): 
    card_1_on: bool = True 

    def turn_card_1_off(self): 
        self.card_1_on = False

    # @rx.var
    # def get_card_1_on(self) -> bool: 
    #     if self.card_1_on: 
    #         return 1
    #     return 0
        # return self.card_1_on
