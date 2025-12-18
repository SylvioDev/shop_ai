from django.db import models
from django.contrib.auth.models import User
from django.db import models
from django.conf import settings

def user_directory_path(instance, filename):
    return f'profile_pics/user_{instance.user.id}/{filename}'

class Address(models.Model):
    """
    Rerpesents a physical address associated with a user.
    """

    ADDRESS_TYPE_CHOICES = [
        ('billing', 'Billing'),
        ('shipping', 'Shipping'),
        ('home', 'Home')
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    street_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default='Madagascar')
    zip_code = models.CharField(max_length=100)
    address_type = models.CharField(max_length=10, choices=ADDRESS_TYPE_CHOICES, default='home')

    def __str__(self):
        return f"{self.user.username}' address "

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to=user_directory_path, null=True, blank=True)
    social_media_username = models.CharField(null=True, max_length=100)
    reset_token_used = models.BooleanField(default=False)
    phone_number = models.CharField(null=False, default='000 000 00 000', max_length=255)

    def __str__(self):
        return f'{self.user.username} Profile' 
class PendingEmailChange(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    new_email = models.EmailField()
    token = models.CharField(max_length=256, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        from datetime import timedelta, timezone, datetime
        return self.created_at < datetime.now(timezone.utc) - timedelta(hours=1)
