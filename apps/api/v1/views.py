from .serializers import ProductSerializer
from .serializers import RegisterSerializer
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.filters import SearchFilter
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import JSONParser
from django_filters.rest_framework import DjangoFilterBackend
from apps.products.models import Product
from apps.api.v1.custom_filters import ProductFilter
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

class RegisterJSONView(APIView):
    """
    Viewset for user registration

    Provides an endpoint for user to register in database.

    Methods:
        post (request) : Handle post requests 
    """
    parser_classes = [JSONParser]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message':'User successfully registered via JSON'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    



