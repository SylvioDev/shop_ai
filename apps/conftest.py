import pytest
import factory
import uuid
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
from django.contrib.auth.models import User
from apps.users.models import Address
from apps.cart.cart import Cart
import tempfile
import shutil
from django.urls import reverse
from apps.container import container

pytestmark = pytest.mark.django_db

@pytest.fixture(scope="session", autouse=True)
def media_tmp_dir():
    """
    Overrides Django's MEDIA_ROOT to a temporary directory for tests.
    Automatically cleans up after the test session.
    """
    tmp_dir = tempfile.mkdtemp()
    original_media_root = settings.MEDIA_ROOT
    settings.MEDIA_ROOT = tmp_dir
    yield tmp_dir
    # Cleanup: restore original MEDIA_ROOT and remove temp folder
    settings.MEDIA_ROOT = original_media_root
    shutil.rmtree(tmp_dir)
    
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

@pytest.fixture
def mock_session(cart_data, order_data, payment_data):
    checkout_session = container.payment_service.create_session(
        cart=cart_data,
        user=order_data.customer_id,
        order=order_data,
        payment=payment_data
    )
    return checkout_session

@pytest.fixture
def valid_user():
    user = User.objects.create_user(
        username='test',
        email='test@example.com',
        password='mypassword'
    )
    user.save()
    address = Address.objects.create(
        user=user,
        address_type='shipping',
        city='Bruxelles',
        state = 'Bruxelles',
        country = 'Switzerland',
        zip_code = 70028,
        street_address='Hans Meier Gerechtigkeistgasse 10 3011 Berne'
    )
    address.save()
    return user

def checkout_user(username, user_address):
    user = User.objects.create_user(
        username=username,
        email=f'{username}@example.com',
        password='password'
    )
    address = Address.objects.create(
        user=user,
        address_type='shipping',
        city='New York',
        state = 'New York',
        country = 'US',
        zip_code = 10028,
        street_address=user_address
    )
    return user

#### Checkout app fixtures ####

@pytest.fixture
def cart_data(sku, variant_sku, product, variant_product):
    cart = Cart({})
    cart.add(sku, quantity=4)
    cart.add(variant_sku, quantity=2)
    return cart

@pytest.fixture
def payment_process_cart(client, sku, variant_sku, product, variant_product):
    params = {
        'product_sku' : sku,
        'product_quantity' : 4
    }
    variant_params = {
        'product_sku': variant_sku,
        'product_quantity' : 5
    }
    cart_add = client.post(reverse('cart-add', kwargs=params))
    another_cart_add = client.post(reverse('cart-add', kwargs=variant_params))
    
@pytest.fixture
def cart_summary_test(cart_data):
    return cart_data.get_cart_summary()

@pytest.fixture
def total_amount_test(cart_summary_test):
    output = cart_summary_test.get('subtotal_price') + cart_summary_test.get('taxes') + cart_summary_test.get('shipping_fee')
    return output

def user_order(cart_data, username, user_address):
    cart_summary = cart_data.get_cart_summary()
    total_amount = cart_summary.get('subtotal_price') + cart_summary.get('taxes') + cart_summary.get('shipping_fee')
    order = container.checkout_repo.create_order(
        user=checkout_user(username=username, user_address=user_address),
        cart_data=cart_summary,
        total_amount=total_amount
    )
    return order    

@pytest.fixture
def order_data(cart_data):
    order = user_order(cart_data, 'Paul', '78th street')
    return order

@pytest.fixture
def payment_data(cart_data, order_data):
    payment = container.checkout_repo.create_payment(
        order=order_data,
        payment_provider='Stripe',
        amount=cart_data.get_cart_summary()['total_price']
    )
    return payment
