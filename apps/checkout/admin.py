from django.contrib import admin
from .models import (
    PromoCode,
    Order,
    OrderItem
)
# Register your models here.

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'customer_id', 'created_at', 'final_total']
    list_filter = ['order_number', 'customer_id', 'created_at']
    search_fields = ['order_number', 'customer_id']

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'product_name']
    list_filter = ['order', 'product']
    search_fields = ['product', 'order']

@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_type', 'is_active', 'times_used', 'valid_from','valid_to']
