from django.http import JsonResponse
from django.views.generic import ListView
from django.views.generic import DetailView
from .models import Product
from .models import *
from django.contrib.sites.shortcuts import get_current_site
from shop_ai.settings import MEDIA_URL
from django.http import HttpResponse
from django.shortcuts import render
from .services import ProductService
from .repositories import ProductRepository

def filter_category(request, category : str):
    """
    Retrieve and display products belonging to a specific category

    This view handles filtering products based on the provided category name.

    Args:
        category (str): The category name used to filter products.
        Must match an existing category in the database.

    Returns:
        - A JSON response containing the list of filtered products if successful.
        If category is All , returns all products inside database.
        
        - A JSON response with a message error if category doesn't exists in database.
    
        
    """
    if request.method == 'POST' or request.method == 'GET':
        products = ProductService().filter_products_by_category(category)
        if products == 'Error':
            return JsonResponse({
                'status' : 'error',
                'message' : f"Category '{category}' doesn't exist"
            })
        else:
            return JsonResponse({
            'status' : 'success',
            'products' : products
         })

class ListProductsView(ListView):
    """
    Display a list of active products with optional filtering.

    This Class Based View retrieves all products and categories from database.
    It can optionally fitler based on query parameter category. The view supports both
    HTML and JSON responses depending on the request type

    Attributes:
        model (Product) : database model for products retrieval
        context_object_name (str) : label used for listing
        template_name (str) : HTML page to display all products

    Method:
        get(request) :
            Handles GET requests and return a list of products
    """
    model = Product
    context_object_name = 'products'
    template_name = 'products.html'

    def get(self, request): 
        data = ProductService().list_products()
        return render(
            request, 
            self.template_name , 
            {
                'products' : data['products'],
                'categories' : data['categories'],
                'count' : len(request.session.get('cart', {})),
            }
        )

class ProductDetail(DetailView):
    """
    Display a product with all its attributes.

    This Class Based View retrieves all products attributes from database.
    It also retrieves variants if latter exists. The view supports both
    HTML and JSON responses depending on the request type

    Attributes:
        model (Product) : database model for products retrieval
        context_object_name (str) : label used for listing
        template_name (str) : HTML page to display all products

    Method:
        get(request) :
            Handles GET requests and return product details
    """
    model = Product
    template_name = 'product_detail.html'

    def get(self, request : HttpResponse, slug : str):
        try:
            product = Product.objects.get(slug=slug)
        except Product.DoesNotExist:
            return JsonResponse({'message' : f'Product with slug "{slug}" does\'t exist'})

        variants = ProductVariant.objects.filter(product=product)
        attributes = ProductRepository().get_variant_attribute(variants[0].id) if len(variants) > 0 else None
        cart = request.session.get('cart', {})
        output = {
            'product' : product,
            'variants' : variants,
            'count' : len(cart)
        }
        
        if attributes:
            output['attributes'] = attributes
        return render(
            request, 
            self.template_name, 
            output
        )
        
def update_variant(request, product_sku : str) -> JsonResponse:
    """
    View that handles variant update when selecting another product

    Args:
        product_sku (str): product sku

    Returns:
        JsonResponse: a dict data with message to indicate if it's a variant or a base product.

    """
    result = ProductService().update_product_variant(product_sku)
    output = result
    output['status'] = 'success'
    output['message'] = 'variant' if output['product_type'] == 'variant' else 'no-variant'
    return JsonResponse(output)
