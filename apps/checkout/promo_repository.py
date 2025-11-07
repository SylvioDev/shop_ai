from .models import PromoCode
class PromoRepository:
    def retrieve_code(self, promo_code : str):
        output = PromoCode.objects.get(code=promo_code)
        if output.is_active:
            return output

        return None
