from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.cart.cart import Cart
from apps.users.services import UserService
from .promo.promo_service import PromoService
from django.http import JsonResponse
from .promo.custom_exceptions import (
    PromoCodeNotFoundError,
    PromoCodeExpiredError,
    PromoCodeInactiveError
)
import json

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

def check_code_promo(request):
    """
    View that handle promo code validation request

    """
    promo_code = json.loads(request.body).get('promo_code')
    try:
        validated_promo = PromoService().check_promo(promo_code)
        message = f"Promo code \"{validated_promo.get('promo').code}\" applied!"
        return JsonResponse({
            'status' : 'success',
            'promo' : validated_promo.get('promo').code,
            'message' : message
        })
    
    except (PromoCodeNotFoundError, PromoCodeExpiredError, PromoCodeInactiveError) as error:
        return JsonResponse({'status':'error', 'error' : str(error)})    
    
    