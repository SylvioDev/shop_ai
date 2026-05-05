import django_filters as filters
from apps.products.models import Product

class ProductFilter(filters.FilterSet):
    description = filters.CharFilter(field_name='description', lookup_expr='icontains')
    category = filters.CharFilter(field_name='category__name', lookup_expr='icontains')
    
    class Meta:
        model = Product
        fields = {
            'price' : ['exact', 'gte', 'lte'],
            'name' : ['icontains'],
            'status' : ['exact']
        }
    
    def filter_queryset(self, queryset):
        return super().filter_queryset(queryset)
