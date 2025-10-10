import pytest 
import factory
from apps.cart.cart import Cart 
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

from apps.products.repositories import ProductRepository

pytestmark = pytest.mark.django_db

@pytest.fixture
def exceed_product(sku):
    """Create a product with a certain quantity"""
    output_product = ProductFactory(name='Blue Jeans', sku=sku, stock=8)
    ProductImageFactory(product=output_product, image=factory.django.ImageField(color='red'))
    return output_product

@pytest.fixture 
def mock_session():
    """Mock session for anonymous cart testing"""
    session = {}
    return session

@pytest.fixture
def cart(mock_session):
    cart = Cart(mock_session)
    return cart


class TestCart:
    def test_cart_initialization(self, mock_session):
        cart = Cart(mock_session)
        assert cart.cart == {}
        assert len(cart) == 0
        assert cart.items_count == 0
        assert cart.total_items == 0
        assert cart.taxes == 0.0
        assert cart.shipping_fee == 0.0
        assert cart.subtotal == 0.0
        assert cart.total_amount == 0.0
    
    def test_cart_add_unexisting_product(self, sku, mock_session, cart, product):
        cart.add(sku)
        assert len(cart) == 1
    
    def test_cart_add_existing_product(self, sku, mock_session, cart, product):
        cart.add(sku)
        cart.add(sku)
        assert cart.cart[sku]['quantity'] > 1
    
    def test_cart_add_quantity_exceeds_stock(self, sku, mock_session, cart, exceed_product):
        cart.add(sku, quantity=9)
        assert cart.cart[sku]['quantity'] == 8

    def test_cart_add_has_discount(self, sku, mock_session, product):
        product.old_price = 800
        product.save()
        assert product.discount > 0.0

    def test_cart_save(self, sku, mock_session, cart, product):
        cart.add(sku)
        cart.cart[sku]['quantity'] = 6
        assert cart.cart[sku]['quantity'] == 6
        cart.modified == False 
        cart.save()
        assert cart.modified == True

    def test_cart_variant_product_with_attributes(self, variant_sku, cart, variant_product):
        variant_attributes = ProductRepository().get_variant_attribute(variant_product.id)
        assert variant_attributes is not {}
        assert variant_product.sku == variant_sku
        cart.add(variant_product.sku, quantity=7)
        assert cart.cart[variant_product.sku]['attributes'] is not {}

    def test_cart_remove_method(self, sku, variant_sku, product, variant_product, cart):
        cart.add(sku, quantity=7)
        cart.add(variant_sku, quantity=10)
        cart.remove(sku) # We remove the base product
        assert len(cart.cart) == 1
        assert cart.cart.get(sku) is None

    def test_cart_clear_method(self, sku, cart, product):
        cart.add(sku)
        assert len(cart) > 0
        cart.clear()
        assert cart.cart == {}

    def test_cart_update_quantity_method(self, sku, variant_sku, product, variant_product, cart):
        cart.add(sku)
        cart.add(variant_sku)
        cart.add(variant_sku)
        cart.add(variant_sku)
        cart.add(variant_sku)
        message = cart.update_product_quantity(variant_sku, product_quantity=2)
        assert cart.cart[variant_sku]['quantity'] == 2 
        assert message == 1
        
    def test_cart_summary_method(self, variant_sku, sku, cart, product, variant_product):
        assert cart.cart is not {}
        summary = cart.get_cart_summary()
        assert summary['count'] == cart.items_count
        assert summary['total_items'] == cart.total_items
        assert summary['subtotal_price'] == cart.subtotal
        assert summary['taxes'] == cart.taxes
        assert summary['shipping_fee'] == cart.shipping_fee
        assert summary['total_price'] == cart.total_amount

    def test_cart_set_items_count_method(self, variant_product, cart):
        assert cart.items_count == len(cart)
    
    def test_cart_set_total_items_method(self, variant_product, cart):
        assert cart.total_items == sum(item['quantity'] for item in cart.cart.values())

    def test_cart_set_taxes_method(self, product, variant_product, cart):
        assert cart.taxes == cart.subtotal - (cart.subtotal * 20) / 100
    
    def test_cart_set_subtotal_method(self, product, variant_product, cart):
        assert cart.subtotal == sum([item['price'] * item['quantity'] for item in cart.cart.values()])

    def test_cart_set_shipping_fee_method(self, product, variant_product, cart):
        cart.set_shipping_fee(40)
        assert cart.shipping_fee == 40

    def test_cart_set_total_amount(self, product, variant_product, cart):
        cart.get_cart_summary()
        assert cart.total_amount == cart.subtotal + cart.taxes + cart.shipping_fee
    
    def test_cart_string_representation(self, cart):
        assert str(cart) == 'Cart Class' 
    
    



        

        


    
