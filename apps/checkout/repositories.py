from django.contrib.auth.models import User
class UserRepository:
    def retrieve_user(self, user_id) -> User:
        return User.objects.filter(id=user_id)

        
    