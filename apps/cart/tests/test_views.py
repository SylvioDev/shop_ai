import pytest 
from django.urls import reverse
import json 
from apps.cart.cart import Cart
from apps.conftest import (
    product, 
    variant_product,
    sku,
    variant_sku,
)
from apps.cart.tests.test_cart import (
    mock_session,
    cart
)
from apps.conftest import pytestmark

@pytest.fixture
def root_url():
    return reverse('cart')

@pytest.fixture
def count_url():
    return reverse('cart-count')

class TestCartDetailView:
    def test_cart_detail_get(self, client, root_url):
        response = client.get(root_url)
        html = response.content.decode()
        template_name = response.templates[0].name
        assert response.status_code == 200
        assert template_name == 'cart.html'
        assert 'Shopping Cart : 0 items' in html 

class TestCartCountView:
    def test_cart_count_empty(self, client, count_url):
        response = client.get(count_url)
        cart = Cart({})
        assert response.status_code == 200
        assert len(cart) == 0
    
    def test_cart_count_not_empty(self, cart, count_url, client, product, sku, variant_sku, variant_product):
        cart.add(sku)
        cart.add(variant_sku)
        response = client.get(count_url)
        assert response.status_code == 200
        assert len(cart) == 2

class TestCartAddView:
    def test_cart_add_failed(self, client, sku):
        fake_sku = 'SKU-PO84KSM'
        params = {
            'product_sku' : fake_sku,
            'product_quantity' : 4
        }
        response = client.post(reverse('cart-add', kwargs=params))
        json_response = json.loads(response.content.decode())
        assert json_response.get('status') == 'error'
        assert json_response.get('message') == f'Product with SKU \'{fake_sku}\' not found'

    def test_cart_add_success(self, client, sku, product):
        params = {
            'product_sku' : sku,
            'product_quantity' : 5
        }
        response = client.post(reverse('cart-add', kwargs=params))
        json_response = json.loads(response.content.decode())
        cart = json_response['cart']
        assert response.status_code == 200
        assert cart.get(sku) is not None
        assert cart.get(sku)['quantity'] == 5
        
class TestCartUpdateQuantityView:
    def test_cart_update_quantity_failure(self, client, variant_sku, variant_product):
        invalid_sku = 'Invalid sku'
        params = {
            'product_sku' : invalid_sku,
            'product_quantity' : 3
        }
        add_response = client.post(reverse('cart-add', kwargs=params))
        response = client.post(reverse('update-quantity', kwargs={'product_sku':invalid_sku, 'product_quantity':8}))
        json_response = json.loads(response.content.decode())
        assert json_response['status'] == 'error'
        assert json_response['message'] == f"product '{invalid_sku}' doesn't exist"

    def test_cart_update_quantity_success(self, client, variant_sku, variant_product):
        params = {
            'product_sku' : variant_sku,
            'product_quantity' : 4
        }
        add_response = client.post(reverse('cart-add', kwargs=params))
        response = client.post(reverse('update-quantity', kwargs={'product_sku':variant_sku, 'product_quantity':8}))
        json_response = json.loads(response.content.decode())
        cart = json_response['cart']
        assert json_response.get('status') == 'success'
        assert cart[variant_sku]['quantity'] == 8
        
class TestCartDeleteView:
    def test_cart_delete_failure(self, client, variant_sku, variant_product):
        params = {
            'product_sku' : variant_sku,
            'product_quantity' : 4
        }
        add_response = client.post(reverse('cart-add', kwargs=params))
        invalid_sku = 'invalid sku'
        response = client.post(reverse('delete-product', kwargs={'product_sku' : invalid_sku}))
        json_response = json.loads(response.content.decode())
        assert json_response.get('status') == 'error'
        assert json_response.get('message') == f'Product with sku "{invalid_sku}" doesn\'t exist !'
    
    def test_cart_delete_success(self, client, variant_sku,  variant_product):
        params = {
            'product_sku' : variant_sku,
            'product_quantity' : 4
        }
        add_response = client.post(reverse('cart-add', kwargs=params))
        response = client.post(reverse('delete-product', kwargs={'product_sku':variant_sku}))
        json_response = json.loads(response.content.decode())
        assert json_response.get('status') == 'success'
        assert json_response.get('message') == f'Product with sku "{variant_sku}" deleted successfully !'
    
        
        



