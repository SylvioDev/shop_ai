from django.contrib.auth.models import User
from apps.users.models import Address
from .models import PromoCode
class CheckoutRepository:
    def retrieve_code(self, promo_code : str):
        output = PromoCode.objects.get(code=promo_code)
        return output


