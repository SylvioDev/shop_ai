import json
from django.urls import reverse
from django.db.models.query import QuerySet
from apps.conftest import (
    valid_user,
    test_order,
    cart_data,
    login_user,
    order_data,
    order_items,
    paul_user,
    pytestmark
)
from apps.container import container
from apps.users.models import User
from apps.checkout.custom_exceptions import OrderNotFoundError

class TestOrderListView:
    def test_order_listview_not_authenticated(self, client):
        response = client.get(reverse('orders'))
        assert response.status_code == 302
        assert response.url == reverse('login')+'?next='+reverse('orders')
    
    def test_order_listview_authenticated(self, client, order_data):
        login_response = client.post(
            reverse('login'), 
            data = {
                'identifier':'Paul', 
                'password':'password', 
                'next':reverse('orders')
            }
        )
        assert login_response.status_code == 302
        assert login_response.url == reverse('orders')
        
        response = client.get(reverse('orders'))
        assert response.status_code == 200
        assert response.templates[0].name == 'order_list.html'
        context = response.context
        orders = context.get('orders')
        assert str(context.get('user')) == 'Paul'
        assert isinstance(orders, QuerySet)
        assert orders[0] == order_data 
    
class TestOrderDetailView:
    def test_order_detailview_not_authenticated(self, client):
        response = client.get(reverse('orders'))
        assert response.status_code == 302
        assert response.url == reverse('login')+'?next='+reverse('orders')
    
    def test_order_detailview_authenticated(self, client, login_user, paul_user):
        order = container.order_repo.retrieve_user_orders(paul_user)[0]
        address = container.user_repo.retrieve_adress(paul_user)
        response = client.get(reverse('order_detail', kwargs={'order_number':order.order_number}))
        context = response.context
        assert response.status_code == 200
        assert response.templates[0].name == 'order_detail.html'
        assert context.get('user') == paul_user
        assert context.get('order') == order
        assert context.get('shipping_address') == address
        
class TestProcessReceiptView:
    def test_process_receipt_order_not_found(self, client):
        order_id = 'fake-order_id'
        response = client.get(reverse('process-receipt', kwargs={'order_id':order_id}))
        assert response.status_code == 404
        content = json.loads(response.content.decode())
        assert content.get('status') == 'error'
        assert content.get('message') == f'Order with ID {order_id} not found.'
    
    def test_process_receipt_success(self, client, order_data, order_items, paul_user):
        response = client.get(reverse('process-receipt', kwargs={'order_id':order_data.order_number}))
        assert response.status_code == 200
        assert response.templates[0].name == 'receipt.html'
        context = response.context[0]
        assert context.get('order_id') == order_data.order_number
        assert context.get('order') == order_data
        assert context.get('user') == paul_user
        assert context.get('shipping_address') == container.user_repo.retrieve_adress(paul_user).street_address
        assert isinstance(context.get('order_items'), QuerySet)
        assert len(context.get('order_items')) == 2