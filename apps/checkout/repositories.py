from django.contrib.auth.models import User
from apps.users.models import Address
class UserRepository:
    def retrieve_user(self, user_id) -> User:
        return User.objects.filter(id=user_id)

    def retrieve_adress(self, user_instance : User):
        user_address = Address.objects.get(user=user_instance)
        return user_address

