from django.db import models
from apps.orders.models import Order    
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
    order = models.OneToOneField('orders.Order', on_delete=models.CASCADE, related_name='payment')
    method = models.CharField(choices=PAYMENT_METHODS, max_length=255)
    provider = models.CharField(choices=PAYMENT_PROVIDERS, default=('stripe'), max_length=255)
    status = models.CharField(choices=PAYMENT_STATUS, max_length=255)
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