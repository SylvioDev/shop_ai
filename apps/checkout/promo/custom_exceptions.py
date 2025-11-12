class PromoCodeNotFoundError(Exception):
    def __init__(self, promo_code : str):
        self.message = f'Promo code "{promo_code}" not found'
        super().__init__(self.message)

class PromoCodeExpiredError(Exception):
    def __init__(self, promo_code : str):
        self.message = f'Promo code "{promo_code}" has expired.'

class PromoCodeInactiveError(Exception):
    def __init__(self, promo_code : str):
        self.message = f'Promo code "{promo_code}" is not active.'
