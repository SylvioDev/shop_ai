from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.cart.cart import Cart

@login_required
def home(request):
    cart = Cart.from_request(request)
    return render(
        request, 
        'checkout.html', 
        {
            'cart' : cart.cart, 
            'count' : len(cart),
            'cart_summary' : cart.get_cart_summary()
        }
    )

    
