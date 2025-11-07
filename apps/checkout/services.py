from .repositories import CheckoutRepository
from typing import (
    AnyStr,
    List,
    Dict,
    Bool
)
class CheckoutService:
    """
        Service for handling the checkout process in an e-commerce platform.

        This class orchestrates the complete checkout flow including:
            - Validating cart contents
            - Applying promotions and discounts
            - Processing payment
            - Creating orders
            - Sending confirmation emails

        Attributes:
            repo : (CheckoutRepository): Single source of truth for all checkout data.

        Methods:
            check_promo_code(promo_code : str) : check promo code validity
    """
    def __init__(self):
        """
        Initialize service with repository dependency.
        """
        self.repo = CheckoutRepository()
    
    def check_promo_code(self, promo_code : str) -> Dict:
        """
        Check promotion code validity

        Returns:

        """
        code = self.repo.retrieve_code(promo_code)
        print(code)