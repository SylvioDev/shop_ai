from apps.container import container
import pytest
from unittest.mock import MagicMock
from apps.conftest import (
    user_order,
    Cart,
    sku,
    product,
    order_data,
    payment_data,
    mock_session
)
from django.conf import settings
import stripe
from apps.checkout.custom_exceptions import (
    InvalidPayloadException,
    InvalidSignatureException
)
from apps.checkout.payment_service import StripePaymentService
from apps.checkout.repositories import CheckoutRepository

@pytest.fixture
def fake_secret():
    return 'c51a0d81b4f3e67c92a84f3d1e67c92a84f3d1e67c92a84f3d1e67c92'

@pytest.fixture
def fake_payload():
    return b'{}'

@pytest.fixture
def fake_header():
    return 'fake-header'

@pytest.fixture
def fake_pi():
    mock_pi = MagicMock()
    mock_pi.latest_charge = "ch_123"
    mock_pi.created = 1700000000  # Unix timestamp
    return mock_pi

@pytest.fixture
def fake_session(order_data, payment_data):
    order = order_data
    payment = payment_data
    # fake session (supports .id and .get)
    session = MagicMock()
    session.id = "cs_test_123"
    session.payment_method_types=['card']
    session.amount_total = 8000
    session.payment_intent = 'pi_157'
    session.currency = 'usd'
    session.get.side_effect = lambda key, default=None: {
        "metadata": {
            "order_id":f"{order.order_number}",
            "user_id": f"{order.customer_id.id}",
            "payment_id" : f"{payment.id}"
        }
    }.get(key, default)

    return session

@pytest.fixture
def fake_event(fake_session):
    fake_event = MagicMock()
    fake_event.id = "cs_test_123"
    fake_event.type = 'checkout.session.completed'
    fake_event.__getitem__.return_value={'object':fake_session}
    return fake_event

### Failure ###

@pytest.fixture
def failed_pi(order_data, payment_data):
    return {
        'id': 'pi_12345',
        'latest_charge': 'ch_123',
        'created': 1700000000,
        'last_payment_error': {
            'message': 'Your card is invalid',
            'type': 'card_error'
        },
        'metadata' : {
            'order_id' : order_data.order_number,
            'user_id' : str(order_data.customer_id.id),
            'payment_id' : str(payment_data.id)
        }
    }

@pytest.fixture
def failed_event(failed_pi):
    # This dictionary holds the data we want to access via brackets []
    event_dict_data = {
        'data': {'object': failed_pi}
    }

    mock_event = MagicMock()
    
    # A. Handle Dot Notation (event.type)
    mock_event.type = 'payment_intent.payment_failed'
    
    # B. Handle Dictionary Notation (event['data'])
    # We tell the mock: "When someone uses [], look inside event_dict_data"
    mock_event.__getitem__.side_effect = event_dict_data.__getitem__
    
    return mock_event
    
pytestmark = pytest.mark.django_db

class TestStripePaymentService:    
    def test_initialization(self):
        service = container.payment_service
        assert isinstance(service, StripePaymentService)
        assert isinstance(service.repo, CheckoutRepository)
    
    def test_create_cart_checkout(self, cart_data):
        line_items = container.payment_service.create_cart_checkout(cart_data)
        assert isinstance(line_items, list)
        assert len(line_items) == 4
        index = 0
        for item in line_items:
            product_name = item['price_data']['product_data']['name']
            if product_name == 'VAT' or product_name == 'Shipping Fee':
                index += 1
        assert index == 2 # Both VAT and Shipping Fee inside line_items
            
    def test_create_session_empty_cart(self):
        cart = Cart({})
        order = user_order(cart, 'Paul', '78th street')
        with pytest.raises(ValueError) as exc_info:
            checkout_session = container.payment_service.create_session(
                cart=cart,
                user=order.customer_id,
                order=order,
                payment=container.checkout_repo.create_payment(order,'Stripe',8000)
            )
        assert 'Cart is empty. Cannot create checkout session.' == str(exc_info.value)
    
    def test_create_session_success(self, cart_data, order_data, payment_data, mock_session): 
        metadata = mock_session.get('metadata')
        
        assert metadata is not None
        assert metadata['user_id'] == str(order_data.customer_id.id)
        assert metadata['order_id'] == str(order_data.order_number)
        assert metadata['payment_id'] == str(payment_data.id)
        assert mock_session.mode == 'payment'
        assert mock_session.payment_status == 'unpaid'
        assert mock_session.success_url == settings.DOMAIN_URL + f'checkout/success/?order_id={order_data.order_number}&session_id={{CHECKOUT_SESSION_ID}}'
        assert mock_session.cancel_url == settings.DOMAIN_URL + f'checkout/cancel/?order_id={order_data.order_number}&session_id={{CHECKOUT_SESSION_ID}}'
    
    @pytest.mark.parametrize('exception', [
        stripe.InvalidRequestError("bad params", "param"),
        stripe.AuthenticationError("invalid api key"),
        stripe.APIConnectionError("network error"),
        stripe.RateLimitError("too many requests"),
        stripe.APIError("stripe internal error"),
        Exception("generic failure")
    ])
    def test_create_session_failed(self, mocker, cart_data, order_data, payment_data, exception):
        mocker.patch('stripe.checkout.Session.create', side_effect=exception)#Exception('Stripe is down'))
        
        # ---- 2. Call the function under test ----
        response = container.payment_service.create_session(
            cart=cart_data,
            user=order_data.customer_id,
            order=order_data,
            payment=payment_data
        )
    
        assert response == 'An error occured while creating Stripe checkout session. '
        
    def test_payment_details(self, payment_data):
        output = container.payment_service.payment_details(payment=payment_data)
        assert isinstance(output, dict)
        assert output.get('transaction_id') == 'SDQSA'
        assert output.get('amount_paid') == payment_data.amount / 100
        assert output.get('date') == payment_data.paied_at
        assert output.get('payment_method') == payment_data.method
        assert output.get('status') == payment_data.status
    
    def test_handle_webhook_failed_payload(self, mocker, fake_payload, fake_header):
        error_message = 'Invalid payload received in Stripe webhook.'
        mocker.patch('stripe.Webhook.construct_event', side_effect=ValueError(error_message))
        with pytest.raises(InvalidPayloadException) as exc_info:
            response = container.payment_service.handle_webhook(fake_payload, fake_header)
        assert str(exc_info.value) == error_message        
    
    def test_handle_webhook_failed_signature(self, mocker, fake_payload, fake_header):
        error_message = 'Invalid signature in Stripe webhook.'
        mocker.patch('stripe.Webhook.construct_event', side_effect=InvalidSignatureException(error_message))
        with pytest.raises(InvalidSignatureException) as exc_info:
            response = container.payment_service.handle_webhook(fake_payload, fake_header)
        assert str(exc_info.value) == error_message        
    
    def test_webhook_session_completed(self, mocker, fake_session, fake_event, fake_pi, order_data, fake_payload, fake_header):
        mocker.patch('stripe.Webhook.construct_event', return_value=fake_event)
        mocker.patch('stripe.checkout.Session.retrieve', return_value=fake_session)
        mocker.patch('stripe.PaymentIntent.retrieve', return_value=fake_pi)
        mocker.patch('apps.checkout.services.CheckoutService.handle_success_payment_status')
        
        container.payment_service.handle_webhook(fake_payload, fake_header)
        
        container.checkout_service.handle_success_payment_status.assert_called_once_with(
            session_id=fake_session.id,
            order_id=order_data.order_number,
            user_id=order_data.customer_id
        )
        
    def test_webhook_payment_failed(
        self,
        mocker,
        failed_event,
        failed_pi,
        fake_header,
        fake_payload,
        order_data
    ):
        mocker.patch("stripe.Webhook.construct_event", return_value=failed_event)
        mocker.patch("stripe.PaymentIntent.retrieve", return_value=failed_pi)
        mock_failure = mocker.patch(
            "apps.checkout.services.CheckoutService.handle_failure_payment_status"
        )

        container.payment_service.handle_webhook(fake_payload, fake_header)

        mock_failure.assert_called_once_with(
            order_id=str(order_data.order_number),
            user_id=order_data.customer_id,
            error_message=failed_pi['last_payment_error']['message'],
        )
         