from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.generic.detail import DetailView
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
            #'cart' : cart_validation
        })
    except (EmptyCartError, OutOfStockError) as error:
        return JsonResponse({'status':'error', 'error': str(error)})
    
class PaymentInitView(DetailView):
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
        
