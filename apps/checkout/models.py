from django.db import models
from django.contrib.auth.models import User
from apps.products.models import (
    Product,
    ProductVariant
)
from apps.users.models import Address
import uuid
from datetime import datetime
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
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE,null=True)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE,null=True)
    product_name = models.CharField(max_length=255)
    attributes = models.JSONField(verbose_name='product_attributes')
    unit_price = models.DecimalField(decimal_places=2, max_digits=10)
    quantity = models.IntegerField(default=1)
    total_price = models.DecimalField(decimal_places=2, max_digits=10)
    image_url = models.CharField(max_length=500, null=True)
    
class Payment(models.Model):

    PAYMENT_PROVIDERS = [
        ('paypal', 'Paypal'),
        ('stripe', 'Stripe'),
    ]
    
    PAYMENT_METHODS = [
        ('card', 'Credit Card'),
        ('cash_on_delivery', 'Cash on Delivery')
    ]

    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed')
    ]
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    method = models.CharField(choices=PAYMENT_METHODS)
    provider = models.CharField(choices=PAYMENT_PROVIDERS, default=('stripe'))
    status = models.CharField(choices=PAYMENT_STATUS)
    stripe_payment_intent_id = models.TextField(default='67N9717781765035V', null=True)
    stripe_session_id = models.TextField(default='1234')
    transaction_id = models.CharField(max_length=255, default='SDQSA')
    amount = models.DecimalField(decimal_places=2, max_digits=10, default=0.00)
    currency = models.CharField(max_length=10, default='USD')
    created_at = models.DateTimeField(auto_now_add=True)
    paied_at = models.DateTimeField(null=True, blank=True)
    
class Shipping(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    address_line = models.CharField(max_length=255)
    zip_code = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    status = models.CharField(max_length=255)