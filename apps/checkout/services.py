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
from stripe.checkout import Session
        
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
        order = self.repo.create_order(user, cart.get_cart_summary(), total_price)
        order.cart = cart.cart
        order.save()
        return order
    
    def payment_creation(self, order : Order, payment_provider : str):
        """
        Responsible for creating a payment record for the order.
        Args:
            order (str): The order associated with the payment.
            payment_method (str): The method of payment.            

        """
        amount = order.final_total
        payment = self.repo.create_payment(order, payment_provider, amount)
        return payment
    
    def add_order_items(self, order : Order, cart : dict):
        """
        Attach order items to a particular order
        """
        for sku, item in cart.items():
            product_dict = ProductRepository().get_by_sku(item.get('sku'))
            product = product_dict['product']
            total_price = item.get('quantity') * item.get('price')
            order_item = CheckoutRepository().add_order_item(
                order=order,
                product=product,
                product_type=product_dict['product_type'],
                product_name=item.get('title'),
                product_attributes=item.get('attributes', {}),
                unit_price=item.get('price'),
                quantity=item.get('quantity'),
                total_price=total_price,
                img_src=item.get('image')    
            )
        return order_item
    
    def handle_success_payment_status(self, session_id : str, order_id : str, user_id : User):
        """
        Handle a successful Stripe checkout and persist payment/order updates.

        Locate the order owned by the given user and order identifier, mark it paid,
        update the associated Payment record from the Stripe payment intent, decrement
        inventory for each ordered item and return the updated Order
        
        Args:
            session (stripe.checkout.Session): Stripe checkout session (or the webhook
            session object) containing payment_intent, amount_total,
            payment_method_types, currency, etc.
            order_id (str): The order identifier (order number) to update.
            user_id (int | apps.users.models.User): User id or User instance who owns
            the order; used to scope the order lookup.

        Returns:
            apps.checkout.models.Order: The updated order instance (status set to paid).

        Side effects:
            - Calls CheckoutRepository().retrieve_user_order() to fetch the order.
            - Updates order status to 'paid'.
            - Retrieves the Stripe PaymentIntent and updates the corresponding Payment
            model fields (transaction id, status, amount, paid timestamp, method,
            stripe_payment_intent_id, currency) and saves it.
            - Decreases product stock based on quantities recorded in the order's cart.
            - Persists all changes to the database.

        Raises:
            - django.core.exceptions.ObjectDoesNotExist: if the Order or Payment cannot be found.
            - stripe.error.StripeError (or subclasses): on Stripe API failures.
            - Any repository-specific exceptions raised by CheckoutRepository.

        Notes:
            - Amount conversions assume session.amount_total is in cents (divide by 100).
            - Timestamps are converted to UTC.
            - This method performs multiple DB writes; callers may want to run it inside
            a transaction if atomicity is required.
    """
        # retrieve user's order
        order = CheckoutRepository().retrieve_user_order(order_id, user_id=user_id)
        paid_order = CheckoutRepository().update_order_status(order_id, 'paid')
        payment = Payment.objects.get(order=order.id)
        
        # retrieve stripe payment intent 
        session = stripe.checkout.Session.retrieve(session_id)
        pi = stripe.PaymentIntent.retrieve(session.payment_intent)
        # Update payment model
        payment.transaction_id = pi.latest_charge
        payment.status = 'success'
        payment.amount = session.amount_total / 100
        payment.paied_at = datetime.fromtimestamp(pi.created, tz=timezone.utc)
        payment.method = session.payment_method_types[0]
        payment.stripe_payment_intent_id = session.payment_intent
        payment.currency = session.currency.upper()
        payment.stripe_session_id = session.id
        payment.save()
    
        payment = Payment.objects.get(order=order.id)
        payment_details = StripePaymentService().payment_details(payment)
        
        # Decrease stock
        cart = order.cart
        for sku, product in cart.items():
            CheckoutRepository().decrease_stock(product_sku=sku, quantity=product.get('quantity'))
            
        return order
         
    def handle_failure_payment_status(self, order_id : str, user_id : str, error_message : str):
        """
        Handle a failed payment for a given order.
        Update the order and associated payment records when a payment attempt fails. 
        
        This will:
            - Locate the order owned by the given user and order identifier.
            - Mark the order as cancelled and persist the provided failure reason.
            - Update the related payment record status to 'failed' and save it.
        
        Args:
            order_id (str): The order identifier (order number) to update.
            user_id (str | int): Identifier of the user who owns the order.
            error_message (str): Human-readable failure reason to store on the order.
        
        """
        order = CheckoutRepository().retrieve_user_order(order_id, user_id)
        updated_order = CheckoutRepository().update_order_status(order.order_number, 'cancelled')
        updated_order.failure_reason = error_message
        updated_order.save()
        payment = CheckoutRepository().update_payment_status(order.order_number, 'failed')
        payment.save()
    
    def handle_webhook_fallback(self, session_id : str, order_id : str, user_id : str):
        """
        Handle webhook issues. Update database for payment and order when webhook endpoint
        is down. 
        """
        order = Order.objects.get(order_number=order_id)
        payment = Payment.objects.get(order=order)
        updated_payment = CheckoutService().handle_success_payment_status(
                session_id=session_id,
                order_id=order_id,
                user_id=user_id
            )
        payment.refresh_from_db()
        order.refresh_from_db()
        return order, payment

        