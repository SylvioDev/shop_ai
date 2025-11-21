from .repositories import CheckoutRepository
from ..cart.cart import Cart
from .cart_validation.cart_chain import CartValidationChain
from .models import (
    Order,
    Payment
)
from apps.users.models import User
from apps.products.repositories import ProductRepository
import stripe
from datetime import timezone, datetime
from .payment_service import StripePaymentService
from apps.users.repositories import UserRepository
        
class CheckoutService:
    """
        Service for handling the checkout process in an e-commerce platform.

        This class orchestrates the complete checkout flow including:
            - Validating cart contents
            - Applying promotions and discounts
            - Processing payment
            - Creating orders
            - Sending confirmation emails

        Attributes:
            repo : (CheckoutRepository): Single source of truth for all checkout data.

        Methods:
            
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

    def handle_order_status(self, order_number : str, payment_status : str):
        """
        Responsible for updating order status based on payment outcome.

        Args:
            session_id (str): The Stripe session ID associated with the order.
            payment_status (str): The payment status ('success' or 'error').    
        """
        if payment_status == 'success':
            order = self.repo.update_order_status(order_number, 'paid')
        else:
            order = self.repo.update_order_status(order_number, 'canceled')

        return order        
    
    def order_creation(self, cart : Cart, user):
        """
        Responsible for creating an order from the cart.

        Args:
            cart (Cart): The shopping cart to create an order from.
            user: The user placing the order.
        """
        total_price = cart.get_cart_summary().get('total_price')
        subtotal = cart.get_cart_summary().get('subtotal_price')
        order = self.repo.create_order(user, cart.get_cart_summary(), total_price)
        order.cart = cart.cart
        order.save()
        
        return order
    
    def payment_creation(self, order : Order, payment_method : str):
        """
        Responsible for creating a payment record for the order.
        Args:
            order (str): The order associated with the payment.
            payment_method (str): The method of payment.            

        """
        amount = order.total_price
        payment = self.repo.create_payment(order, payment_method, amount)
        return payment
    
    def handle_success_payment_status(self, session, order_id : str, user_id : User):
        """
        Handle payment status for authenticated users.
        """
        # retrieve user's order
        order = CheckoutRepository().retrieve_user_order(order_id, user_id=user_id)
        paid_order = CheckoutRepository().update_order_status(order_id, 'paid')
        payment = Payment.objects.get(order=order.id)
        
        # retrieve stripe payment intent 
        pi = stripe.PaymentIntent.retrieve(session.payment_intent)
        # Update payment model
        payment.transaction_id = pi.latest_charge
        payment.status = 'success'
        payment.amount = session.amount_total
        payment.paied_at = datetime.fromtimestamp(pi.created, tz=timezone.utc)
        payment.method = session.payment_method_types[0]
        payment.stripe_payment_intent_id = session.payment_intent
        payment.save()
    
        payment = Payment.objects.get(order=order.id)
        payment_details = StripePaymentService().payment_details(payment)
        
        # Decrease stock
        cart = order.cart
        for sku, product in cart.items():
            CheckoutRepository().decrease_stock(product_sku=sku, quantity=product.get('quantity'))
        
        return order
        