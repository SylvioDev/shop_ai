import pytest
from apps.conftest import (
    cart_data,
    cart_summary_test,
    user_order,
    Cart,
    product,
    sku,
    checkout_user,
    CheckoutRepository
)
from apps.checkout.services import CheckoutService
from apps.checkout.cart_validation.cart_exceptions import (
    EmptyCartError,
    OutOfStockError
)
from apps.checkout.models import Payment, OrderItem
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone
from apps.products.repositories import ProductRepository

pytestmark = pytest.mark.django_db
class TestCheckoutService:
    def test_cart_validation_empty_cart(self):
        cart = Cart({})
        with pytest.raises(EmptyCartError) as exc_info:
            invalid_cart = CheckoutService().cart_validation(cart)
        assert "Your cart is empty. Add items to proceed." == str(exc_info.value)
        
    def test_cart_validation_out_of_stock(self, sku, product):
        cart = Cart({})
        cart.add(product_sku=sku, quantity=15)
        product.stock = 8
        product.save()
        with pytest.raises(OutOfStockError) as exc_info:
            invalid_cart = CheckoutService().cart_validation(cart)
        assert f'Not enough stock for "{product.name}" . Only {product.stock} left.' in str(exc_info.value)
    
    def test_cart_validation_valid_cart(self, cart_data):
        valid_cart = CheckoutService().cart_validation(cart_data)
        assert isinstance(valid_cart.cart, dict)
        
    @pytest.mark.parametrize('payment_status, expected_output', [
        ('paid', 'paid'),
        ('cancelled', 'cancelled')
    ])
    def test_handle_order_status(self, cart_data, payment_status, expected_output):
        order = user_order(cart_data,username='rakoto', user_address='75th Street')
        updated_order = CheckoutService().handle_order_status(order.order_number, payment_status=payment_status)
        updated_order.status == expected_output
        
    def test_order_creation(self, cart_data):
        user = checkout_user('Nina', '80th Street')
        order = CheckoutService().order_creation(cart=cart_data, user=user)
        assert order.cart == cart_data.cart
        assert order.status == 'pending'
        assert order.final_total == cart_data.get_cart_summary()['total_price']
        
    def test_payment_creation(self, cart_data):
        user = checkout_user('Rams', '48th Street Elizabeth')
        order = CheckoutService().order_creation(cart=cart_data, user=user)
        payment = CheckoutService().payment_creation(order, 'stripe')
        assert isinstance(payment, Payment)
        assert payment.provider == 'stripe'
        assert payment.amount == order.final_total
        assert payment.status == 'pending'
    
    def test_add_order_items_success(self, cart_data):
        user = checkout_user('Rams', '48th Street Elizabeth')
        order = CheckoutService().order_creation(cart=cart_data, user=user)
        CheckoutService().add_order_items(order, cart_data.cart)
        order_items = OrderItem.objects.all()
        assert len(order_items) == 2
        for order_item in order_items:
            assert isinstance(order_item, OrderItem)
            assert order_item.order == order
            
    def test_add_order_items_failure(self, cart_data):
        with pytest.raises(AttributeError) as exc_info:
            order_items = CheckoutService().add_order_items("qsdqsdqsd", cart_data.cart)
        assert "'str' object has no attribute 'id'" == str(exc_info.value)
    
    def test_handle_success_payment_status(self, mocker, sku, product):
        cart = Cart({})
        cart.add(sku, quantity=4)
        user = checkout_user('Malm', '99th Street')
        order = CheckoutService().order_creation(cart=cart, user=user)
        payment = CheckoutService().payment_creation(order, 'stripe')    
        order.cart = cart.cart
        
        # setting cart data
        session_id = 'cs_test_a1B2c3D4'
        payment_intent_id = 'pi_18789484'
        fake_charge_id = 'ch_abc18984'
                
        mock_session = MagicMock()
        mock_session.id = "sess_123"
        mock_session.amount_total = 2000
        mock_session.payment_intent = "pi_123"
        mock_session.currency = "usd"
        mock_session.payment_method_types = ["card"]

        mock_pi = MagicMock()
        mock_pi.latest_charge = "ch_123"
        mock_pi.created = 1700000000  # Unix timestamp

        mocker.patch("stripe.checkout.Session.retrieve", return_value=mock_session)
        mocker.patch("stripe.PaymentIntent.retrieve", return_value=mock_pi)

        assert order.status == 'pending'
        assert payment.status == 'pending'
        
        product = ProductRepository().get_by_sku(sku)['product']
        original_product_stock = product.stock # 12
        
        new_order = CheckoutService().handle_success_payment_status(
            session_id=session_id,
            order_id=order.order_number,
            user_id=user
        )
        
        order.refresh_from_db()
        payment.refresh_from_db()
        product.refresh_from_db()
        
        # After successful payment
        assert order.status == 'paid'
        assert payment.status == 'success'
        assert float(payment.amount) == float(mock_session.amount_total / 100)
        assert payment.method == mock_session.payment_method_types[0]
        assert payment.currency == 'USD'
        assert payment.stripe_session_id == mock_session.id
        assert payment.stripe_payment_intent_id == mock_session.payment_intent
        assert payment.paied_at == datetime.fromtimestamp(mock_pi.created, tz=timezone.utc)
        assert payment.transaction_id == mock_pi.latest_charge
        # Cart length verification
        assert len(cart.cart) > 0 # We don't clear cart yet here
        # Inventory stock decrease
        assert product.stock == 8 # 12 - 4 = 8
    
    def test_handle_failure_payment_status(self, mocker, sku, variant_product, variant_sku):
        variant_product.stock = 15
        variant_product.save()
        
        cart = Cart({})
        cart.add(variant_sku, quantity=8)
        
        user = checkout_user('Malm', '99th Street')
        order = CheckoutService().order_creation(cart=cart, user=user)
        payment = CheckoutService().payment_creation(order, 'stripe')    
        order.cart = cart.cart
        
        
        # setting cart data
        session_id = 'cs_test_bisO5187'
        payment_intent_id = 'pi_974855'
        fake_charge_id = 'ch_mlp154456'
                
        mock_session = MagicMock()
        mock_session.id = "sess_456"
        mock_session.amount_total = 6000
        mock_session.payment_intent = "pi_257"
        mock_session.currency = "usd"
        mock_session.payment_method_types = ["card"]
        mock_session.last_payment_error = {
            "message": "Your card was declined",
            "type": "card_error"
        }
 
        mock_pi = MagicMock()
        mock_pi.latest_charge = "ch_111"
        mock_pi.created = 1700000000  # Unix timestamp
        mock_pi.status = 'canceled'
        
        mocker.patch("stripe.checkout.Session.retrieve", return_value=mock_session)
        mocker.patch("stripe.PaymentIntent.retrieve", return_value=mock_pi)
        
        assert order.status == 'pending'
        assert payment.status == 'pending'
        
        updated_order = CheckoutService().handle_failure_payment_status(
            order_id=order.order_number,
            user_id=user,
            error_message=mock_session.last_payment_error['message']
        )
        
        order.refresh_from_db()
        payment.refresh_from_db()
        
        assert updated_order.status == 'cancelled'
        assert payment.status == 'failed'
        assert updated_order.failure_reason == mock_session.last_payment_error['message']
        assert variant_product.stock == 15 # no stock decrease
        assert len(cart.cart) > 0
        assert payment.amount != mock_session.amount_total
    
    def test_handle_webhook_fallback(self, mocker, sku, product):
        
        cart = Cart({})
        cart.add(sku, quantity=4)
        user = checkout_user('Malm', '99th Street')
        order = CheckoutService().order_creation(cart=cart, user=user)
        payment = CheckoutService().payment_creation(order, 'stripe')    
        order.cart = cart.cart
        
        # setting cart data
        session_id = 'cs_test_a1B2c3D4'
        payment_intent_id = 'pi_18789484'
        fake_charge_id = 'ch_abc18984'
                
        mock_session = MagicMock()
        mock_session.id = "sess_123"
        mock_session.amount_total = 2000
        mock_session.payment_intent = "pi_123"
        mock_session.currency = "usd"
        mock_session.payment_method_types = ["card"]

        mock_pi = MagicMock()
        mock_pi.latest_charge = "ch_123"
        mock_pi.created = 1700000000  # Unix timestamp

        mocker.patch("stripe.checkout.Session.retrieve", return_value=mock_session)
        mocker.patch("stripe.PaymentIntent.retrieve", return_value=mock_pi)

        assert order.status == 'pending'
        assert payment.status == 'pending'
        
        product = ProductRepository().get_by_sku(sku)['product']
        original_product_stock = product.stock # 12
                
        new_order = CheckoutService().handle_webhook_fallback(
            session_id=session_id,
            order_id=order.order_number,
            user_id=user
        )
        
        order.refresh_from_db()
        payment.refresh_from_db()
        product.refresh_from_db()
    