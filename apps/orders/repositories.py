from django.contrib.auth.models import User
from apps.orders.models import Order
from apps.orders.models import OrderItem
class OrderRepository:
    """
    Repository for managing order data.
    Order-related database operations are handled here. 
    
    Methods:
        - retrieve_user_orders: Fetch orders for a specific user.
        - retrieve_user_order_items: Fetch order items for a specific order.
        - retrieve_order_details: Fetch detailed information for a specific order.
    """
    def retrieve_user_orders(self, user : User):
        """
        Retrieve all orders associated with a given user.
        """
        return Order.objects.filter(customer_id=user)
        
    def retrieve_user_order_items(self, order : Order):
        """
        Retrieve all order items associated with a given order.
        """
        return OrderItem.objects.filter(order=order)
    
    def retrieve_order_details(self, order_number : str):
        """
        Retrieve detailed information for a specific order by its order number.
        """
        return Order.objects.get(order_number=order_number)