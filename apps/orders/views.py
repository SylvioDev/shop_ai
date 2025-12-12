from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (
    ListView,
    DetailView
)
from apps.container import container
from apps.checkout.models import Order

# Create your views here.

class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'order_list.html'
    
    def get(self, request):
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
    model = Order
    template_name = 'order_detail.html'
    
    def get(self, request, order_number : str):
        order = container.order_repo.retrieve_order_details(order_number)
        user = request.user
        shipping_address = container.user_service.get_user_address(user)
        context = {
            'user':user,
            'order' : order,
            'shipping_address':shipping_address
        }
        
        return render(request, self.template_name, context)