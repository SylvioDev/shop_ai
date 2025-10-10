from .repositories import ProductRepository
from django.urls import reverse
from .models import Category
from ..utils import get_full_image_url

class ProductService:
    """
    Service layer handling business logic for product-related operations.

    This class coordinates higher-level application workflows involving
    products, such as filtering and calculation before data
    is returned to views. It relies on the ProductRepository for
    database access, maintaining a clear separation between domain logic
    and persistence.

    Attributes:
        retpository (ProductRepository) : The repository instance used for
            database interactions.

    Methods:
        filter_products_by_category(category : str) :
            Returns products filtered by the specified category
        
        list_products() :
            Returns list of all active products
        
        update_product_variant(request, sku : str):
            Returns product variant details with its attributes
        
        calculate_discount(product : Product | ProductVariant):
            Returns product's discount in percent

    """
    def __init__(self):
        self.repository = ProductRepository()
    
    def filter_products_by_category(self, category : str) -> list | str:
        """
        Filter products belonging to a specific product.

        Args:
            category (str): product category

        Returns:
            list : list of products
        """
        if category == 'All':
            products = self.repository.get_all_products()
        else:
            try:
                products = self.repository.get_by_category(category)
            except Category.DoesNotExist:
                return 'Error'
                    
        product_data = []
        for product in products:
            product_data.append({
                'id' : product.id,
                'name' :  product.name,
                'category' : product.category.name,
                'stock' : product.stock,
                'price' : product.price,
                'old_price' : product.old_price,
                'discount' : product.discount,
                'image_url' : product.images.first().image.url,
                'product-url' : f'{reverse('products')}{product.slug}'
            })

        return product_data
    
    def list_products(self) -> dict:
        """
        List of all active products inside database with all categories

        Returns:
            dict with the following format : 
                {
                    'products' : list of all products,
                    'categories' : list of all categories 
                }
        """
        products = self.repository.get_all_products()
        categories = self.repository.get_all_category()
        data = {
            'products' : products,
            'categories' : categories
        }

        return data

    def calculate_discount(self, product : object) -> float:
        """
        Calculate product discount

        Args:
            product (object): product model => Product | ProductVariant

        Returns:
            product discount in percent
        """
        output = 100 - (product.price * 100) / product.old_price
        return output 

    def update_product_variant(self, sku : str) -> dict:
        """
        Update product detail page with selected product.
        Show additional attributes for variant.

        Args:
            sku (str): product sku

        Returns:
            dict : products informations
        """
        product_dict = ProductRepository().get_by_sku(sku)
        product_variant = product_dict['product']
        if product_dict['product_type'] == 'variant':
            variant_images = ProductRepository().get_product_image(sku)
            attributes = ProductRepository().get_variant_attribute(product_variant)
        
            full_image_url = variant_images    
            data = {
                'product_type' : 'variant',
                'title' : str(product_variant),
                'price' : product_variant.price,
                'stock' : product_variant.stock,
                'old_price' : product_variant.old_price,
                'attributes' : attributes,
                'image' : full_image_url
            }
            
        else:
            product = product_variant
            data = {
                'product_type' : 'base',
                'title' : product.name,
                'price' : product.price,
                'stock' : product.stock,
                'old_price' : product.old_price,
                'image' : ProductRepository().get_product_image(sku)
            }

        return data
            