from django.urls import path
from .views import (
    home,
    review_cart,
    payment_status,
    stripe_webhook,
    success,
    cancel,
    PaymentConfirmView,
    payment_processing
)

urlpatterns = [
    path('', home, name='home'),
    path('review/', review_cart, name='review'),
    path('confirm/', PaymentConfirmView.as_view(), name='confirm'),
    path('payment/', payment_processing, name='create-checkout-session'),
    path('payment_status/<order_id>', payment_status, name='payment-status'),
    path('webhook/stripe/', stripe_webhook, name='stripe_webhook'),
    path('success/<order_id>', success, name='success'),
    path('cancel/<order_id>', cancel, name='cancel'),
]
