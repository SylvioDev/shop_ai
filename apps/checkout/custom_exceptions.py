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