from rest_framework import serializers
from apps.products.models import Product
from apps.products.models import Category
from apps.users.models import Address
from django.contrib.auth.models import User
from apps.container import container
class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer for Product model.

    Handles validation and transformation of Product data between
    the API and the database.

    Fields:
        id (int): Unique identifier (read-only).
        name (str): Name of the product.
        price (Decimal): Product price (must be positive).
        description (str): Optional product description.
        
    Methods:
        validate_price(value):
            Ensures the price is a positive value.
    """
    category = serializers.SlugRelatedField(
        slug_field='name',
        queryset=Category.objects.all(),
    )
    class Meta:
        model = Product
        fields = ['name', 'slug', 'description', 'price', 'stock', 'status', 'category']


    def validate_price(self, value):
        """Check that the price is not a negative value"""
        if value < 0:
            raise serializers.ValidationError('Price must be positive.')
        return value

        
class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.

    This serializer handles validation and creation of new user accounts.
    It ensures that the provided email is unique and that the password
    is stored securely using Django's built-in hashing mechanism.

    Fields:
        username (str): Unique username for the user.
        email (str): User's email address (must be unique).
        password (str): Raw password (write-only).

    Methods:
        validate_email(value):
            Ensures the email is not already registered.

        create(validated_data):
            Creates and returns a new user instance with a hashed password.
    """
    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def validate_email(self, value):
        """Check that the email is not already in use."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email already in use.')
        return value
    
    def create(self, validated_data):
        """Create a new user with a hashed password"""
        user = container.signup_repo.create(**validated_data)
        user.is_active = True
        container.user_repo.create_user_address(user.id)
        user.save()
        return user

    