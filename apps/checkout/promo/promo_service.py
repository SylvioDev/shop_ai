from .promo_repository import PromoRepository
from .promo_chain import PromoValidationChain
from .custom_exceptions import PromoCodeNotFoundError
from ..models import PromoCode

class PromoService:
    def __init__(self):
        self.repo = PromoRepository()
        self.validation_chain = PromoValidationChain()

    def check_promo(self, promo_code : str):
        """
        Validates the promo and calculate discount.

        Returns:
            A dict with the applied discount or raises an error.

        """
        try:
            promo = self.repo.retrieve_code(promo_code)
        except PromoCode.DoesNotExist as error:
            raise PromoCodeNotFoundError(promo_code)

        context = {
            'promo' : promo,
        } 

        validated_context = self.validation_chain.validate(context)
        
        return {
            'promo' : promo,
            'discount' : 20_000
        } 

    #def check_promo_code(self, promo_code : str) -> Dict:
        """
        Verify and apply a promo code to an in-progress checkout.

        Raises:
            InvalidPromoCodeError if a promo code doesn't exist in the database
        
        """
    """    try:
            code = self.repo.retrieve_code(promo_code)
        except PromoCode.DoesNotExist:
            raise PromoCodeNotFoundError(promo_code)

        unit = '%' if code.discount_type == 'percentage' else '$'
        message = f'"{code.code}" discount of {code.discount_value:.0f}{unit} applied !'
        
        return {
            'message' : message,
            'code_value' : code.discount_value
        }
    """