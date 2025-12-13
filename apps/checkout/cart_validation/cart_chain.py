from apps.cart.cart import Cart
from .cart_handlers import (
    EmptyCartHandler,
    OutOfStockHandler
)
class CartValidationChain:
    """
    Orchestrates cart validation handlers.
    """
    def __init__(self):
        handlers = [
            EmptyCartHandler,
            OutOfStockHandler
        ]
        self.chain = None
        for handler_class in reversed(handlers):
            self.chain = handler_class(next_handler=self.chain)
        
    def validate(self, cart : Cart):
        return self.chain.handle(cart)

