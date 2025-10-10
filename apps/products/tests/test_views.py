import pytest
import json
from django.urls import reverse
from apps.conftest import \
(
    variant_sku,
    sku,
    variant_product,
    product,
    sample_products
)

pytestmark = pytest.mark.django_db

@pytest.fixture
def product_url():
    return reverse('products')

@pytest.fixture 
def active_products(products_lists):
    for product in products_lists:
        product.status == 'published'
    return products_lists

class TestListProductView:
    def test_list_product_get(self, client, product_url, product):
        response = client.get(product_url)
        html = response.content.decode('utf-8')
        template_name = response.templates[0].name
        assert response.status_code == 200
        assert template_name == 'products.html'
        assert response.context.get('products') is not None 
        assert response.context.get('categories') is not None
        assert response.context.get('count') is not None
        assert 'Blue Jeans' in html
    
class TestCategoryFilterView:
    def test_category_filter_all(self, client, sample_products):
        response = client.post(reverse('filter-category', kwargs={'category':'All'}))
        json_response = json.loads(response.content.decode())
        products = json_response.get('products')
        assert len(products) == 5
    
    def test_category_filter_food(self, client, sample_products):
        """Filter all food products """
        response = client.post(reverse('filter-category', kwargs={'category':'Food'}))
        json_response = json.loads(response.content.decode())
        products = json_response.get('products')
        assert len(products) == 2
        assert products[0]['name'] == 'Yogurt'
        assert products[1]['name'] == 'Red Velvet Cake'
    
    def test_category_filter_invalid(self, client, sample_products):
        invalid_category = 'invalid'
        response = client.post(reverse('filter-category', kwargs={'category': invalid_category}))
        json_response = json.loads(response.content.decode())
        assert json_response.get('status') == 'error'
        assert json_response.get('message') == f"Category '{invalid_category}' doesn't exist"
        
class TestProductDetailView:
    def test_product_detail_get_success(self, client, product):
        response = client.get(reverse('product-detail', kwargs={'slug' : product.slug}))
        template_name = response.templates[0].name
        assert response.status_code == 200
        assert template_name == 'product_detail.html'

    def test_product_detail_get_failure(self, client, product):
        invalid_slug = 'invalid product'
        response = client.get(reverse('product-detail', kwargs={'slug' : invalid_slug}))
        error = json.loads(response.content.decode())
        assert response.status_code == 200
        assert error['message'] == f'Product with slug "{invalid_slug}" does\'t exist'

    def test_product_detail_variant(self, client, variant_product, variant_sku):
        response = client.get(reverse('update-variant', kwargs={'product_sku':variant_sku}))
        json_response = json.loads(response.content.decode()) 
        attributes = json_response.get('attributes')
        assert 'attributes' in json_response
        assert attributes['Color'] == 'Red'
        assert attributes['Size'] == 'XL'
        assert attributes['Material'] == 'Coton'