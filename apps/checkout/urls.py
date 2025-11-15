from django.urls import path
from .views import (
    home,
    review_cart,
    payment_status,
    PaymentInitView
)

urlpatterns = [
    path('', home, name='home'),
    path('review/', review_cart, name='review'),
    path('payment/', PaymentInitView.as_view(), name='checkout-payment'),
    path('payment_status/', payment_status, name='payment-status')
]
