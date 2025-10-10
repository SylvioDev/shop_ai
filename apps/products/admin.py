from django.contrib import admin
from .models import Product
from .models import Category
from .models import ProductImage
from .models import Attribute
from .models import AttributeValue
from .models import ProductVariant
from .models import VariantAttribute
from .models import VariantImage


# Register your models here.

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    readonly_fields = ('sku',)
    list_display = ['name', 'price', 'slug', 'stock', 'status', 'sku']
    list_filter = ['status', 'discount']
    search_fields = ['name', 'sku']
    readonly_fields = ['sku']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline]

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    list_filter = ['name']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'image']

admin.site.register(Attribute)
admin.site.register(ProductVariant)
admin.site.register(AttributeValue)
admin.site.register(VariantAttribute)

class VariantImageInline(admin.TabularInline):
    model = ProductVariant
    extra = 1

admin.site.register(VariantImage)
