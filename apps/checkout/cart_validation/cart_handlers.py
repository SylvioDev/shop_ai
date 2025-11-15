from apps.cart.cart import Cart
from apps.products.repositories import ProductRepository
from apps.checkout.cart_validation.cart_exceptions import (
    EmptyCartError,
    OutOfStockError
)
class BaseHandler:
    def __init__(self, next_handler=None):
        self.next_handler = next_handler

    def handle(self, cart : Cart):
        if self.next_handler:
            return self.next_handler.handle(cart)
        return cart
    
class EmptyCartHandler(BaseHandler):
    def handle(self, cart : Cart):
        if len(cart.cart) == 0:
            raise EmptyCartError()
    
        return super().handle(cart)

class OutOfStockHandler(BaseHandler):
    def handle(self, cart : Cart):
        # Check for stock availability
        invalid_products = []
        for item in cart.cart.values():
            product_quantity = item.get('quantity')
            product_sku = str(item.get('sku')).strip()
            product_dict = ProductRepository().get_by_sku(product_sku)
            product = product_dict.get('product')
            data = {
                'product_name' : item.get('title'),
                'stock_quantity' : product.stock
            }
            if int(product_quantity) > product.stock:
                invalid_products.append(data)
                message = 'There was an issue with your payment.'
                for product in invalid_products:
                    message += f"\n Not enough stock for \"{product.get('product_name')}\" . Only {product.get('stock_quantity')} left."
        
                raise OutOfStockError(message)
            else:
                return super().handle(cart)