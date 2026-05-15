from .serializers import (
    ProductSerializer,
    RegisterSerializer,
    UserSerializer,
    ProductImageSerializer,
    UserProfileSerializer,
    ProductVariantSerializer,
    ProductVariantImageSerializer
)
from apps.api.v1.custom_permissions import (
    ProductPermission,
    UserPermission,
    UserProfilePermission
)
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.filters import SearchFilter
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import JSONParser
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import User
from apps.users.models import UserProfile
from apps.products.models import Product
from apps.products.models import ProductVariant
from apps.api.v1.custom_filters import ProductFilter
from apps.api.v1.custom_filters import VariantFilter
from .custom_mixins import ImageMixin
class ProductPagination(PageNumberPagination):
    page_size = 3
    max_page_size = 5
    invalid_page_message = 'Page {page_number} does not exist.'
class ProductViewSet(ImageMixin, viewsets.ModelViewSet):
    """
    ViewSet for managing products.

    Provides standard CRUD operations:
    - list: Retrieve all products
    - retrieve: Get a single product by slug
    - create: Add a new product
    - update / partial_update: Modify an existing product (including product images)
    - destroy: Delete a product

    Queryset:
        All Product instances.

    Serializer:
        Uses ProductSerializer for validation and representation.

    Permissions:
        Can be customized (e.g., read-only for unauthenticated users,
        write access for admins).
    """
    queryset = Product.objects.all().order_by('-status')
    serializer_class = ProductSerializer
    filterset_class = ProductFilter
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['name', 'stock']
    search_fields = ['name']
    ordering_fields = ['price']
    lookup_field = 'slug'
    pagination_class = ProductPagination
    image_serializer_class = ProductImageSerializer
    permission_classes = [ProductPermission]
    image_fk_field = 'product'

class ProductVariantViewSet(ImageMixin, viewsets.ModelViewSet):
    """
    ViewSet for managing products variants.

    Provides standard CRUD operations:
    - list: Retrieve all products
    - retrieve: Get a single product by identifiant
    - create: Add a new product
    - update / partial_update: Modify an existing variant product (including variant images)
    - destroy: Delete a product

    Queryset:
        All ProductVariant instances.

    Serializer:
        Uses ProductVariantSerializer for validation and representation.

    Permissions:
        Can be customized (e.g., read-only for unauthenticated users,
        write access for admins).
    """
    queryset = ProductVariant.objects.all().order_by('-price')
    serializer_class = ProductVariantSerializer
    filterset_class = VariantFilter
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['identifiant', 'stock']
    search_fields = ['identifiant']
    ordering_fields = ['price']
    lookup_field = 'identifiant'
    pagination_class = ProductPagination
    image_serializer_class = ProductImageSerializer
    permission_classes = [ProductPermission]
    image_fk_field = 'variant'
    image_serializer_class = ProductVariantImageSerializer
class RegisterJSONView(APIView):
    """
    Viewset for user registration

    Provides an endpoint for user to register in database.

    Methods:
        post (request) : Handle post requests 
    """
    parser_classes = [JSONParser]

    def post(self, request):
        """Handle post"""
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message':'User successfully registered via JSON'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserViewset(viewsets.ModelViewSet):
    """
    ViewSet for managing users.

    Provides standard CRUD operations:
    - list: Retrieve all users
    - retrieve: Get a single product by username
    - create: Add a new user
    - update / partial_update: Modify an existing user
    - destroy: Delete an user

    Queryset:
        All User instances.

    Serializer:
        Uses UserSerializer for validation and representation.

    Permissions:
        Can be customized (e.g., read-only for unauthenticated users,
        write access for admins).
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [UserPermission]
class UserProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user profiles.

    Provides standard CRUD operations:
    - list: Retrieve all profiles
    - retrieve: Get a single product by username
    - create: Add a new profile
    - update / partial_update: Modify an existing profile (including profile picture)
    - destroy: Delete a profile

    Queryset:
        All Userprofile instances.

    Serializer:
        Uses UserProfileSerializer for validation and representation.

    Permissions:
        Can be customized (e.g., read-only for unauthenticated users,
        write access for admins).
    """
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [UserProfilePermission]

    