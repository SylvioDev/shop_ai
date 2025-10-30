from .repositories import UserRepository

class CheckoutService:
    def __init__(self):
        self.repository = UserRepository()
    
    def get_user_credentials(self, user_id : int):
        user = self.repository.retrieve_user(user_id)
        return {
            'username' : user.username,
            'first_name' : user.first_name,
            'last_name' : user.last_name,
            'email' : user.email,
            
        }
    