from apps.cart.cart import Cart
from .repositories import CheckoutRepository
from django.conf import settings
from django.contrib.auth.models import User
from django.http import JsonResponse
import stripe
from .custom_exceptions import (
    InvalidPayloadException,
    InvalidSignatureException
)
import logging
from .models import (
    Order,
    Payment
)
import json

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
        
    def create_session(self, cart : Cart, user : User, order : Order, payment : Payment):
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
                success_url=settings.DOMAIN_URL + f'checkout/success/{order.order_number}',
                cancel_url=settings.DOMAIN_URL + f'checkout/cancel/{order.order_number}',
                metadata={
                        'user_id' : user.id,
                        'order_id' : order.order_number,
                        'payment_id' : payment.id,
                    }
                )
            return checkout_session
        except Exception as error:
            return JsonResponse({'error': str(error)})
    
    def payment_details(self, payment : Payment):
        """
        Retrieve payment details from database
        Args:
            payment (str): The Stripe checkout session ID.
            
        Returns:
            dict: A dictionary containing payment details.
            
        """
        
        transaction_id = payment.transaction_id
        amount_paid = payment.amount / 100  # Convert cents to dollars
        date = payment.paied_at
        payment_method = payment.method
        status = payment.status        
        details = {
            'transaction_id' : transaction_id,
            'amount_paid' : amount_paid,
            'date' : date,
            'payment_method' : payment_method,
            'status' : status
        }
        
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
            # For successful payment
            # Retrieve session variable
            session = event['data']['object']
            order_number = session.get('metadata')['order_id']
            user_id = session.get('metadata')['user_id']
            # local import to avoid circular import with services.py
            from .services import CheckoutService
            CheckoutService().handle_success_payment_status(
                session=session,
                order_id=order_number,
                user_id=int(user_id)
            )
        elif event.type == 'payment_intent.succeeded':
            pass
            #cls.handle_payment_intent_succeeded(event.data.object)
        elif event.type == 'payment_intent.payment_failed':
            pass
            #cls.handle_payment_intent_failed(event.data.object)
        else:
            logger.info(f"Unhandled event type {event.type}")
        
        return event