from apps.cart.cart import Cart
from .repositories import CheckoutRepository
from django.conf import settings
from django.contrib.auth.models import User
from django.http import JsonResponse
import stripe
from .utils import format_timestamp
from .custom_exceptions import (
    InvalidPayloadException,
    InvalidSignatureException
)
import logging

logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_SECRET_KEY

class StripePaymentService:
    """
        Service for handling Stripe payment processing.

        This class manages interactions with the Stripe API including:
            - Creating payment intents
            - Handling webhooks
            - Managing customer data

        Attributes:
            repo : (CheckoutRepository): Single source of truth for all checkout data.

        Methods:
            
    """
    def __init__(self):
        """
        Initialize service with repository dependency.
        """
        self.repo = CheckoutRepository()
        
    
    def create_cart_checkout(self, cart : Cart):
        """
        Responsible for creating Stripe checkout session for the cart.
        
        Args:
            cart (Cart): The shopping cart to create a checkout session for.
        
        Returns:
            list: A list of line items formatted for Stripe checkout session.

        """ 
        line_items = []

        for item_id, item_data in cart.cart.items():
            line_items.append({
                'price_data': {
                    'currency': 'usd',  
                    'product_data': {
                        'name': item_data.get('title'),
                    },
                    'unit_amount': int(float(item_data.get('price')) * 100), # Price in cents
                },
                'quantity': item_data.get('quantity'),
            })
        
        shipping_fee = int(float(cart.get_cart_summary().get('shipping_fee')) * 100)
        vat = int(float(cart.get_cart_summary().get('taxes')) * 100)
        # Shipping_fee as a separate line item
        line_items.append({
            'price_data' : {
                'currency' : 'usd',
                'product_data' : {
                    'name' : 'Shipping Fee'
                },
                'unit_amount' : shipping_fee          
            },
            'quantity' : 1
        })
        line_items.append({
            'price_data' : {
                'currency' : 'usd',
                'product_data' : {
                    'name' : 'VAT'
                },
                'unit_amount' : vat          
            },
            'quantity' : 1
        })
    
        return line_items    
        
    def create_session(self, cart : Cart, user : User):
        """
        Create a Stripe checkout session for the given cart.

        Args:
            cart (Cart): The shopping cart to create a checkout session for.
        
        Returns :
            stripe.checkout.Session: The created Stripe checkout session.
            
        """
        if len(cart.cart) == 0:
            raise ValueError("Cart is empty. Cannot create checkout session.")  
        
        line_items = StripePaymentService().create_cart_checkout(cart)
            
        try:
            # Create the checkout session
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=line_items,
                mode='payment',
                success_url=settings.DOMAIN_URL + 'checkout/success/?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=settings.DOMAIN_URL + 'checkout/cancel/?session_id={CHECKOUT_SESSION_ID}',
                metadata={
                        'user_id' : user.id
                    }
                )
            return checkout_session
        except Exception as error:
            return JsonResponse({'error': str(error)})
    
    def payment_details(self, session_id : str):
        """
        Retrieve payment details from Stripe using the session ID.

        Args:
            session_id (str): The Stripe checkout session ID.
            
        Returns:
            dict: A dictionary containing payment details.
            
        """
        try:
            session = stripe.checkout.Session.retrieve(session_id)

            transaction_id = session.payment_intent
            amount_paid = session.amount_total / 100  # Convert cents to dollars
            date = format_timestamp(session.created)
            payment_method = session.payment_method_types[0]
            status = session.payment_status        
            details = {
                'transaction_id' : transaction_id,
                'amount_paid' : amount_paid,
                'date' : date,
                'payment_method' : payment_method,
                'status' : status
            }
        except stripe.InvalidRequestError as error:
            details = {'error' : str(error)}
            return 'invalid session id'
        
        return details

    @classmethod
    def handle_webhook(cls, payload, sig_header):
        """
        Handle Stripe webhook events.

        Args:
            payload (bytes): The raw payload from the webhook.
            sig_header (str): The signature header from the webhook request.

        Returns:
            stripe.Event: The processed Stripe event.
        """
        # 1 Verify the webhook signature and construct the event
        
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError as e:
            # Invalid payload
            logger.error("Invalid payload received in Stripe webhook.")
            raise InvalidPayloadException("Invalid payload")
            # Invalid signature
        except stripe.error.SignatureVerificationError as e:
            logger.error("Invalid signature in Stripe webhook.")
            raise InvalidSignatureException("Invalid signature")

        # 2 Handle event types as needed
        
        if event.type == 'checkout.session.completed':
            cls.handle_checkout_session_completed(event.data.object)
        elif event.type == 'payment_intent.succeeded':
            cls.handle_payment_intent_succeeded(event.data.object)
        elif event.type == 'payment_intent.payment_failed':
            cls.handle_payment_intent_failed(event.data.object)
        else:
            logger.info(f"Unhandled event type {event.type}")
        
        return event