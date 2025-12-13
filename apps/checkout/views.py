from apps.users.models import User
from django.shortcuts import (
    redirect,
    render
)
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.generic.detail import DetailView
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import stripe
from apps.cart.cart import Cart
from .cart_validation.cart_exceptions import (
    EmptyCartError,
    OutOfStockError
)
from .custom_exceptions import (
    InvalidPayloadException,
    InvalidSignatureException,
)
from apps.container import container
from apps.orders.models import Order
from apps.orders.models import OrderItem

stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def home(request):
    """
    View for the checkout home page.
    """
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
            'user_address' : container.user_service.get_user_address(user_instance=user.id)
        }
    )

def review_cart(request):
    cart = Cart.from_request(request)
    try:
        cart_validation = container.checkout_service.cart_validation(cart)
        return JsonResponse({
            'status':'success',
            'message' : 'cart is valid',
            
        },status=200)
    except (EmptyCartError, OutOfStockError) as error:
        return JsonResponse({'status':'error', 'error': str(error)}, status=400)

@login_required
def payment_processing(request):
    """
    Handle payment processing via Stripe.
    1. Create order and payment records.
    2. Create Stripe checkout session.
    3. Redirect user to Stripe checkout page.
    4. Handle errors appropriately.
    5. Return JsonResponse with error details if any issues arise.
    
    Args:
        request (HttpRequest): The incoming HTTP request.
        
    Returns:
        HttpResponse: Redirect to Stripe checkout or JsonResponse with error.
        
    """ 
    cart = Cart.from_request(request)
    # Order and payment initialization
    order = container.checkout_service.order_creation(cart, request.user)
    payment = container.checkout_service.payment_creation(order=order, payment_provider="stripe")
    checkout_session = container.payment_service.create_session(cart, request.user, order, payment)
    
    if isinstance(checkout_session, str):
        return JsonResponse({'status':'error', 'error': checkout_session}, status=400)
    
    payment.stripe_payment_intent_id = checkout_session.payment_intent
    payment.stripe_session_id = checkout_session.id
    payment.save()
    order.final_total = checkout_session.amount_total / 100
    order.save()
    container.checkout_service.add_order_items(order, cart=cart.cart)

    return redirect(checkout_session.url, code=303)
    
@csrf_exempt
@require_POST
def stripe_webhook(request):
    """
    Handle Stripe webhook events.
    
    Args:
        request (HttpRequest): The incoming HTTP request containing the webhook payload.
    
    Returns:
        HttpResponse: Acknowledgment of the webhook event processing.
         
    """
    payload = request.body
    try:
        event = container.payment_service.handle_webhook(payload, request.META.get('HTTP_STRIPE_SIGNATURE'))
    except InvalidPayloadException as e:
        return JsonResponse({'error':str(e)}, status=400)
    except InvalidSignatureException as e:  
        return JsonResponse({'error':str(e)}, status=400)
    return HttpResponse(status=200)

def success(request):
    order_id = request.GET.get('order_id')
    session_id = request.GET.get('session_id')
    return redirect(f'/checkout/payment_status/?order_id={order_id}&session_id={session_id}')
    
def cancel(request):
    order_id = request.GET.get('order_id')
    session_id = request.GET.get('session_id')
    return redirect(f"/checkout/payment_status/?order_id={order_id}&session_id={session_id}")

@login_required
def payment_status(request):
    """ 
    Handle payment status 
    """
    from apps.container import container
    user = request.user
    order_id = request.GET.get('order_id')
    session_id = request.GET.get('session_id')
    cart = Cart.from_request(request)
    
    checkout_context = container.checkout_service.fetch_checkout_context(session_id, order_id)
    
    if type(checkout_context) == str:
        return JsonResponse({
            'status':'error',
            'error' : checkout_context
        }, status=500)
        
    session = checkout_context[0]
    order, payment = checkout_context[1], checkout_context[2]

    if session.payment_status == 'paid':
        request.session['cart'] = {} # Clear user cart
        cart_len = 0
        if payment.status == 'pending':
            updated_order, updated_payment = container.checkout_service.handle_webhook_fallback(
                session_id=session_id,
                order_id=order_id,
                user_id=user
            )
            order = updated_order
            payment = updated_payment
        return render(
            request, 
            'payment_status.html', 
            {   
                'payment_status' : session.payment_status,
                'count' : cart_len,
                'payment' : payment,
                'order' : order
            }
        )
    else:
        context = {
            'payment' : payment,
            'failure_reason' : order.failure_reason,
            'count' : len(cart)
        }
        return render(
            request,
            'payment_status.html',
            context=context,
            status=500
        )
    
class PaymentConfirmView(DetailView):
    """
    Responsible for handling payment confirmation view.
    """
    template_name = 'confirm.html'
    def get(self, request):
        """
        Handle GET requests for payment confirmation.
        """
        cart = Cart.from_request(request)
        cart_summary = cart.get_cart_summary()
        context = {
            'count' : len(cart.cart),
            'subtotal' : cart_summary.get('subtotal_price'),
            'vat_rate' : 20,
            'vat_total' : cart_summary['taxes'],
            'shipping_fee' : cart_summary['shipping_fee'],
            'total' : cart_summary.get('total_price'),
            'payment_method' : 'Stripe',
            'redirect_url' : redirect('create-checkout-session').url,
            
        }
        return render(
            request,
            self.template_name,
            context=context
        )
    
    def post(self, request):
        """
        Handle POST requests for payment confirmation.
        """
        return redirect('create-checkout-session')
    
