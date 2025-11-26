import pytest
from django.urls import reverse
from apps.conftest import (
    valid_user,
    sku,
    variant_sku,
    product,
    variant_product
)
import json
from apps.cart.cart import Cart

pytestmark = pytest.mark.django_db

@pytest.fixture
def home_url():
    return reverse('home')

@pytest.fixture
def login_url():
    return reverse('login')

@pytest.fixture
def log_user(client, valid_user, home_url, login_url):
    data = {
            'identifier' : 'test',
            'password' : 'mypassword'
    }
    response = client.get(home_url)
    other_response = client.post(
        login_url, 
        data={
            'identifier':'test', 
            'password':'mypassword', 
            'next':home_url
        }
    )
    third_response = client.get(other_response.url)
    
    
class TestCheckoutHomePage:
    def test_homepage_redirect_not_authenticated(self, client, home_url):
        response = client.get(home_url)
        assert response.status_code == 302
        # user should sign in before accesing to checkout page
        assert response.url == '/accounts/login/?next=/checkout/'
    
    def test_homepage_renders_authenticated(self, client, home_url, login_url, valid_user):
        response = client.get(home_url)
        other_response = client.post(login_url, data={'identifier':'test', 'password':'mypassword', 'next':home_url})
        assert other_response.status_code == 302
        assert other_response.url == '/checkout/'
        third_response = client.get(other_response.url)
        assert third_response.status_code == 200
        template_name = third_response.templates[0].name
        assert template_name == 'checkout.html'
        template = third_response.content.decode()
        assert 'Cart review' in template
        context = third_response.context[0]
        assert 'user_address' in context
        assert 'cart' in context
        assert 'count' in context
        assert 'cart_summary' in context
    
    #### cart review ####
    
@pytest.fixture
def cart_url():
    return reverse('review')
    
class TestCartReview:
    def test_cart_review_empty_cart(self, client, cart_url, log_user):
        response = client.get(cart_url)
        assert response.status_code == 400
        content = json.loads(response.content.decode())
        error_message = content.get('error')
        assert error_message == 'Your cart is empty. Add items to proceed.'
    
    def test_cart_review_not_enough_stock(self, client, cart_url, log_user, product, sku):
        cart = Cart({})
        params = {
            'product_sku' : sku,
            'product_quantity' : 5
        }
        response = client.post(reverse('cart-add', kwargs=params))
        cart.add(sku, quantity=4)
        product.stock = 0
        product.save()
        response = client.get(cart_url)
        assert response.status_code == 400
        error_message = json.loads(response.content.decode()).get('error')
        assert 'Not enough stock for "Blue Jeans" . Only 0 left' in error_message
        
    def test_cart_review_valid(self, client, cart_url, log_user, product, sku):
        cart = Cart({})
        params = {
            'product_sku' : sku,
            'product_quantity' : 5
        }
        response = client.post(reverse('cart-add', kwargs=params))
        cart.add(sku, quantity=4)
        response = client.get(cart_url)
        assert response.status_code == 200
        success_message = json.loads(response.content.decode()).get('message')
        assert success_message == 'cart is valid'

