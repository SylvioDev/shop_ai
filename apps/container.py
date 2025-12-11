#### Used for depedency injection in services ####

class ServiceContainer:
    def __init__(self):
        # All repositories and services
        # Checkout init
        self._checkout_repo = None
        self._payment_service = None
        self._checkout_service = None
        self._cart_validation = None
        # Product init
        self._product_repo = None
        self._product_service = None
        # User init
        self._user_repo = None
        self._signup_repo = None
        self._login_repo = None
        self._user_service = None
        self._login_service = None
        self._signup_service = None
        
    
    # Checkout app
    @property
    def checkout_repo(self):
        if self._checkout_repo is None:
            from apps.checkout.repositories import CheckoutRepository
            self._checkout_repo = CheckoutRepository()
        return self._checkout_repo
    
    @property
    def checkout_service(self):
        if self._checkout_service is None:
            from apps.checkout.services import CheckoutService
            self._checkout_service = CheckoutService(self.checkout_repo)
        return self._checkout_service
    
    @property
    def payment_service(self):
        if self._payment_service is None:
            from apps.checkout.payment_service import StripePaymentService
            self._payment_service = StripePaymentService(self.checkout_repo)
        return self._payment_service
    
    @property
    def cart_validation(self):
        if self._cart_validation is None:
            from apps.checkout.cart_validation.cart_chain import CartValidationChain
            self._cart_validation = CartValidationChain()
        return self._cart_validation
    
    # Product app
    @property
    def product_repo(self):
        if self._product_repo is None:
            from apps.products.repositories import ProductRepository
            self._product_repo = ProductRepository()
        return self._product_repo
    
    @property
    def product_service(self):
        if self._product_service is None:
            from apps.products.services import ProductService
            self._product_service = ProductService(self.product_repo)
        return self._product_service
    
    # User app
    @property
    def user_repo(self):
        if self._user_repo is None:
            from apps.users.repositories import UserRepository
            self._user_repo = UserRepository()
        return self._user_repo

    @property
    def signup_repo(self):
        if self._signup_repo is None:
            from apps.users.repositories import SignupRepository
            self._signup_repo = SignupRepository()
        return self._signup_repo
    
    @property
    def login_repo(self):
        if self._login_repo is None:
            from apps.users.repositories import LoginRepository
            self._login_repo = LoginRepository()
        return self._login_repo
    
    @property
    def user_service(self):
        if self._user_service is None:
            from apps.users.services import UserService
            self._user_service = UserService(self.user_repo)
        return self._user_service
    
    @property
    def signup_service(self):
        if self._signup_service is None:
            from apps.users.services import SignupService
            self._signup_service = SignupService(self.signup_repo)
        return self._signup_service
    
    @property
    def login_service(self):
        if self._login_service is None:
            from apps.users.services import LoginService
            self._login_service = LoginService(self.login_repo)
        return self._login_service
    
container = ServiceContainer()

"""
# Checkout app 
        self._checkout_repo = CheckoutRepository()
        self._checkout_service = CheckoutService(self._checkout_repo)
        self._payment_service = StripePaymentService(self._checkout_repo)
        self.card_validation = CartValidationChain()

        # Product app
        self.product_repo = ProductRepository()
        self.product_service = ProductService(self.product_repo)
        
        # Users app
        self.user_repo = UserRepository()
        self.signup_repo = SignupRepository()
        self.login_repo = LoginRepository()
        # services
        self.user_service = UserService(self.user_repo)
        self.signup_service = SignupService(self.signup_repo)
        sself.login_service = LoginService(self.login_repo)
        
"""
