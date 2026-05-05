from rest_framework import serializers
from apps.products.models import Product
from apps.products.models import Category

class ProductSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        slug_field='name',
        queryset=Category.objects.all()
    )

    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'stock', 'status' , 'category']
