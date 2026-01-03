from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.generic import (
    ListView,
    DetailView
)
from apps.container import container
from apps.checkout.models import Order
from apps.checkout.custom_exceptions import OrderNotFoundError

# Create your views here.

class OrderListView(LoginRequiredMixin, ListView):
    """
    Handle displaying a list of orders for the logged-in user.
    1. Retrieve orders associated with the user.
    2. Render the order list template with the retrieved orders.

    Methods:
        get(self, request): Handle GET requests to display the order list.
        
    """
    model = Order
    template_name = 'order_list.html'
    
    def get(self, request):
        """
        Handle GET requests to display the order list.
        
        Args:
            request: The HTTP request object.   
        
        Returns:
            Rendered order list template with user orders.
            
        """
        user = request.user
        orders = container.order_repo.retrieve_user_orders(user)
        context = {
            'user':user,
            'orders':orders,
        }
        return render(
            request,
            self.template_name,
            context
            
        )

class OrderDetailView(LoginRequiredMixin, DetailView):
    """
    Responsible for displaying detailed information about a specific order.
    1. Retrieve order details using the provided order number.
    2. Render the order detail template with the retrieved order information.
    
    Methods:
        get(self, request, order_number : str): Handle GET requests to display order details.
        
    """
    model = Order
    template_name = 'order_detail.html'
    
    def get(self, request, order_number : str):
        """
        Handle GET requests to display order details.
        
        Args:
            request: The HTTP request object.
            order_number (str): The unique identifier for the order.
        
        Returns:
            Rendered order detail template with order information.
        """
        order = container.order_repo.retrieve_order_details(order_number)
        user = request.user
        shipping_address = container.user_service.get_user_address(user)
        context = {
            'user':user,
            'order' : order,
            'shipping_address':shipping_address
        }
        
        return render(request, self.template_name, context)

#### Receipt view ####

def process_receipt(request, order_id : str):
    """
    Handle receipt processing and rendering.
    Retrieve the necessary context for the receipt and render the receipt template.
    
    Args:
        request: The HTTP request object.
        order_id (str): The identifier of the order for which to generate the receipt.
        
    Returns:
        Rendered receipt template with order context.
    """
    try:
        context = container.order_service.processing_receipt(order_id)
    except OrderNotFoundError as error:
        return JsonResponse({'status':'error', 'message':str(error)}, status=404)
    
    return render(
        request,
        'receipt.html',
        context=context
    )
