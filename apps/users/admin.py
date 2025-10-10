from django.contrib import admin
from .models import UserProfile
from django.apps import AppConfig

# Register your models here.

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'social_media_username')
