from django.db import models
from django.contrib.auth.models import User

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

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    promo_code = models.ForeignKey(PromoCode, on_delete=models.CASCADE)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    final_total = models.DecimalField(max_digits=10, decimal_places=2)

