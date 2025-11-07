from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.cart.cart import Cart
from apps.users.services import UserService

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

def check_code_promo(request, promo_code):
    print(f'Promo code : {promo_code}')
    
