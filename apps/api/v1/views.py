from .serializers import ProductSerializer
from .serializers import RegisterSerializer
from .serializers import UserSerializer
from .serializers import UserProfileSerializer
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.filters import SearchFilter
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import JSONParser
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import User
from apps.users.models import UserProfile
from apps.products.models import Product
from apps.api.v1.custom_permissions import ProductPermission
from apps.api.v1.custom_permissions import UserPermission
from apps.api.v1.custom_permissions import UserProfilePermission
from apps.api.v1.custom_filters import ProductFilter
import json
class ProductPagination(PageNumberPagination):
    page_size = 3
    max_page_size = 5
    invalid_page_message = 'Page {page_number} does not exist.'
class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing products.

    Provides standard CRUD operations:
    - list: Retrieve all products
    - retrieve: Get a single product by ID
    - create: Add a new product
    - update / partial_update: Modify an existing product
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
    filterset_fields = ['stock', 'name']
    search_fields = ['name']
    ordering_fields = ['price']
    lookup_field = 'slug'
    pagination_class = ProductPagination
    permission_classes = [ProductPermission]

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
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [UserPermission]
class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [UserProfilePermission]

    """
    @action(detail=False, methods=['get', 'put', 'patch'])
    def profile(self, request):
        user_id = request.query_params.get('id')
        if not user_id:
            return Response({'message':'You must provide an id parameter'})
        try:
            user_profile = UserProfile.objects.get(user=user_id)
            print(user_profile)
            # Checking permissions
            self.check_object_permissions(request, user_profile)

            if request.method == 'GET':
                serializer = UserProfileSerializer(user_profile)
                return Response({'message':'User infos', 'data':serializer.data}, status=status.HTTP_200_OK)
            elif request.method == 'PATCH':
                serializer = UserProfileSerializer(instance=user_profile, data=request.data, partial=True)
            elif request.method == 'PUT':
                serializer = UserProfileSerializer(instance=user_profile, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({'message':'User updated succesfully'}, status=status.HTTP_200_OK)
            else:
                return Response({'message' : serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except (UserProfile.DoesNotExist, Exception) as error:
            return Response({'message': str(error)}, status=status.HTTP_404_NOT_FOUND)
        
    """