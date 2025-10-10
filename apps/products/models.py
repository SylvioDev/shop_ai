from django.db import models
from django.utils.text import slugify
import uuid 

def product_image_path(instance, filename):
    return f'product_images/{instance.product.slug}/{filename}'

def variant_product_image_path(instance, filename):
    product_name = instance.variant.product.name.replace(' ', '_').lower()
    return f'product_images/{product_name}/{instance.variant.identifiant}/{filename}'

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField()
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'Categories'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('review', 'In Review'),
        ('published', 'Published'),
        ('archived', 'Archived')
    ]

    class Meta:
        ordering = ['-discount']

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    slug = models.SlugField(unique=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    old_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    discount = models.DecimalField(max_digits=10, default=0.0, blank=True, null=True, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    sku = models.CharField(max_length=100, unique=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_published(self):
        return self.status == 'published'

    def save(self, force_insert = False , *args, **kwargs):
        if not self.sku:
            self.sku = f'SKU-{uuid.uuid1().hex[:8].upper()}'

        self.discount = 100 - (self.price * 100) / self.old_price if self.old_price > 0 else 0.0
        super().save(force_insert=force_insert, *args, **kwargs)

    def __str__(self):
        return self.name 
    
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=product_image_path, max_length=400, null=True, blank=True)
    alt_text = models.CharField(max_length=255, blank=True)
    is_featured = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Image for {self.product.name}'

### Scalable ###

class Attribute(models.Model):
    name = models.CharField(max_length=50)  # e.g., Color, Size, Material

    def __str__(self):
        return self.name

class AttributeValue(models.Model):
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, related_name='values')
    value = models.CharField(max_length=50)  # e.g., Red, XL, Cotton

    def __str__(self):
        return f"{self.attribute.name}: {self.value}"

class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    sku = models.CharField(max_length=100, unique=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    discount = models.DecimalField(max_digits=10, default=0.0, blank=True, null=True, decimal_places=2)
    old_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    identifiant = models.CharField(null=False, default="name")

    def save(self, force_insert = False , *args, **kwargs):
        if not self.sku:
            self.sku = f'SKU-{uuid.uuid1().hex[:8].upper()}'
        
        self.discount = 100 - (self.price * 100) / self.old_price if self.old_price > 0 else 0.0
        super().save(force_insert=force_insert, *args, **kwargs)
        
    def __str__(self):
        return f"{self.identifiant}"

class VariantImage(models.Model):
    variant = models.ForeignKey(ProductVariant, related_name='variant_image', on_delete=models.Case)
    image = models.ImageField(upload_to=variant_product_image_path)
    alt_text = models.CharField(max_length=255, blank=True)
    is_main = models.BooleanField(default=False)

    def __str__(self):
        return f'Image of {self.variant.product.name} - {self.variant.identifiant}'

class VariantAttribute(models.Model):
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='attributes')
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE)
    value = models.ForeignKey(AttributeValue, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('variant', 'attribute')

    def __str__(self):
        return f"{self.variant} | {self.attribute.name} = {self.value.value}"

