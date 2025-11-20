from .repositories import CheckoutRepository
from ..cart.cart import Cart
from .cart_validation.cart_chain import CartValidationChain

class CheckoutService:
    """
        Service for handling the checkout process in an e-commerce platform.

        This class orchestrates the complete checkout flow including:
            - Validating cart contents
            - Applying promotions and discounts
            - Creating orders
            - Sending confirmation emails

        Attributes:
            repo : (CheckoutRepository): Single source of truth for all checkout data.

            
    """
    def __init__(self):
        """
        Initialize service with repository dependency.
        """
        self.repo = CheckoutRepository()
        self.validation_chain = CartValidationChain()
    
    def cart_validation(self, cart : Cart):
        """
        Responsible for cart validation rules.

        """ 
        validated_cart = self.validation_chain.validate(cart)
        return validated_cart
