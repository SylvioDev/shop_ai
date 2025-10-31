from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.cart.cart import Cart
from .services import CheckoutService

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
            'user_address' : CheckoutService().get_user_address(user.id)
        }
    )

    
