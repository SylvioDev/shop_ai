from django.urls import path
from .views import (
    ListProductsView,
    filter_category,
    ProductDetail,
    update_variant
)

urlpatterns = [
    path('', ListProductsView.as_view(), name='products'),
    path('filter-category/<category>', filter_category, name = 'filter-category'),
    path('<slug>', ProductDetail.as_view(), name='product-detail'),
    path('update-variant/<product_sku>', update_variant, name='update-variant')
]