from django.contrib import admin
from .models import Cart

@admin.register(Cart)
class CartModelAdmin(admin.ModelAdmin):
    list_display = ['user', 'items', 'updated_at']