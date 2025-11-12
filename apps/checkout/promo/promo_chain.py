from .handlers import (
    PromoActiveHandler,
    PromoExpiredHandler
)

class PromoValidationChain:
    """Orchestrates promo validation handlers."""

    def __init__(self):
        handlers = [
            PromoActiveHandler,
            PromoExpiredHandler
        ]
    
        self.chain = None
        for handler_class in handlers:
            self.chain = handler_class(next_handler=self.chain)
    
    def validate(self, context):
        return self.chain.handle(context)