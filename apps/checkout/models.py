from django.db import models
from django.contrib.auth.models import User
from apps.products.models import Product
import uuid
class PromoCode(models.Model):
    
    DISCOUNT_TYPES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed')
    ]

    code = models.CharField(max_length=20, default='PROMOS')
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=False)
    valid_from = models.DateField(auto_now_add=True)
    usage_limit = models.IntegerField(default=1)
    times_used = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
    promo_code = models.ForeignKey(PromoCode, on_delete=models.CASCADE)
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

    