import factory
from apps.products.models import (
    Product,
    Category,
    ProductVariant,
    ProductImage,
    Attribute,
    AttributeValue,
    VariantAttribute,
    VariantImage
)
from factory import Faker
from factory import fuzzy
from factory import SubFactory
from factory.django import ImageField
import uuid

class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category
    name = Faker('word')
    slug = Faker('word')
    
class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product
    
    name = factory.fuzzy.FuzzyChoice(['Jeans', 'T-Shirt', 'Sneakers', 'Laptop'])
    price = Faker('pydecimal', left_digits=3, right_digits=2, max_value=100)
    stock = Faker('pyint', min_value=1, max_value=100)
    category = factory.SubFactory(CategoryFactory)
    slug = Faker('word')
    sku = factory.LazyAttribute(lambda obj : f'SKU-{uuid.uuid4().hex[:8].upper()}')
    
class ProductVariantFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProductVariant
    
    product = factory.SubFactory(ProductFactory)
    identifiant = factory.fuzzy.FuzzyChoice(['Yogurt', 'T-Shirt', 'Sneakers', 'PC Gamer'])
    price = Faker('pydecimal', left_digits=3, right_digits=2, max_value=100)
    stock = Faker('pyint', min_value=1, max_value=100)
    sku = factory.LazyAttribute(lambda obj : f'SKU-{uuid.uuid4().hex[:8].upper()}')

class VariantImageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = VariantImage
    variant = factory.SubFactory(ProductVariantFactory)
    image = factory.django.ImageField(color='black', width=100, height=200)

class ProductImageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProductImage
    product = factory.SubFactory(ProductFactory)
    image = factory.django.ImageField(color='black', width=100, height=200)

class AttributeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Attribute
    name = factory.fuzzy.FuzzyChoice(['Taste', 'Color', 'Material', 'Size'])

class AttributeValueFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AttributeValue
    attribute = factory.SubFactory(AttributeFactory)
    value = factory.fuzzy.FuzzyChoice(['42', 'Good', 'XL', 'Coton'])

class VariantAttributeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = VariantAttribute
    
    variant = factory.SubFactory(ProductVariantFactory)
    attribute = factory.SubFactory(AttributeFactory)
    value = factory.SubFactory(AttributeValueFactory)

