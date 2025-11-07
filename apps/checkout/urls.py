from django.urls import path
from .views import (
    home,
    check_code_promo
)

urlpatterns = [
    path('', home, name='home'),
    path('promo-code/verify/<promo_code>', check_code_promo, name='check_promo')
]
