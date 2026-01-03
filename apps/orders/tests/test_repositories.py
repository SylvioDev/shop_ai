import pytest
from django.db.models.query import QuerySet
from django.contrib.auth.models import User
from apps.conftest import (
    valid_user,
    order_data,
    order_items
)
from apps.orders.models import Order
from apps.container import container

pytestmark = pytest.mark.django_db

class TestOrderRepository:
    def test_retrieve_user_orders_success(self, order_data):
        user = User.objects.get(username='Paul')
        orders = container.order_repo.retrieve_user_orders(user)
        assert isinstance(orders, QuerySet)
        assert len(orders) == 1
    
    def test_retrieve_user_orders_failure(self, valid_user):
        orders = container.order_repo.retrieve_user_orders(valid_user)
        assert isinstance(orders, QuerySet)
        assert len(orders) == 0
    
    def test_retrieve_order_details_success(self, order_data):
        order = container.order_repo.retrieve_order_details(order_data.order_number)
        assert isinstance(order, Order)
        assert str(order) == order_data.order_number
    
    def test_retrieve_order_details_failure(self):
        with pytest.raises(Order.DoesNotExist) as exc_info:
            order = container.order_repo.retrieve_order_details('False order')
        assert 'Order matching query does not exist.' == str(exc_info.value)
    
    def test_retrieve_user_order_items(self, order_data, order_items, cart_data):
        order_items = container.order_repo.retrieve_user_order_items(order_data)
        assert isinstance(order_items, QuerySet)
        assert len(order_items) == 2
        
        for item, order_item in zip(cart_data.cart.items(), order_items):
            item[1].get('title') == order_item.product_name
            item[1].get('price') == order_item.unit_price
            item[1].get('quantity') == order_item.quantity
        
    def test_retrieve_user_order_items_empty(self, order_data):
        order_items = container.order_repo.retrieve_user_order_items(order_data)
        assert isinstance(order_items, QuerySet)
        assert len(order_items) == 0