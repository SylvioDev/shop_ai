import pytest
from apps.conftest import (
    sku,
    variant_sku,
    variant_product,
    product,
    sample_products
)
from apps.products.models import Category
from apps.products.services import ProductService

pytestmark = pytest.mark.django_db

@pytest.fixture
def category():
    output = Category.objects.filter(name='Food')
    return output

class TestProductService:
    @pytest.mark.parametrize(
        'input_category, expected_count',
        [
            ('All', 5),
            ('Clothe', 2),
            ('High-Tech', 1),
            ('invalid_category', 'Error')
        ]
    )
    def test_filter_by_category(self, category, sample_products, input_category, expected_count):
        result = ProductService().filter_products_by_category(input_category)
        if isinstance(result, str):
            assert result == expected_count
        else:
            item = result[0]
            assert isinstance(result, list)
            assert len(result) == expected_count
            assert len(item.keys()) == 9
    
    def test_list_products(self, sample_products):
        result = ProductService().list_products()
        assert isinstance(result, dict)
        assert 'products' in result.keys()
        assert 'categories' in result.keys()
        assert len(result['products']) == 5
        assert len(result['categories']) == 3

    def test_calculate_discount(self, product):
        product.old_price = 18.00
        discount = ProductService().calculate_discount(product)
        assert isinstance(discount, float)
        assert round(discount) == 33

    def test_update_product_variant(self, variant_sku, variant_product):
        result = ProductService().update_product_variant(variant_sku)
        assert isinstance(result, dict)
        assert result['product_type'] == 'variant'
        assert result['title'] == variant_product.identifiant
        assert result['price'] == variant_product.price
        assert result['stock'] == variant_product.stock
        assert result['old_price'] == variant_product.old_price
        assert result['attributes'] == {
            'Color':'Red',
            'Size':'XL',
            'Material':'Coton'
        }
    
    def test_update_product_variant_base(self, sku, product):
        result = ProductService().update_product_variant(sku)
        assert isinstance(result, dict)
        assert result['product_type'] == 'base'
        assert result['title'] == product.name
        assert result['price'] == product.price
        assert result['stock'] == product.stock
        assert result['old_price'] == product.old_price