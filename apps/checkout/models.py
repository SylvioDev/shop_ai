from django.db import models
from django.contrib.auth.models import User
from apps.products.models import Product
import uuid
class Order(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('shipped', 'Shipped'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ]

    order_number = models.CharField(max_length=255, unique=True, editable=False, default='ORD-2025')
    customer_id = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    final_total = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, force_insert = False , *args, **kwargs):
        self.order_number = f'ORD-{self.created_at.year}-{uuid.uuid1().hex[:8].upper()}'
        super().save(force_insert=force_insert, *args, **kwargs)

    def __str__(self):
        return self.order_number

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(default=0.00, decimal_places=2, max_digits=10)
    total_price = models.DecimalField(decimal_places=2, max_digits=10, default=0.00)
    product_name = models.CharField(max_length=255)
    attributes = models.JSONField(verbose_name='product_attributes')
    unit_price = models.DecimalField(decimal_places=2, max_digits=10)
    quantity = models.IntegerField(default=1)
    total_price = models.DecimalField(decimal_places=2, max_digits=10)

class Payment(models.Model):

    PAYMENT_METHODS = [
        ('paypal', 'Paypal')
    ]

    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed')
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    method = models.CharField(choices=PAYMENT_METHODS)
    status = models.CharField(choices=PAYMENT_STATUS)
    transaction_id = models.CharField(max_length=255, default='67N9717781765035V')
    amount = models.DecimalField(decimal_places=2, max_digits=10, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)

class Shipping(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    address_line = models.CharField(max_length=255)
    zip_code = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    status = models.CharField(max_length=255)