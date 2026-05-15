from rest_framework import serializers
from apps.products.models import Product
from apps.products.models import Category
from apps.products.models import ProductVariant
from apps.products.models import ProductImage
from apps.products.models import VariantImage
from apps.users.models import UserProfile
from django.contrib.auth.models import User
from apps.container import container
import re
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

class ProductVariantSerializer(serializers.ModelSerializer):
    """
    Serializer for ProductVariant model.

    Handles validation and transformation of ProductVariant data between
    the API and the database.

    Fields:
        identifiant (str): Name of variant.
        price (Decimal) : ProductVariant price (must be positive).
        stock (Decimal) : available quantity in database.
        sku(str) : String to identify each variant.

    Methods:
        validate_price(value):
            Ensures the price is a positive value.
    """
    class Meta:
        model = ProductVariant
        fields = ['identifiant', 'price', 'stock', 'sku']

class ProductImageSerializer(serializers.ModelSerializer):
    """
    Serializer for product image objects.

    This serializer handles the representation of images associated
    with a product, including the image file and the upload timestamp.

    Attributes:
        Meta:
            model (ProductImage):
                The model associated with this serializer.
            fields (list[str]):
                Fields included in the serialized output:
                - image: The uploaded product image.
                - uploaded_at: Timestamp indicating when the image was uploaded.
    """
    class Meta:
        model = ProductImage
        fields = ['image', 'uploaded_at']

class ProductVariantImageSerializer(serializers.ModelSerializer):
    """
    Serializer for product variant image objects.

    This serializer is responsible for serializing images linked
    to a specific product variant.

    Attributes:
        Meta:
            model (VariantImage):
                The model associated with this serializer.
            fields (list[str]):
                Fields included in the serialized output:
                - image: The uploaded variant image.
    """
    class Meta:
        model = VariantImage
        fields = ['image']

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

class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile objects.

    This serializer manages the serialization and deserialization
    of user profile data, including social media information,
    phone number validation, linked user reference, and profile picture.

    Attributes:
        user (SlugRelatedField):
            Represents the related user object using its unique ID.

    Meta:
        model (UserProfile):
            The model associated with this serializer.
        fields (list[str]):
            Fields included in the serialized output:
            - social_media_username: User's social media handle.
            - phone_number: User's validated phone number.
            - user: Related user identifier.
            - profile_picture: User profile image.
    """
    user = serializers.SlugRelatedField(
        slug_field='id',
        queryset=User.objects.all(),
    )
    class Meta:
        model = UserProfile
        fields = ['social_media_username', 'phone_number', 'user', 'profile_picture']
        
    def validate_phone_number(self, value : str):
        """
        Validate the provided phone number format.

        Ensures that the phone number matches the expected
        Malagasy mobile phone number format:
        03(2|3|4|7|8) xx xxx xx

        Args:
            value (str):
                The phone number to validate.

        Returns:
            str:
                The validated phone number.

        Raises:
            ValueError:
                If the phone number format is invalid.
        """
        pattern = re.fullmatch(r'(032|033|034|037|038) \d{2,2} \d{3,3} \d{2,2}$', value)
        if not pattern:
            raise ValueError('Phone number should be 03(2|3|4|7|8) xx xxx xx')
        return value

    def update(self, instance, validated_data):
        """
        Update an existing user profile instance.

        Updates the editable fields of a user profile using
        validated serializer data.

        Args:
            instance (UserProfile):
                The existing user profile instance to update.
            validated_data (dict):
                Dictionary containing validated input data.

        Returns:
            UserProfile:
                The updated user profile instance.
        """
        instance.phone_number = validated_data.get(
            'phone_number', 
            instance.phone_number
        )
        instance.social_media_username = validated_data.get(
            'social_media_username', 
            instance.social_media_username
        )
        instance.profile_picture = validated_data.get(
            'profile_picture', 
            instance.profile_picture
        )
        instance.save()
        return instance
class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user objects.

    This serializer provides a representation of the application's
    user model along with its associated profile information.

    Attributes:
        profile (UserProfileSerializer):
            Nested read-only serializer containing the related
            user profile details.

    Meta:
        model (User):
            The model associated with this serializer.
        fields (list[str]):
            Fields included in the serialized output:
            - username: User's unique username.
            - email: User's email address.
            - first_name: User's first name.
            - last_name: User's last name.
            - profile: Associated user profile information.
    """
    profile = UserProfileSerializer(source='userprofile', read_only=True)
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'profile']


    