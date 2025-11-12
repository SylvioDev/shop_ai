from datetime import datetime
from .custom_exceptions import (
    PromoCodeExpiredError,
    PromoCodeInactiveError,
    PromoCodeNotFoundError
)
from typing import (
    Dict
)

class BaseHandler:
    def __init__(self, next_handler=None):
        self.next_handler = next_handler
    
    def handle(self, context):
        if self.next_handler:
            return self.next_handler.handle(context)
        return context
    
class PromoExpiredHandler(BaseHandler):
    def handle(self, context):
        promo = context.get('promo')
        now = datetime.now().date()
        
        if now > promo.valid_to:
            raise PromoCodeExpiredError(self.promo.code)

        return super().handle(context)

class PromoActiveHandler(BaseHandler):
    def handle(self, context : Dict):
        promo = context.get("promo")

        if not promo.is_active:
            raise PromoCodeInactiveError("Promo code is not active.")

        # pass control to next handler
        return super().handle(context)

class PromoExpiredHandler(BaseHandler):
    def handle(self, context : Dict):
        promo = context.get('promo')
        now = datetime.now().date()
        
        if now > promo.valid_to:
            raise PromoCodeExpiredError(self.promo.code)

        return super().handle(context)
        