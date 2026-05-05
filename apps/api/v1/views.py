from .serializers import ProductSerializer
from rest_framework import viewsets
from rest_framework.filters import SearchFilter
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from apps.products.models import Product
from apps.api.v1.custom_filters import ProductFilter

class ProductPagination(PageNumberPagination):
    page_size = 3
    max_page_size = 5
    invalid_page_message = 'Page {page_number} does not exist.'
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by('-status')
    serializer_class = ProductSerializer
    filterset_class = ProductFilter
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['stock', 'name']
    search_fields = ['name']
    ordering_fields = ['price']
    pagination_class = ProductPagination




