import pytest
import json
from django.urls import reverse
from apps.conftest import product
from apps.conftest import sku


@pytest.fixture
def token(client, valid_user):
    data = {'username':'test', 'password':'mypassword'}
    output = client.post(reverse('get-token'), data=data).json().get('access')
    return output

@pytest.fixture
def added_product(client, product, sku, token):
    product.stock = 15
    data = {'product_sku' : sku, 'quantity' : 4}
    extra_headers = {'HTTP_AUTHORIZATION':f'Bearer {token}'}
    response = client.post(
        reverse('cart-api'), 
        data=json.dumps(data),
        content_type='application/json',
        **extra_headers
        )
    return response