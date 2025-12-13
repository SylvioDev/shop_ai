from django.contrib import admin
from .models import Payment
from apps.orders.models import Order
from apps.orders.models import OrderItem

# Register your models here.

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'customer_id', 'created_at', 'final_total', 'status']
    list_filter = ['order_number', 'customer_id', 'created_at']
    search_fields = ['order_number', 'customer_id']

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'product_name']
    list_filter = ['order', 'product']
    search_fields = ['product', 'order']

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['order', 'method', 'status', 'amount']
    list_filter = ['method', 'status']
    search_fields = ['order', 'method']
    