from django.contrib.auth.models import User
from apps.checkout.models import (
    Order,
    OrderItem
)

class OrderRepository:
    def retrieve_user_orders(self, user : User):
        return Order.objects.filter(customer_id=user)
        
    def retrieve_user_order_items(self, order : Order):
        return OrderItem.objects.filter(order=order)
    
    def retrieve_order_details(self, order_number : str):
        return Order.objects.get(order_number=order_number)