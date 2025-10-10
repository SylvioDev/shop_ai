from .models import Product
from .models import ProductVariant
from .models import Category
from .models import VariantImage
from .models import VariantAttribute
from django.db.models import QuerySet

class ProductRepository:
    """
    Repository class responsible for database operations related to products.

    This class encapsulates all data access login for both Product and ProductVariant model.
    It helps separate persistence concerns from business logic, improving code maintainability
    and testability.

    Methods:
        get_all_products () -> QuerySet[Product]
        get_all_categories() -> QuerySet[Product]
        get_by_category(category : str) -> QuerySet[Product]
    
    """
    def get_all_products(self) -> QuerySet[Product]:
        """
        Retrieve all active products from the database.
        
        Returns :
            QuerySet : All active products objects.

        """
        products = Product.objects.select_related('category').filter(status='published')
        return products

    def get_all_category(self,) -> QuerySet[Product]:
        """
        Retrieves all category from the database
        
        Returns:
            QuerySet : All categories that exists in the database

        """
        categories = Category.objects.prefetch_related('products').all()
        return categories

    def get_by_category(self, category_name : str) -> QuerySet[Product] | str:
        """
        Retrieve all active products belonging to a specific category.
        
        Args:
            category (str) : The category name to filter by.

        Returns :
            QuerySet : Active Product objects within the given category.

        Raises:
            Category.DoesNotExist: If the specified category does not exists

        """
        category = Category.objects.get(name=category_name)
        products = Product.objects.filter(category=category)
        return products

    def get_by_sku(self, sku : str) -> str | dict:
        """
        Retrieve a product (base or variant) by SKU.
        
        Args:
            sku (str) : product' sku

        Returns :
            dict : The product object and product_type if found
        
        Raises :
            ValueError : if there is no product found

        """
        sku = str(sku).strip()
        product = Product.objects.filter(sku=sku).first() \
                or ProductVariant.objects.filter(sku=sku).first()
        if not product:
            raise ValueError(f"Product with SKU '{sku}' not found")
        
        try:
            name = product.name
            return {'product_type':'base', 'product':product}
        except AttributeError:
            pass 

        return {'product_type':'variant', 'product':product}

    def get_product_image(self, sku : str) -> QuerySet[Product]:
        product = self.get_by_sku(sku)['product']
        """
        Returns all images of a product (base or variant)
        
        Args:
            sku (str): product's sku

        Returns:
            output (list) : list of images
        """
        
        try:
            output = str(VariantImage.objects.filter(variant=product)[0].image.url)
            return output
        except ValueError:
            pass 
        
        output = str(product.images.first().image.url)
        return output

    def get_variant_attribute(self, product_variant_id):
        """
        Returns attributes of a variant product 
        
        Args:
            product_variant_id (int): primary key of variant product

        Returns:
            output (dict) : Attributes of product variant
        """
        
        try:
            attributes = VariantAttribute.objects.filter(variant_id=product_variant_id)
        except ValueError:
            return {}
        output = {}
        for attr in attributes:
            output[attr.attribute.name] = attr.value.value
        return output


