import pytest
from apps.container import container
from apps.conftest import (
    order_data,
    valid_user,
    order_items,
    pytestmark
)
from apps.users.utils import validate_required_keys
from apps.users.models import User
from apps.checkout.custom_exceptions import OrderNotFoundError
from django.db.models.query import QuerySet

class TestOrderService:
    def test_process_receipt(self, order_data, order_items):
        order_number = order_data.order_number
        user = User.objects.get(username='Paul')
        shipping_address = container.user_repo.retrieve_adress(user)
        context = container.order_service.processing_receipt(order_number)
        keys = [
            'order_id', 'order', 'user', 
            'full_name', 'order_items', 'shipping_address'
        ]
        assert isinstance(context, dict)
        assert validate_required_keys(context, keys) is True
        assert context.get('order_id') == order_number
        assert context.get('order') == order_data
        assert context.get('user') == user
        assert context.get('full_name') == user.first_name + ' ' + user.last_name
        assert context.get('shipping_address') == shipping_address.street_address
        assert len(context.get('order_items')) == 2
        assert isinstance(context.get('order_items'), QuerySet)
    
    def test_process_receipt_order_not_found(self, order_data):
        order_id = 'ORD-2026-PO7SML'
        with pytest.raises(OrderNotFoundError) as exc_info:
            context = container.order_service.processing_receipt(order_id)
            
        assert f'Order with ID {order_id} not found.' == str(exc_info.value)