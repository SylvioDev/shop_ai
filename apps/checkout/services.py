from .repositories import UserRepository

class CheckoutService:
    def __init__(self):
        self.repository = UserRepository()
    
    def get_user_credentials(self, user_id : int):
        user = self.repository.retrieve_user(user_id)
        return user

    def get_user_address(self, user_instance):
        user_address = self.repository.retrieve_adress(user_instance)
        return user_address