import pytest
import json
from apps.conftest import pytestmark
from apps.conftest import valid_user
from apps.conftest import product
from apps.conftest import sku
from django.urls import reverse
from .api_fixtures import token, added_product
from urllib.parse import urlencode

class TestCartAddProduct:
    def test_success(self, client, valid_user, sku, token, product):
        extra_headers = {'HTTP_AUTHORIZATION':f'Bearer {token}'}
        data = {'product_sku' : sku, 'quantity' : 4}
        response = client.post(
            reverse('cart-api'), 
            data=json.dumps(data),
            content_type='application/json',
            **extra_headers
        )
        assert response.status_code == 200
        assert response.json().get('message') == f'Product \"{sku}\" added successfully'
    
    def test_product_not_found(self, client, valid_user, token, product, added_product):
        extra_headers = {'HTTP_AUTHORIZATION':f'Bearer {token}'}
        invalid_sku = 'whatever'
        data = {'product_sku' : invalid_sku, 'quantity' : 4}
        response = client.post(
            reverse('cart-api'), 
            data=json.dumps(data),
            content_type='application/json',
            **extra_headers
        )
        assert response.status_code == 404
        assert response.json().get('error') == f'Product with SKU \'{invalid_sku}\' not found'

    def test_add_duplicate_product(self, client, valid_user, sku, product, token):
        product.stock = 15
        extra_headers = {'HTTP_AUTHORIZATION':f'Bearer {token}'}
        data = {'product_sku' : sku, 'quantity' : 4}
        response = client.post(
            reverse('cart-api'), 
            data=json.dumps(data),
            content_type='application/json',
            **extra_headers
        )
        assert response.status_code == 200
        other_response = client.post(
            reverse('cart-api'),  
            data=json.dumps(data),
            content_type='application/json',
            **extra_headers
        )
        assert other_response.status_code == 200
        cart_request = client.get(reverse('cart-api'), **extra_headers)
        quantity = cart_request.json().get(sku)['quantity']
        assert cart_request.status_code == 200
        assert quantity == 8 # same product added twice 4 + 4 = 8

class TestCartRemoveProduct:
    def test_remove_unexisting_product(self, client, product, sku, token, added_product):
        extra_headers = {'HTTP_AUTHORIZATION':f'Bearer {token}'}
        invalid_sku = 'fake sku'
        
        base_url = reverse('cart-api')
        params = {'product_sku':invalid_sku}
        full_url = f'{base_url}?{urlencode(params)}'
        delete_response = client.delete(
            full_url,
            **extra_headers
        )
        assert delete_response.status_code == 404
        assert delete_response.json().get('error') == f'Product with sku "{invalid_sku}" doesn\'t exist !'

    def test_missing_product_sku(self, client, product, sku, token):
        base_url = reverse('cart-api')
        extra_headers = {'HTTP_AUTHORIZATION':f'Bearer {token}'}
        response = client.delete(
            base_url,
            **extra_headers
        )
        assert response.status_code == 400
        assert response.json().get('error') == 'missing data!'

    def test_delete_success(self, client, product, sku, token, added_product):
        extra_headers = {'HTTP_AUTHORIZATION':f'Bearer {token}'}
        base_url = reverse('cart-api')
        full_url = f'{base_url}?{urlencode({'product_sku':sku})}' 
        response = client.delete(
            full_url,
            **extra_headers
        )
        assert response.status_code == 200
        assert response.json().get('message') == f'Product with sku "{sku}" deleted successfully !'

class TestCartClear:
    def test_clear_success(self, client, added_product, token):
        extra_headers = {'HTTP_AUTHORIZATION':f'Bearer {token}'}
        response = client.delete(
            reverse('cart-clear'),
            **extra_headers
        )
        assert response.status_code == 200
        assert response.json().get('message') == 'Cart cleared'
        assert response.json().get('cart') == {}

class TestCartUpdateQuantity:
    def test_missing_product_data(self, client, product, sku, token, added_product):
        extra_headers = {'HTTP_AUTHORIZATION':f'Bearer {token}'}
        data={'':''}
        response = client.patch(
            reverse('cart-api'),
            data=json.dumps(data),
            content_type='application/json',
            **extra_headers
        )
        assert response.status_code == 400
        assert response.json().get('error') == 'missing data!'
    
    def test_invalid_quantity(self, client, product, sku, token, added_product):
        extra_headers = {'HTTP_AUTHORIZATION':f'Bearer {token}'}
        data = {'product_sku' : sku, 'quantity' : 'shit'}
        response = client.patch(
            reverse('cart-api'),
            data=json.dumps(data),
            content_type='application/json',
            **extra_headers
        )
        assert response.status_code == 400
        assert response.json().get('error') == 'Please provide a valid quantity number'

    def test_product_not_found(self, client, product, token, sku, added_product):
        extra_headers = {'HTTP_AUTHORIZATION':f'Bearer {token}'}
        fake_sku = 'fake sku'
        data = {'product_sku':fake_sku, 'quantity':7}
        response = client.patch(
            reverse('cart-api'),
            data=json.dumps(data),
            content_type='application/json',
            **extra_headers
        )
        assert response.status_code == 404
        assert response.json().get('error') == f'There is no product with sku "{fake_sku}"'

    def test_update_success(self, client, product, sku, token, added_product):
        extra_headers = {'HTTP_AUTHORIZATION':f'Bearer {token}'}
        data = {'product_sku': sku, 'quantity' : 8}
        response = client.patch(    
            reverse('cart-api'),
            data=json.dumps(data),
            content_type='application/json',
            **extra_headers
        )
        assert response.status_code == 200
        assert response.json().get('message') == 'Product quantity updated successfully'
        cart = client.get(reverse('cart-api'), **extra_headers).json()
        assert cart.get(sku).get('quantity') == 8

class TestCartGet:
    def test_success(self, client, sku, product, added_product, token):
        extra_headers = {'HTTP_AUTHORIZATION':f'Bearer {token}'}
        response = client.get(reverse('cart-api'), **extra_headers)
        cart = response.json()
        assert response.status_code == 200
        assert isinstance(cart, dict)
        assert len(cart) > 0
    
    def test_failure(self, client, sku, product, added_product):
        response = client.get(reverse('cart-api'))
        assert response.status_code == 401
        assert response.json().get('detail') == 'Authentication credentials were not provided.'
        