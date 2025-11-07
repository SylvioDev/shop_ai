from .promo_repository import PromoRepository
from .promo_repository import PromoCode
from typing import (
    List,
    Dict
)

class InvalidPromoCodeError(Exception):
    def __init__(self, promo_code : str):
        self.message = f"Promo code '{promo_code}' not found"
        super().__init__(self.message)

class PromoService:
    def __init__(self):
        self.repo = PromoRepository()
    
    def check_promo_code(self, promo_code : str) -> Dict:
        """
        Verify and apply a promo code to an in-progress checkout.

        Raises:
            InvalidPromoCodeError if a promo code doesn't exist in the database
        
        """
        try:
            code = self.repo.retrieve_code(promo_code)
        except PromoCode.DoesNotExist:
            raise InvalidPromoCodeError(promo_code)

        return code.discount_value