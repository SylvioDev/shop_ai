import json
from apps.conftest import (
    valid_user,
    sku,
    product,
    pytestmark
)
from .api_fixtures import (
    added_product,
    token
)
from django.urls import reverse

class TestOrderView:
    def test_order_list(self, client, product, sku, token):
        extra_headers = {'HTTP_AUTHORIZATION':f'Bearer {token}'}
        response = client.get(reverse('order-list'), **extra_headers)
        orders = response.json().get('results')
        assert response.status_code == 200
        assert isinstance(orders, list)

    def test_order_detail(self, client, product, sku, token):
        extra_headers = {'HTTP_AUTHORIZATION':f'Bearer {token}'}
        response = client.get(
            reverse('order-list'),
            **extra_headers
        )
        assert response.status_code == 200
        print(response.json())

class TestOrderCreation:
    def test_empty_cart(self, client, product, sku, token, valid_user):
        extra_headers = {'HTTP_AUTHORIZATION':f'Bearer {token}'}
        data = {'customer_id' : valid_user.id, 'final_total' : 487}
        response = client.post(
            reverse('order-list'),
            data=json.dumps(data),
            content_type='application/json',
            **extra_headers
        )
        assert response.status_code == 400
        assert response.json().get('error') == 'You cannot create order with empty cart'

    def test_invalid_data(self, client, product, sku, token, valid_user, added_product):
        extra_headers = {'HTTP_AUTHORIZATION':f'Bearer {token}'}
        data = {'customer_id' : 'whatever', 'final_total' : 877}
        response = client.post(
            reverse('order-list'),
            data=json.dumps(data),
            content_type='application/json',
            **extra_headers
        )
        assert response.status_code == 400
        assert ''.join(response.json().get('customer_id')) == 'Incorrect type. Expected pk value, received str.'
    
    def test_success(self, client, product, sku, token, added_product, valid_user):
        extra_headers = {'HTTP_AUTHORIZATION':f'Bearer {token}'}
        data = {'customer_id' : valid_user.id, 'final_total' : 877}
        response = client.post(
            reverse('order-list'),
            data=json.dumps(data),
            content_type='application/json',
            **extra_headers
        )
        cart = response.json().get('data').get('cart')
        dict_product = cart.get(sku)
        final_total = float(dict_product.get('price')) * int(dict_product.get('quantity')) + float(response.json().get('data').get('vat')) + 120
        assert response.status_code == 200
        assert response.json().get('message') == 'Order successfully created'
        assert isinstance(response.json().get('data'), dict) 
        assert isinstance(response.json().get('order_number'), str)
        assert isinstance(cart, dict)
        assert final_total == float(response.json().get('data').get('final_total'))
    
class TestOrderUpdate:
    def test_order_not_found(self, client, sku, added_product, token):
        extra_headers = {'HTTP_AUTHORIZATION':f'Bearer {token}'}
        order_number = 'whatever'
        data = {'status':'paid'}
        response = client.patch(
            reverse('order-detail', kwargs={'order_number':order_number}),
            data=json.dumps(data),
            content_type='application/json',
            **extra_headers
        )
        assert response.status_code == 404
        assert response.json() == 'Order matching query does not exist.'

    def test_order_already_paid(self, client, sku, valid_user,added_product, token):
        extra_headers = {'HTTP_AUTHORIZATION':f'Bearer {token}'}
        data = {'customer_id' : valid_user.id, 'final_total' : 877}
        response = client.post(
            reverse('order-list'),
            data=json.dumps(data),
            content_type='application/json',
            **extra_headers
        )
        order_number = response.json().get('order_number')
        payment_data = {'status':'paid'}
        paying_order = client.patch(
            reverse('order-detail', kwargs={'order_number':order_number}),
            data=payment_data,
            content_type="application/json",
            **extra_headers
        )
     
        assert paying_order.status_code == 200
        assert paying_order.json() == 'Order paid succesfully! Thank you for purchasing on shopai.com'
        
        another_payment = client.patch(
            reverse('order-detail', kwargs={'order_number':order_number}),
            data=json.dumps(payment_data),
            content_type="application/json",
            **extra_headers
        )
        
        assert another_payment.status_code == 400
        assert another_payment.json() == 'This order is already paid'
    
    def test_success(self, client, valid_user, added_product, token):
        extra_headers = {'HTTP_AUTHORIZATION':f'Bearer {token}'}
        data = {'customer_id' : valid_user.id, 'final_total' : 877}
        response = client.post(
            reverse('order-list'),
            data=json.dumps(data),
            content_type='application/json',
            **extra_headers
        )
        order_number = response.json().get('order_number')
        payment_data = {'status':'paid'}
        paying_order = client.patch(
            reverse('order-detail', kwargs={'order_number':order_number}),
            data=payment_data,
            content_type="application/json",
            **extra_headers
        )
     
        assert paying_order.status_code == 200
        assert paying_order.json() == 'Order paid succesfully! Thank you for purchasing on shopai.com'
        