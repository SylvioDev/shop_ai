from .serializers import (
    ProductSerializer,
    RegisterSerializer,
    UserSerializer,
    ProductImageSerializer,
    UserProfileSerializer,
    ProductVariantSerializer,
    ProductVariantImageSerializer,
    OrderSerializer
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
from apps.cart.models import Cart
from apps.orders.models import Order
from apps.orders.models import OrderItem

from apps.api.v1.custom_filters import ProductFilter
from apps.api.v1.custom_filters import VariantFilter

from .custom_mixins import ImageMixin
from rest_framework.permissions import IsAuthenticated
from .serializers import CartSerializer
from .custom_mixins import CartMixin

from apps.container import container
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
class CartView(CartMixin, APIView):
    """
    Handles cart operations for authenticated users.
    
    Supports retrieving, adding, removing, and updating cart items.
    Cart is persisted in the database via CartMixin helpers.
    
    Endpoints:
        GET    /cart/              → retrieve cart items
        POST   /cart/              → add product to cart
        DELETE /cart/              → remove a product from cart
        PATCH  /cart/              → update product quantity
    """
    permission_classes = [IsAuthenticated]
    serializer_class = CartSerializer

    def get(self, request):
        """
        Retrieve all items in the authenticated user's cart.

        Returns:
            200: cart items dict
        """
        cart, _ = Cart.objects.get_or_create(user=request.user)
        return Response(cart.items)

    def post(self, request):
        """
        Add a product to the cart by SKU.

        Body:
            product_sku (str): SKU of the product to add
            quantity (int): desired quantity

        Returns:
            200: success message
            400: missing product_sku or quantity
            404: product SKU not found in database
        """
        product_sku = request.data.get('product_sku')
        quantity = int(request.data.get('quantity'))
        if not product_sku or not quantity:
            return Response({'error': 'missing data!'}, status=status.HTTP_400_BAD_REQUEST)

        cart_dict, db_cart ,fake_session = self._get_cart(request)
        response = cart_dict.add(product_sku, quantity)
        if 'SKU' in str(response):
            return Response({'error': str(response)}, status=status.HTTP_404_NOT_FOUND)
        
        self._save_cart(db_cart, cart_dict.cart)

        return Response({'message' : f'Product "{product_sku}" added successfully'}, status=status.HTTP_200_OK)

    def delete(self, request):
        """
        Remove a product from the cart by SKU.

        Query Params:
            product_sku (str): SKU of the product to remove

        Returns:
            200: success message
            400: missing product_sku
            404: product not found in cart
        """
        product_sku = request.query_params.get('product_sku')
        if not product_sku:
            return Response({'error': 'missing data!'}, status=status.HTTP_400_BAD_REQUEST)

        cart_dict, db_cart, fake_session = self._get_cart(request)
        response = cart_dict.remove(product_sku)
        
        if 'exist' in response:
            return Response({'error': str(response)}, status=status.HTTP_404_NOT_FOUND)
        
        self.save_cart(db_cart, cart_dict.cart)

        return Response({'message': response})

    def patch(self, request):
        """
        Update the quantity of a product already in the cart.

        Body:
            product_sku (str): SKU of the product to update
            quantity (int): new desired quantity

        Returns:
            200: success message
            400: missing product_sku or quantity
            404: product not found in cart
        """
        product_sku = request.data.get('product_sku')
        quantity = int(request.data.get('quantity'))

        if not product_sku or not quantity:
            return Response({'error': 'missing data!'}, status=status.HTTP_400_BAD_REQUEST)

        cart_dict, db_cart, fake_session = self._get_cart(request)
        response = cart_dict.update_product_quantity(product_sku, quantity)
        if response is None:
            return Response(f'error, there is no product with sku "{product_sku}"', status=status.HTTP_404_NOT_FOUND)
        
        self._save_cart(db_cart, cart_dict.cart)
        
        return Response({'message':f'Product updated successfully'}, status=status.HTTP_200_OK)

class CartClearView(CartMixin, APIView):
    """
    Clears all items from the authenticated user's cart.
    
    Typically called after a successful checkout.

    Endpoints:
        DELETE /cart/clear/  → wipe all cart items
    """
    permission_classes = [IsAuthenticated]
    
    def delete(self, request):
        """
        Remove all products from the cart.

        Returns:
            200: confirmation message
        """
        cart_dict, db_cart, fake_session = self._get_cart(request)
        cart_dict.clear()
        self._save_cart(db_cart, cart_dict.cart)
        return Response({'message' : 'Cart cleared'}, status=status.HTTP_200_OK)
    
class OrderViewSet(CartMixin, viewsets.ModelViewSet):
    """
    Handles order management for authenticated users.
    
    Inherits CartMixin for cart access helpers (_get_cart, _save_cart).
    Users can only see and manage their own orders.
    Orders are identified by order_number instead of pk.
    
    Endpoints:
        GET    /orders/                    → list authenticated user's orders
        GET    /orders/{order_number}/     → retrieve specific order
        POST   /orders/                    → create order from cart
        PATCH  /orders/{order_number}/     → pay a pending order
    """
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer
    lookup_field = 'order_number'

    def get_queryset(self):
        """
        Restrict queryset to authenticated user's orders only.
        
        Prevents users from accessing other users' orders.
        Unauthenticated access returns 404 instead of 403
        for security (doesn't reveal order existence).

        Returns:
            QuerySet: orders belonging to the current user
        """
        return Order.objects.filter(customer_id=self.request.user)

    def create(self, request, *args, **kwargs):
        """
        Create a new pending order from the authenticated user's cart.

        Rejects creation if cart is empty.
        Delegates order creation and item attachment to checkout_service.
        Order items are attached immediately at creation (not after payment)
        to preserve order history regardless of payment outcome.

        Args:
            request: HTTP request (no body required — order built from cart)

        Returns:
            200: success message + serialized order data
            400: empty cart or serializer validation errors
            
        Flow:
            cart → order_creation() → add_order_items() → return order
        """
        cart_dict, cart_db, fake_session = self._get_cart(request)

        if cart_dict.set_total_items() == 0 : # Empty cart
            return Response({f'error' : 'You cannot create order with empty cart'}, status=status.HTTP_400_BAD_REQUEST)

        order = container.checkout_service.order_creation(cart=cart_dict, user=request.user)
        serializer = self.get_serializer(instance=order, data=request.data)
        
        if serializer.is_valid():
            container.checkout_service.add_order_items(order=order, cart=cart_dict.cart)
            return Response(
                {
                    'message' : 'Order successfully created',
                    'data' : serializer.data
                },
                status=status.HTTP_200_OK
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        """
        Simulate a successful payment by transitioning order status to 'paid'.

        On successful payment:
            - Stock is decreased for each item in the order
            - Cart is cleared (both in-memory and in DB)
            - Order status is updated to 'paid'

        Rejects the request if:
            - order_number is missing from request body
            - order is already paid (immutable after payment)
            - order_number does not exist

        Args:
            request.data:
                order_number (str): unique identifier of the order to pay

        Returns:
            200: confirmation message
            400: missing order_number, already paid, or validation errors
            404: order not found

        Note:
            Payment processing (Stripe) is handled separately in the
            e-commerce website. This endpoint simulates payment success only.
        """
        order_number = request.data.get('order_number')
        if not order_number:
            return Response({'error' : 'You must provide a order_number '}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            order = Order.objects.get(order_number=order_number)
            if order.status == 'paid':
                return Response('This order is already paid', status=status.HTTP_400_BAD_REQUEST)
            
            serializer = self.get_serializer(instance=order, partial=True, data=request.data)

            if serializer.is_valid():
                cart_dict, cart_db, fake_session = self._get_cart(request)
                container.order_service.decrease_stocks(cart_dict.cart) # decreasing stock
                cart_dict.clear()
                cart_db.items = {} # clear cart
                cart_db.save()
                serializer.save()
                return Response('Order paid succesfully! Thank you for purchasing on shopai.com', status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Order.DoesNotExist as error:
            return Response(str(error), status=status.HTTP_404_NOT_FOUND)
        
        