from django.shortcuts import render
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.generic.detail import DetailView
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from apps.cart.cart import Cart

from apps.users.services import UserService
from apps.checkout.checkout_services import CheckoutService
from apps.checkout.payment_service import StripePaymentService
from .cart_validation.cart_exceptions import (
    EmptyCartError,
    OutOfStockError
)
from .custom_exceptions import (
    InvalidPayloadException,
    InvalidSignatureException
)
from .models import (
    Order,
    Payment
)
from apps.users.services import UserService

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

def payment_status(request):
    """ 
    Display payment status to the user based on the session_id 
    and status provided in the GET parameters.
    """
    cart = Cart.from_request(request)
    session_id = request.GET.get('session_id', '')
    status = request.GET.get('status', 'pending')
    payment_details = StripePaymentService().payment_details(session_id)
   
    if session_id == '' or status == 'pending' or payment_details == 'invalid session id':
        return HttpResponseBadRequest('Error encountered while retrieving payment details.')
    
    return render(
        request, 
        'payment_status.html', 
        {
            'count' : len(cart),
            'status' : status,
            'payment_details' : payment_details
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

@login_required
def payment_processing(request):
    cart = Cart.from_request(request)
    try:
        checkout_session = StripePaymentService().create_session(cart, request.user)
    except ValueError as error:
        return JsonResponse({'status':'error', 'error': str(error)})
    
    if 'error' in checkout_session:
        return JsonResponse({'status':'error', 'error': checkout_session.get('error')})
    
    return redirect(checkout_session.url, code=303)
    
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

def success(request):
    session_id = request.GET.get('session_id', '')
    return redirect(f'/checkout/payment_status/?session_id={session_id}&status=success')

def cancel(request):
    session_id = request.GET.get('session_id', '')
    return redirect(f'/checkout/payment_status/?session_id={session_id}&status=error')

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
        cart = Cart.from_request(request)
        total_price = cart.get_cart_summary().get('total_price')
        subtotal = cart.get_cart_summary().get('subtotal_price')
        user = request.user
        # Order creation before redirecting to payment gateway
        order = Order.objects.create(
            customer_id=user,
            status='pending',
            total_price=subtotal,
            final_total=total_price,
            vat = cart.get_cart_summary().get('taxes'),
            shipping_cost = cart.get_cart_summary().get('shipping_fee'),
            shipping_address = UserService.get_user_address(user_instance=user.id)
        )
        
        # Payment creation 
        
        payment = Payment.objects.create(
            order=order,
            method='stripe',
            status='pending',
            amount=total_price
        )
        
        order.save()
        payment.save()
        
        return redirect('create-checkout-session')