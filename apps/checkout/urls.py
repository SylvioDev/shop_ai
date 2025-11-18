from django.urls import path
from .views import (
    home,
    review_cart,
    payment_status,
    create_checkout_session,
    stripe_webhook,
    success,
    cancel
)

urlpatterns = [
    path('', home, name='home'),
    path('review/', review_cart, name='review'),
    path('payment/', create_checkout_session, name='create_checkout_session'),
    path('payment_status/', payment_status, name='payment-status'),
    path('webhook/stripe/', stripe_webhook, name='stripe_webhook'),
    path('success/', success, name='success'),
    path('cancel/', cancel, name='cancel'),
]
