from django.contrib import admin
from .models import (
    UserProfile,
    Address
)
from django.apps import AppConfig


# Register your models here.

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'social_media_username')

@admin.register(Address)
class UserAddressAdmin(admin.ModelAdmin):
    list_display = ('street_address', 'city', 'state', 'address_type', 'zip_code', 'user')
    search_fields = ('street_address', 'city', 'state')
    ordering = ('city',)