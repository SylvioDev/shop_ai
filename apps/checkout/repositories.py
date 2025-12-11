from apps.container import container
from .models import (
    Order,
    OrderItem,
    Payment
)
from apps.products.models import (
    Product,
    ProductVariant
)
from .custom_exceptions import OrderNotFoundError
from apps.users.models import User
from typing import Union

class CheckoutRepository:
    def create_order(self, user : User, cart_data : dict, total_amount : float) -> Order:
        """
        Create a new order in the repository.

        Args:
            user: The user placing the order.
            cart_data (dict): The data of the cart being ordered.
            total_amount (float): The total amount for the order.

        Returns:
            Order: The created order object.
        """

        order = Order.objects.create(
            customer_id=user,
            status='pending',
            subtotal=cart_data.get('subtotal_price'),
            final_total=total_amount,
            vat=cart_data.get('taxes', 0),
            shipping_cost=cart_data.get('shipping_fee', 0),
            shipping_address=container.user_service.get_user_address(user_instance=user.id)
        )
        order.save()
        return order
    
    def create_payment(self, order : Order, payment_provider : str, amount : float) -> Payment:
        """
        Create a new payment record in the repository.

        Args:
            order (Order): The order associated with the payment.
            payment_method (str): The method of payment.
            amount (float): The amount paid.

        Returns:
            Payment: The created payment object.
        """
        payment = Payment.objects.create(
            order=order,
            provider=payment_provider,
            status='pending',
            amount=amount
        )
        payment.save()
        return payment
    
    def update_order_status(self, order_number : str, status : str) -> Order:
        """
        Update the status of an order.

        Args:
            order_number (str): The unique identifier for the order.
            status (str): The new status to set for the order.

        Returns:
            Order: The updated order object.

        Raises:
            OrderNotFoundError: If the order with the given order_number does not exist.
        """
        try:
            order=Order.objects.get(order_number=order_number)
            order.status=status
            order.save()
            return order
        except Order.DoesNotExist:
            raise OrderNotFoundError(order_number)
    
    def update_payment_status(self, order_number : str, status : str) -> Payment:
        """
        Update the payment status associated with an order.

        Args:
            order_number (str): The unique identifier for the order.
            status (str): The new payment status to set.

        Returns:
            Payment: The updated payment object.

        Raises:
            OrderNotFoundError: If the payment for the given order_number does not exist.
        """
        try:
            payment = Payment.objects.get(order__order_number=order_number)
            payment.status = status
            payment.save()
            return payment
        except Payment.DoesNotExist:
            raise OrderNotFoundError(order_number)
    
    def retrieve_user_order(self, order_number : str, user_id : User) -> Order:
        """
        Retrieve user that belongs to any particular user
        
        Args(order_num)
        
        """
        order = Order.objects.get(order_number=order_number)
        if order.customer_id == user_id:
            return order
        else:
            raise ValueError('You don\'t have permission to view this order')
    
    def decrease_stock(self, product_sku : str, quantity : int = 1):
        """
        Decrease stock of purchased product
        """
        product = container.product_repo.get_by_sku(product_sku)['product']
        if quantity > product.stock:
            raise ValueError(f'Not enough stock for product "{product.name}", only {product.stock} available')
        product.stock -= quantity
        product.save()
        return product
        
    def add_order_item(
        self, 
        order : Order,
        product_type : str, 
        product : Union[Product | ProductVariant], 
        product_name : str,
        product_attributes : dict,
        unit_price : float,
        quantity : int,
        total_price : float,
        img_src : str
        ):
        """
        Create an order item record
        """
        order_item = OrderItem.objects.create(
            order_id=order.id,
            product_name=product_name,
            attributes=product_attributes,
            unit_price=unit_price,
            quantity=quantity,
            total_price=total_price,
            image_url=img_src
        )
        if product_type == 'variant':
            order_item.variant = product
        else:
            order_item.product = product
        order_item.save()
        
        return order_item