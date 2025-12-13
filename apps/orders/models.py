import uuid
from django.db import models
from datetime import datetime
from apps.products.models import Product
from apps.products.models import ProductVariant
from apps.users.models import User
from apps.users.models import Address

class Order(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('shipped', 'Shipped'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('refunded_insufficient_stock', 'RefundedInsufficientStock'),
        
    ]

    order_number = models.CharField(max_length=255, unique=True, editable=False)
    customer_id = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    vat = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    shipping_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, related_name='shipping_address')   
    final_total = models.DecimalField(max_digits=10, decimal_places=2)
    cart = models.JSONField(default=dict)
    failure_reason = models.CharField(max_length=300, null=True)
    
    def save(self, force_insert = False , *args, **kwargs):
        year = datetime.now().year
        if not self.order_number:
            self.order_number = f'ORD-{year}-{uuid.uuid1().hex[:8].upper()}'
        super().save(force_insert=force_insert, *args, **kwargs)

    def __str__(self):
        return self.order_number

class OrderItem(models.Model):
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE,null=True)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE,null=True)
    product_name = models.CharField(max_length=255)
    attributes = models.JSONField(verbose_name='product_attributes')
    unit_price = models.DecimalField(decimal_places=2, max_digits=10)
    quantity = models.IntegerField(default=1)
    total_price = models.DecimalField(decimal_places=2, max_digits=10)
    image_url = models.CharField(max_length=500, null=True)
