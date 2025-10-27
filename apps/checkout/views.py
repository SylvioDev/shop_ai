from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def home(request):
    cart = request.session.get('cart', {})
    return render(request, 'checkout.html', {'count' : len(cart.values())})

