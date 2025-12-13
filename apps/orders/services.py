from .models import Order
from .models import OrderItem
from apps.users.models import User
from apps.container import container

class OrderService:
    """
    Service responsible for processing order-related business logic.
    Handles operations such as processing receipts.
    
    Attributes:
        repo : (OrderRepository): Single source of truth for all order data.
    
    Methods:
        processing_receipt(order_id: str) -> dict:
            Processes the receipt for a given order ID and returns the context data.    
    """
    def __init__(self, order_repo):
        """
        Initialize service with repository dependency.
        """
        self.repo = order_repo
    
    def processing_receipt(self, order_id : str):
        """
        Processes the receipt for a given order ID and returns the context data.
        
        Args:
            order_id (str): The unique identifier of the order.
        
        Returns:
            dict: A dictionary containing order details for receipt generation.
            
        """
        order = container.order_repo.retrieve_order_details(order_id) 
        user = container.user_service.get_user_credentials(user_id=order.customer_id.id)
        
        full_name = user.first_name + ' ' + user.last_name
        shipping_address = container.user_service.get_user_address(user)
        order_items = container.order_repo.retrieve_user_order_items(order) 
        context = {
            'order_id' : order_id,
            'order' : order,
            'user' : user,
            'full_name' : full_name,
            'shipping_address' : shipping_address.street_address,
            'order_items':order_items
        }
        
        return context