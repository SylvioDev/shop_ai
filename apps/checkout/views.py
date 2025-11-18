from django.shortcuts import render
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.generic.detail import DetailView
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.http import require_POST
import stripe
from apps.cart.cart import Cart

from apps.users.services import UserService
from .services import CheckoutService
from .cart_validation.cart_exceptions import (
    EmptyCartError,
    OutOfStockError
)

@login_required
def home(request):
    user = request.user
    cart = Cart.from_request(request)
    return render(
        request, 
        'checkout.html', 
        {
            'cart' : cart.cart, 
            'count' : len(cart),
            'cart_summary' : cart.get_cart_summary(),
            'user' : user,
            'user_address' : UserService().get_user_address(user.id)
        }
    )

def payment_status(request):
    cart = Cart.from_request(request)
    return render(
        request, 
        'payment_status.html', 
        {
            'count' : len(cart)
        }
    )

def review_cart(request):
    cart = Cart.from_request(request)
    try:
        cart_validation = CheckoutService().cart_validation(cart)
        
        return JsonResponse({
            'status':'success',
            'message' : 'ok lesy eee',
        })
    except (EmptyCartError, OutOfStockError) as error:
        return JsonResponse({'status':'error', 'error': str(error)})

stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def create_checkout_session(request):
    cart = Cart.from_request(request)
    
    if cart.cart is {}:
        return HttpResponseBadRequest("Cart is empty")  
    
    line_items = []
    
    for item_id, item_data in cart.cart.items():
        line_items.append({
            # DO NOT put 'currency' here!
            'price_data': {
                'currency': 'usd',  # <--- CURRENCY MUST BE HERE
                'product_data': {
                    'name': item_data.get('title'),
                },
                'unit_amount': int(float(item_data.get('price')) * 100), # Price in cents
            },
            'quantity': 1,
        })
    # int(float(item_data.get('price')) * 100)
    
    try:
        # Create the checkout session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=settings.DOMAIN_URL + 'checkout/success/',
            cancel_url=settings.DOMAIN_URL + 'checkout/cancel/',
            metadata={
                'user_id' : request.user.id
            }
        )
    
        return redirect(checkout_session.url, code=303)
    except Exception as error:
        return JsonResponse({'error': str(error)})

@require_POST
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    event = None

    # 1. Verify the signature to ensure the request is actually from Stripe
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        return HttpResponse(status=400) # Invalid payload
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400) # Invalid signature

    # 2. Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        
        # Retrieve the metadata you passed in step 2
        user_id = session.get('metadata', {}).get('user_id')
        
        # TODO: Fulfill the order here
        # e.g., Empty the user's cart, mark order as paid in DB, send email
        print(f"Payment success for user {user_id}!")

    return HttpResponse(status=200)

def success(request):
    return JsonResponse({'status':'success', 'message':'Payment succeeded!'})

def cancel(request):
    return JsonResponse({'status':'canceled', 'message':'Payment canceled by user.'})


"""class PaymentInitView(DetailView):
    template_name = 'payment.html'

    def get(self, request):
        cart = Cart.from_request(request)
        cart_summary = cart.get_cart_summary()
        context = {
            'count' : len(cart.cart),
            'subtotal' : cart_summary.get('subtotal_price'),
            'vat_rate' : 20,
            'vat_total' : cart_summary['taxes'],
            'shipping_fee' : cart_summary['shipping_fee'],
            'total' : cart_summary.get('total_price'),
            
        }
        return render(
            request,
            self.template_name,
            context=context
        )
"""    
    
        
