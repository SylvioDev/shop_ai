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
from apps.users.services import UserService
from apps.checkout.services import CheckoutService
from apps.checkout.payment_service import StripePaymentService
from .cart_validation.cart_exceptions import (
    EmptyCartError,
    OutOfStockError
)
from .custom_exceptions import (
    InvalidPayloadException,
    InvalidSignatureException,
)
from .models import (
    Payment,
    OrderItem,
    Order
)

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
            'user_address' : UserService().get_user_address(user_instance=user.id)
        }
    )

def review_cart(request):
    cart = Cart.from_request(request)
    try:
        cart_validation = CheckoutService().cart_validation(cart)
        return JsonResponse({
            'status':'success',
            'message' : 'cart is valid',
        })
    except (EmptyCartError, OutOfStockError) as error:
        return JsonResponse({'status':'error', 'error': str(error)})

@login_required
def payment_processing(request):
    """
    Handle payment processing by creating a Stripe checkout session.
    """
    cart = Cart.from_request(request)
    try:
        # Order and payment initialization
        order = CheckoutService().order_creation(cart, request.user)
        payment = CheckoutService().payment_creation(order=order, payment_method='stripe')
        checkout_session = StripePaymentService().create_session(cart, request.user, order, payment)
        CheckoutService().add_order_items(order, cart=cart.cart)
    except ValueError as error:
        return JsonResponse({'status':'error', 'error': str(error)})
    
    if 'error' in checkout_session:
        return JsonResponse({'status':'error', 'error': checkout_session.get('error')})
    
    return redirect(checkout_session.url, code=303)
    
@csrf_exempt
@require_POST
def stripe_webhook(request):
    payload = request.body
    try:
        event = StripePaymentService.handle_webhook(payload, request.META.get('HTTP_STRIPE_SIGNATURE'))
    except InvalidPayloadException as e:
        return HttpResponse(status=400)
    except InvalidSignatureException as e:  
        return HttpResponse(status=400)
    return HttpResponse(status=200)

def success(request, order_id):
    return redirect(f'/checkout/payment_status/{order_id}')

def cancel(request, order_id : str):
    return redirect(f'/checkout/payment_status/{order_id}')

@login_required
def payment_status(request, order_id : str):
    """ 
    Handle payment status 
    """
    user = request.user
    cart = Cart.from_request(request)
    order = Order.objects.get(order_number=order_id)
    payment = Payment.objects.get(order=order)
    
    if order.status == 'paid':
        cart.clear() # Clear user cart
        
    return render(
        request, 
        'payment_status.html', 
        {   
            'order_status' : order.status,
            'count' : len(cart) if cart else 0,
            'payment' : payment,
            'order' : order
        }
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
    
#### Receipt view ####

def process_receipt(request, order_id : str):
    order = Order.objects.get(order_number=order_id)
    user = User.objects.get(id=order.customer_id.id)
    full_name = user.first_name + ' ' + user.last_name
    shipping_address = UserService().get_user_address(user)
    order_items = OrderItem.objects.filter(order=order)
    context = {
        'order_id' : order_id,
        'order' : order,
        'user' : user,
        'full_name' : full_name,
        'shipping_address' : shipping_address.street_address,
        'order_items':order_items
    }
    
    return render(
        request,
        'receipt.html',
        context=context
    )