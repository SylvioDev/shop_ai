from apps.container import container
import pytest
from apps.conftest import (
    sku,
    variant_sku,
    variant_product,
    product,
    checkout_user,
    ProductImageFactory,
    cart_data,
    cart_summary_test,
    user_order
)
from apps.cart.cart import Cart
from apps.orders.models import Order
from apps.users.models import User
from apps.checkout.models import Payment
from apps.products.models import Product, ProductVariant

pytestmark = pytest.mark.django_db


class TestCheckoutRepository:        
    def test_create_order(self, cart_data, total_amount_test, cart_summary_test):
        order = user_order(cart_data, 'paul', '123 East 85th Street, Apt 5G, New York, NY 10028')
        assert isinstance(order, Order)
        assert order.customer_id == User.objects.get(username='paul')
        assert order.subtotal == cart_summary_test.get('subtotal_price')
        assert order.final_total == total_amount_test
        assert order.shipping_address.street_address == '123 East 85th Street, Apt 5G, New York, NY 10028'
        
    def test_create_payment(self, cart_data, cart_summary_test):
        payment = container.checkout_repo.create_payment(
            order=user_order(cart_data, username='Mike', user_address='178 West 98th Street'),
            payment_provider='stripe',
            amount=cart_summary_test.get('total_price')
        )
        assert isinstance(payment.order, Order)
        assert payment.provider == 'stripe'
        assert payment.amount == cart_summary_test.get('total_price')
        assert payment.status == 'pending'
    
    @pytest.mark.parametrize('status, expected_status', [
        ('pending', 'pending'),
        ('paid', 'paid'),
        ('cancelled', 'cancelled'),
        ('completed', 'completed'),
        ('refunded_insufficient_stock', 'refunded_insufficient_stock')
    ])    
    def test_update_order_status(self, cart_data, status, expected_status):
        order = user_order(cart_data, username='Anna', user_address='Address')
        updated_order = container.checkout_repo.update_order_status(
            order_number=order.order_number,
            status=status
        )    
        assert isinstance(updated_order, Order)
        assert updated_order.status == expected_status

    @pytest.mark.parametrize('status, expected_status', [
        ('pending', 'pending'),
        ('success', 'success'),
        ('failed', 'failed')
    ])
    def test_update_payment_status(self, cart_data, status, expected_status):
        order = user_order(cart_data, username='Illico', user_address='Fake Address')
        payment = container.checkout_repo.create_payment(
            order=order, 
            payment_provider='stripe',
            amount=cart_data.get_cart_summary().get('total_price')
        )
        updated_payment = container.checkout_repo.update_payment_status(
            order_number=order.order_number,
            status=status
        )
        assert isinstance(updated_payment, Payment)
        assert updated_payment.status == expected_status
    
    def test_retrieve_user_order_success(self, cart_data):
        order = user_order(cart_data, username='rakoto', user_address='LOT 48 BIS')
        user = User.objects.get(username='rakoto')
        retrieved_order = container.checkout_repo.retrieve_user_order(order.order_number, user)
        assert isinstance(retrieved_order, Order)
    
    def test_retrieve_user_order_wrong_user(self, cart_data):
        order = user_order(cart_data, username='Kylian', user_address='LOT 47 AS')
        with pytest.raises(ValueError) as exc_info:
            retrieved_order = container.checkout_repo.retrieve_user_order(order.order_number, 4)
        
        assert f"You don't have permission to view this order" == str(exc_info.value)
    
    def test_retrieve_user_order_not_found(self, cart_data):
        user = User.objects.create_user(username='testing', email='testing@example.com',password='pass')
        with pytest.raises(Order.DoesNotExist) as exc_info:
            retrieved_user = container.checkout_repo.retrieve_user_order('ORD-2025-PPMO74S', user.id)
        assert "Order matching query does not exist." == str(exc_info.value)
    
    def test_decrease_stock_success(self, cart_data, sku):
        product = container.checkout_repo.decrease_stock(product_sku=sku, quantity=4)
        assert product.stock == 8
    
    def test_decrease_stock_failed(self, cart_data, sku):
        with pytest.raises(ValueError) as exc_info:
            product = container.checkout_repo.decrease_stock(product_sku=sku, quantity=18)
            assert f"Not enough stock for product \"{product.name}\", only {product.stock} available" == str(exc_info.value)
            
    def test_add_order_item_base_product(self, cart_data, sku):
        order = user_order(cart_data, username='Iris', user_address='LOT 45 MS')
        product = container.product_repo.get_by_sku(sku)['product']
        assert isinstance(product, Product)
        order_item = container.checkout_repo.add_order_item(
            order=order,
            product_type='base',
            product=product,
            product_name=cart_data.cart.get(sku)['title'],
            product_attributes={},
            unit_price=cart_data.cart.get(sku)['price'],
            quantity=cart_data.cart.get(sku)['quantity'],
            total_price=cart_data.cart.get(sku)['quantity'] * cart_data.cart.get(sku)['price'],
            img_src='/images'
        )
        assert order == order_item.order
        assert order_item.attributes == {}
        assert order_item.total_price == 4 * product.price
        assert order_item.unit_price == cart_data.cart.get(sku)['price']
        assert order_item.variant is None
        
    def test_add_order_item_variant_product(self, cart_data, variant_sku):
        order = user_order(cart_data, username='Léa', user_address='LOT 48 MS')
        variant = container.product_repo.get_by_sku(variant_sku)['product']
        assert isinstance(variant, ProductVariant)
        order_item = container.checkout_repo.add_order_item(
            order=order,
            product_type='variant',
            product=variant,
            product_name=cart_data.cart.get(variant_sku)['title'],
            product_attributes={},
            unit_price=cart_data.cart.get(variant_sku)['price'],
            quantity=cart_data.cart.get(variant_sku)['quantity'],
            total_price=cart_data.cart.get(variant_sku)['quantity'] * cart_data.cart.get(variant_sku)['price'],
            img_src='/images'
        )
        assert order == order_item.order
        assert order_item.attributes == {}
        assert order_item.total_price == 2 * variant.price
        assert order_item.unit_price == cart_data.cart.get(variant_sku)['price']
        assert order_item.product is None