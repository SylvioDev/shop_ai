import pytest 
from apps.products.models import (
    Category, 
    Product, 
    ProductVariant, 
    VariantImage
)
from apps.conftest import(
    sample_products,
    product,
    variant_product,
    sku,
    variant_sku,
    pytestmark
)
from django.db.models import QuerySet
from apps.container import container
@pytest.mark.django_db
class TestProductRepository:
    def test_get_product_by_category_failed(self, sample_products):
        category_name = 'unknown'
        with pytest.raises (Category.DoesNotExist) as exc_info:
            container.product_repo.get_by_category(category_name)
        
        assert 'Category matching query does not exist.' in str(exc_info)

    def test_get_product_by_category_success(self, sample_products):
        category_name = 'Clothe'
        products = container.product_repo.get_by_category(category_name)
        assert isinstance(products, QuerySet)
        assert len(products) == 2
        
    def test_get_all_category(self, sample_products):
        categories = container.product_repo.get_all_category()
        assert isinstance(categories, QuerySet)
        assert len(categories) == 3

    def test_get_all_products(self, sample_products):
        products = container.product_repo.get_all_products()
        assert isinstance(products, QuerySet)
        assert len(products) == 5
        for product in products:
            assert product.status == 'published'

    def get_by_sku_variant(self, variant_sku, variant_product):
        result = container.product_repo.get_by_sku(variant_sku)
        assert isinstance(result, dict)
        assert result['product_type'] == 'variant'
        assert isinstance(result['product'], ProductVariant)
        assert result['product'] == variant_product
        
    def get_by_sku_base(self, sku, product):
        result = container.product_repo.get_by_sku(sku)
        assert isinstance(result, dict)
        assert result['product_type'] == 'base'
        assert isinstance(result['product'], Product)
        assert result['product'] == product
    
    def test_get_by_sku_failed(self, product):
        invalid_sku = 'invalid_sku'
        with pytest.raises(ValueError) as exc_info:
            container.product_repo.get_by_sku(invalid_sku)

        assert f"Product with SKU '{invalid_sku}' not found" == str(exc_info.value)
    
    def test_get_base_image(self, sku, product):
        result = container.product_repo.get_product_image(sku)
        assert isinstance(result, str)
        assert product.images.first().image.url == result
    
    def test_get_variant_image(self, variant_sku, variant_product):
        result = container.product_repo.get_product_image(variant_sku)
        variant_image_url = VariantImage.objects.filter(variant=variant_product)[0].image.url
        assert isinstance(result, str)
        assert  variant_image_url == result
    
    @pytest.mark.parametrize(
        'product_id, expected_output',
        [
            (1, {'Color':'Red','Size':'XL','Material':'Coton'}),
            (0, {}),
            (8, {}) # product that doesn't exist
        ]
    )
    
    def test_get_variant_attributes(self, variant_product, product, product_id, expected_output):
        result = container.product_repo.get_variant_attribute(product_id)
        assert result == expected_output
    
    def test_get_product_image(self, sku, product):
        result = container.product_repo.get_product_image(sku)
        assert result == product.images.first().image.url
    
    def test_get_variant_image(self, variant_sku, variant_product):
        result = container.product_repo.get_product_image(variant_sku)
        assert result == VariantImage.objects.filter(variant=variant_product)[0].image.url
    