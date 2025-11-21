### Stipe Webhook Custom Exceptions ###
class InvalidPayloadException(Exception):
    """Exception raised for invalid payloads from Stripe webhooks."""
    def __init__(self, msg : str):
        self.message = msg
        super().__init__(self.message)

class InvalidSignatureException(Exception):
    """Exception raised for invalid signatures from Stripe webhooks."""
    def __init__(self, msg : str):
        self.message = msg
        super().__init__(self.message)
    
### Checkout Repository Custom Exceptions ###

class OrderNotFoundError(Exception):
    """Exception raised when an order is not found in the repository."""
    def __init__(self, order_id : str):
        self.message = f"Order with ID {order_id} not found."
        super().__init__(self.message)