from django.db import models
from django.contrib.auth.models import User
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    items = models.JSONField(default=dict)
    updated_at = models.DateTimeField(auto_now=True)

