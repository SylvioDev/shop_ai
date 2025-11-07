from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.cart.cart import Cart
from apps.users.services import UserService
from django.http import JsonResponse
from .promo_service import PromoService
from .promo_service import InvalidPromoCodeError


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
    """
    View that handle promo code validation request

    """
    try:
        code = PromoService().check_promo_code(promo_code)
    except InvalidPromoCodeError as error:
        return JsonResponse({
            'status' : 'error',
            'message' : str(error)
        }, status=400)
    
    return JsonResponse(
        {
            'status' : 'success',
            'message' : code
        }
    )
