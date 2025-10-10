import pytest
import factory
from apps.factories import \
(
    ProductFactory,
    ProductVariantFactory,
    ProductImageFactory,
    VariantImageFactory,
    AttributeFactory,
    AttributeValueFactory,
    VariantAttributeFactory,
    CategoryFactory
)
from django.conf import settings
import tempfile

pytestmark = pytest.mark.django_db

@pytest.fixture(autouse=True)
def media_tmp_dir(settings):
    tmp_dir = tempfile.mkdtemp()
    settings.MEDIA_ROOT = tmp_dir
    yield tmp_dir 
    
@pytest.fixture
def sample_products():
    """Create a set of sample produtcs for testing"""
    clothe_category = CategoryFactory(name='Clothe', slug='clothe')
    high_tech_category = CategoryFactory(name='High-Tech', slug='high-tech')
    food_category = CategoryFactory(name='Food', slug='food')
    products = []
    products.append(ProductFactory(name='T-Shirt', price=12, stock = 9, category=clothe_category, status='published'))
    products.append(ProductFactory(name='Black Jeans', price=22, stock = 6, category=clothe_category, status='published'))
    products.append(ProductFactory(name='Yogurt', price=3, stock = 7, category=food_category, status = 'published'))
    products.append(ProductFactory(name='Red Velvet Cake', price=15, stock = 5, category=food_category, status = 'published'))
    products.append(ProductFactory(name='Laptop Lenovo', price=1300, stock=4, category=high_tech_category, status = 'published'))
    for product in products:
        ProductImageFactory(product=product, image=factory.django.ImageField(color='red'))
        
    return products

@pytest.fixture
def sku():
    """Mock sku of a test product """
    return 'SKU-A27DE69D'

@pytest.fixture 
def variant_sku():
    """Mock sku of a variant test product """
    return 'SKU-A27IU75P'

@pytest.fixture
def product(sku):
    """Create a test product with image """
    output_product = ProductFactory(name='Blue Jeans', sku=sku)
    ProductImageFactory(product=output_product, image=factory.django.ImageField(color='red'))
    output_product.price = 12
    output_product.status = 'published'
    output_product.stock = 12
    output_product.save()
    return output_product

@pytest.fixture
def variant_product(variant_sku):
    """
        Create a variant product "T-Shirt" with the following attributes : 
        - Size : XL
        - Color : Red
        - Material : Coton 
    """
    product = ProductFactory(name='T-Shirt', sku='SKU7845AAM')
    variant_product = ProductVariantFactory(product=product, identifiant='Red T-Shirt Coton', sku=variant_sku)
    color_attribute = AttributeFactory(name='Color')
    size_attribute =  AttributeFactory(name='Size')
    material_attribute = AttributeFactory(name='Material')
    # Values of each attributes
    color_value = AttributeValueFactory(attribute=color_attribute, value='Red')
    size_value = AttributeValueFactory(attribute=size_attribute, value='XL')
    material_value = AttributeValueFactory(attribute=material_attribute, value='Coton')
    # Assigning each attributes to product_variant
    VariantAttributeFactory(variant=variant_product, attribute=color_attribute, value=color_value)
    VariantAttributeFactory(variant=variant_product, attribute=size_attribute, value=size_value)
    VariantAttributeFactory(variant=variant_product, attribute=material_attribute, value=material_value)

    VariantImageFactory(variant=variant_product, image=factory.django.ImageField(color='red')).save()
    variant_product.price = 31
    variant_product.save()

    return variant_product
