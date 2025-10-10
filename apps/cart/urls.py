from django.urls import path
from .views import (
    add_to_cart,
    cart_count,
    cart_detail,
    update_quantity,
    delete_product
)
urlpatterns = [
    path('', cart_detail, name='cart'),
    path('add/<product_sku>/<product_quantity>', add_to_cart, name='cart-add'),
    path('count/', cart_count, name='cart-count'),
    path('update-quantity/<product_sku>&<product_quantity>', update_quantity, name='update-quantity'),
    path('delete/<product_sku>', delete_product, name='delete-product')
    
]