from apps.container import container
import pytest
import stripe
from django.urls import reverse
from django.contrib.auth.models import User
from apps.conftest import (
    valid_user,
    sku,
    variant_sku,
    product,
    variant_product,
    cart_data,
    Cart,
    valid_user,
    payment_process_cart,
    mock_session,
    
)
import json
from apps.cart.cart import Cart
from apps.checkout.models import Payment
from apps.orders.models import Order
from apps.orders.models import OrderItem
from apps.checkout.custom_exceptions import (
    InvalidPayloadException,
    InvalidSignatureException
)
from unittest.mock import Mock
from django.conf import settings
from apps.conftest import pytestmark

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
    
@pytest.fixture
def fakes_pi():
    pi = Mock()
    pi.id = 'pi_12345'
    pi.latest_charge = 'ch_67890'
    pi.created = 1700000000
    pi.status = 'succeeded'
    return pi

class TestCheckoutHomePageView:
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
class TestCartReviewView:
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

### Payment fixtures ###

@pytest.fixture
def cart_session(client, payment_process_cart):
    cart = client.session['cart']
    cart_class = Cart(cart)
    cart_class.cart = cart
    del cart_class.cart['cart']
    return cart_class

@pytest.fixture
def fake_session(cart_session):
    session = Mock()
    session.id = 'cs_123'
    session.payment_intent = 'pi_487mpl41'
    session.url = f'{settings.DOMAIN_URL}/products'
    session.amount_total = int(cart_session.get_cart_summary()['total_price']) * 100 
    session.payment_status = 'paid'
    session.payment_method_types = ["card"]
    session.currency = 'usd'
    return session
class TestPaymentProcessingView:
    def test_payment_empty_cart(self, client, valid_user):
        login_response = client.post(reverse('login'), data={'identifier':'test', 'password':'mypassword', 'next':reverse('create-checkout-session')})
        with pytest.raises(ValueError) as exc_info:
            response = client.get(reverse('create-checkout-session'))
        assert 'Cart is empty. Cannot create checkout session.' == str(exc_info.value)
    
    def test_payment_success(self, mocker ,client, cart_session, valid_user, fake_session):
        client.force_login(valid_user)        
        mock_success = mocker.patch('stripe.checkout.Session.create', return_value=fake_session)
        response = client.get(reverse('create-checkout-session')) 

        assert response.status_code == 302
        assert response.url == fake_session.url
        mock_success.assert_called_once()
        
        # We assert everything here : order, payment and order_items
        # order assert
        order = Order.objects.get(customer_id=valid_user)
        assert order.customer_id == valid_user
        assert round(order.final_total) == round(fake_session.amount_total / 100)
        # payment assert
        payment = Payment.objects.get(order=order)
        assert payment.stripe_payment_intent_id == fake_session.payment_intent
        assert payment.stripe_session_id == fake_session.id      
        # order items assert
        order_items = OrderItem.objects.all()
        for order_item in order_items:
            assert order_item.order == order
class TestStripeWebhookView:
    def test_webhook_success(self, mocker, client):
        fake_payload = {
            'type':'checkout.session.completed',
            'data' : {
                'object':{
                    'id':'cs_test_187'
                }
            }
        }
        fake_payload_bytes = json.dumps(fake_payload).encode('utf-8')
        mocker.patch('apps.checkout.payment_service.StripePaymentService.handle_webhook', return_value=True)
        response = client.post(
            reverse('stripe_webhook'), 
            data=fake_payload_bytes,
            content_type='application/json',
            **{
                'HTTP_STRIPE_SIGNATURE' : 'test_signature'
            }
        )
        
        assert response.status_code == 200
    
    @pytest.mark.parametrize('exception, msg, status_code', [
        (InvalidPayloadException, 'Invalid payload', 400),
        (InvalidSignatureException, 'Invalid signature', 400)
    ])
    def test_webhook_failed(self, mocker, client, exception, msg, status_code):
        fake_payload = {
            'type':'checkout.session.completed',
            'data':{
                'object':{
                    'id' : 'cs_788'
                }
            }
        }
        fake_payload_bytes = json.dumps(fake_payload).encode('utf-8')
        mocker.patch('apps.checkout.payment_service.StripePaymentService.handle_webhook', side_effect=exception(msg))
        response = client.post(
            reverse('stripe_webhook'), 
            data=fake_payload_bytes,
            content_type='application/json',           
        )
        assert response.status_code == status_code
        assert msg == json.loads(response.content.decode('utf-8')).get('error')
        
class TestConfirmPageView:
    def test_confirm_page_renders(self, client, valid_user, payment_process_cart):
        response = client.get(reverse('confirm'))
        template_name = response.templates[0].name
        context = list(response.context[0])[0]
        keys = [
            'count', 'subtotal',
            'vat_rate', 'vat_total', 'shipping_fee',
            'total', 'payment_method', 'redirect_url'
        ]
        assert response.status_code == 200
        assert template_name == 'confirm.html'
        assert context['redirect_url'] == '/checkout/payment/'
        for key in keys:
            assert key in context 
        
    def test_confirm_page_post(self, client):
        response = client.post(reverse('confirm'))
        assert response.status_code == 302
        assert response.url == '/checkout/payment/'
    
class TestSuccessAndFailureView:
    @pytest.mark.parametrize('url', [
        reverse('success'),
        reverse('cancel')
    ])
    def test_view(self, client, url):
        response = client.get(url)
        assert response.status_code == 302
        assert response.get('order_id') is None
        assert response.get('session_id') is None
        assert response.url == '/checkout/payment_status/?order_id=None&session_id=None'

@pytest.fixture
def fake_orders(valid_user, cart_session):
    order = container.checkout_repo.create_order(
        user=valid_user,
        cart_data=cart_session.get_cart_summary(),
        total_amount=cart_session.get_cart_summary()['total_price']
    )
    return order

@pytest.fixture
def fake_payments(fake_orders, fake_session, cart_session):
    payment=container.checkout_repo.create_payment(
            order=fake_orders,
            payment_provider='stripe',
            amount=cart_session.get_cart_summary()['total_price']
        )
    payment.stripe_payment_intent_id = fake_session.payment_intent
    payment.stripe_session_id = fake_session.id
    payment.save()
    return payment

@pytest.fixture
def run_payment_status(mocker, client, valid_user, fakes_pi, fake_session):
    client.force_login(valid_user)
    mocker.patch("stripe.checkout.Session.retrieve", return_value=fake_session)
    mocker.patch("stripe.PaymentIntent.retrieve", return_value=fakes_pi)
        
class TestPaymentStatusView:
    def test_login_required(self, client):
        """
        Test that payment status view requires user to be logged in.
        """
        response = client.get(reverse('payment-status'))
        assert response.status_code == 302
        assert response.url == '/accounts/login/?next=/checkout/payment_status/'
    
    def test_payment_status_success(
        self, 
        mocker, 
        client, 
        valid_user, 
        cart_session, 
        fake_orders, 
        fake_payments, 
        fake_session, 
        fakes_pi
    ): 
        client.force_login(valid_user)
        mocker.patch("stripe.checkout.Session.retrieve", return_value=fake_session)
        mocker.patch("stripe.PaymentIntent.retrieve", return_value=fakes_pi)
        
        
        response = client.get(
            reverse('payment-status') + f'?order_id={fake_orders.order_number}&session_id={fake_session.id}'
        )
        template_name = response.templates[0].name
        context = response.context[0]
        assert response.status_code == 200
        assert template_name == 'payment_status.html'
        assert context['payment_status'] == 'paid'
        assert context['payment'] == fake_payments
        assert context['order'] == fake_orders
        assert context['count'] == 0
        assert client.session.get('cart') == {} # cart is cleared
        
    def test_payment_status_failure(
        self, 
        mocker, 
        client, 
        valid_user, 
        cart_session, 
        fake_session, 
        fake_orders, 
        fake_payments,
        fakes_pi
    ):
        
        client.force_login(valid_user)
        mocker.patch("stripe.checkout.Session.retrieve", return_value=fake_session)
        mocker.patch("stripe.PaymentIntent.retrieve", return_value=fakes_pi)
        
        # mock payment failure
        fake_session.payment_status = 'unpaid'
        fake_orders.failure_reason = 'Card was declined'
        fake_orders.save()
        
        response = client.get(
            reverse('payment-status') + f'?order_id={fake_orders.order_number}&session_id={fake_session.id}'
        )
        template_name = response.templates[0].name
        context = response.context[0]
        assert response.status_code == 500
        assert template_name == 'payment_status.html'
        assert context['failure_reason'] == fake_orders.failure_reason
        assert context['count'] == len(cart_session)    
    
    def test_payment_status_webhook_fallback(
        self, 
        mocker, 
        client, 
        valid_user, 
        cart_session, 
        fake_orders, 
        fake_payments, 
        fake_session, 
        fakes_pi
    ):
        """
        Test that payment status view handles webhook fallback correctly.
        """
        client.force_login(valid_user)
        mocker.patch("stripe.checkout.Session.retrieve", return_value=fake_session)
        mocker.patch("stripe.PaymentIntent.retrieve", return_value=fakes_pi)
        
        # Simulate that payment status is still pending
        fake_payments.status = 'pending'
        fake_payments.save()
        
        mock_handle_fallback = mocker.patch(
            'apps.checkout.services.CheckoutService.handle_webhook_fallback',
            return_value=(fake_orders, fake_payments)
        )
        
        response = client.get(
            reverse('payment-status') + f'?order_id={fake_orders.order_number}&session_id={fake_session.id}'
        )
        template_name = response.templates[0].name
        context = response.context[0]
        assert response.status_code == 200
        assert template_name == 'payment_status.html'
        assert context['payment_status'] == 'paid'
        assert context['payment'] == fake_payments
        assert context['order'] == fake_orders
        assert context['count'] == 0
        assert client.session.get('cart') == {} # cart is cleared
        mock_handle_fallback.assert_called_once()
    
    def test_payment_status_order_not_found(self, client, run_payment_status, fake_session):
        response = client.get(
            reverse('payment-status') + f'?order_id=fake_order&session_id={fake_session.id}'
        )
        
        json_response = json.loads(response.content.decode())
        assert response.status_code == 500
        assert json_response.get('status') == 'error'
        assert json_response.get('error') == 'Order matching query does not exist.'

    def test_payment_status_payment_not_found(self, client, fake_orders, run_payment_status, fake_session):
        response = client.get(
            reverse('payment-status') + f'?order_id={fake_orders.order_number}&session_id={fake_session.id}'
        )

        json_response = json.loads(response.content.decode())
        
        assert response.status_code == 500
        assert json_response.get('status') == 'error'
        assert json_response.get('error') == 'Payment matching query does not exist.'

    @pytest.mark.parametrize('exception', [
        stripe.APIConnectionError('Network communication with Stripe failed'),
        stripe.InvalidRequestError('Missing parameter "amount" ', 'bad param'),
        stripe.AuthenticationError('Invalid API key provided'),
        stripe.RateLimitError('Too many requests to the stripe API'),
        stripe.CardError('Your card was declined', code='bad_code', param='bad_param')
    ])
    def test_payment_status_session_failed(
        self, 
        client, 
        mocker, 
        fakes_pi ,
        fake_orders, 
        fake_session, 
        valid_user,
        exception,
    ):
        client.force_login(valid_user)
        mocker.patch('stripe.checkout.Session.retrieve', side_effect=exception)
        mocker.patch('stripe.PaymentIntent.retrieve', return_value=fakes_pi)
        
        response = client.get(
            reverse('payment-status') + f'?order_id={fake_orders.order_number}&session_id={fake_session.id}'
        )
        
        json_response = json.loads(response.content.decode())
        assert response.status_code == 500
        assert json_response.get('status') == 'error'
        assert json_response.get('error') is not None
        