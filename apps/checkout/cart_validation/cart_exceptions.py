class EmptyCartError(Exception):
    def __init__(self):
        self.message = "Your cart is empty. Please add some products to continue shopping."
        super().__init__(self.message)

class OutOfStockError(Exception):
    def __init__(self, msg : str):
        self.message = msg
        super().__init__(self.message)

