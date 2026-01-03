from apps.container import container
from shop_ai.settings import CART_SESSION_ID 
class Cart:
    """
    Represents a cart in the system.

    The Cart class manages a collection of items that a user intends to purchase.
    It provides methods to add, remove, update, and retrieve items, as well as
    calculate totals and apply discounts or taxes.
    
    Attributes:
        session: session variable to handle products in browser
        cart: dictionnary that stores users's product items
        items_count: number of distinct items within the cart
        total_items : number of all items (quantity) in the cart
        taxes: VAT (20%)
        shipping_fee : delivering fee
        total_amount : amount of what user will pay for checkout
        
    Methods:
        add(), save(), remove(), update_product_quantity(),
        clear(), get_cart_summary()
        
    Example:
        >>> cart = Cart(session_data={}))
        >>> sku = 'SKU-IJQUAS88'
        >>> product = Product.objects.create(name='Sneakers Black Flame', price=21, sku='SKU-IJQUAS88')
        >>> cart.add(sku)
        >>> print(len(cart))
        >>> 1
        
    """
    
    def __init__(self, session_data):
        """
        Initialize the cart 

        Args:
            session_data (dict): session for handling products in browser
        """
        self.session = session_data
        cart = self.session.get(CART_SESSION_ID)
        if not cart:
            cart = self.session[CART_SESSION_ID] = {}
        self.cart = cart
        self.items_count = 0
        self.total_items = 0
        self.taxes = 0.0
        self.shipping_fee = 0.0
        self.subtotal = 0.0
        self.total_amount = 0.0
        
    def save(self):
        """ Save cart modification into session and cart attribute"""
        self.session[CART_SESSION_ID] = self.cart
        self.modified = True 
    
    def add(self, product_sku, quantity=1):
        """
        Add product to cart 

        Args:
            product_sku (str): product' sku
            quantity (int, optional): desired quantity. Defaults to 1.
        
        Example:
            >>> cart = Cart(session_data={}))
            >>> sku = 'SKU-IJQUOPL8'
            >>> product = Product.objects.create(name='PC Gaming Asus', price=1231, sku='SKU-IJQUAS88')
            >>> product_variant = ProductVariant.objects.create(identifiant='Pc Gaming Asus Ryzen 5', price=1400,product=product, sku='SKU-QS578VB')
            >>> cpu_attribute = Attribute.objects.create(name='CPU')
            >>> cpu_value = AttributeValue(attribute=cpu_attribute, value='Ryzen 5')
            >>> cart.add('SKU-QS578VB')
            >>> print(len(cart))
            >>> 1
            >>> print(cart.cart)
            >>> 
            {
                'SKU-A27DE69D': 
                    {
                        'sku': 'SKU-QS578VB', 
                        'category': 'High-Tech', 
                        'title': 'PC Gaming Asus Ryzen 5', 
                        'price': 1400, 
                        'old_price': 0.0, 
                        'stock': 3, 
                        'image': '/media/product_images/sister/example.jpg', 
                        'quantity': 1,
                        'attributes' : {'cpu':'Ryzen 5'}
            }, 
        
        """
        
        try:
            product_dict = container.product_repo.get_by_sku(product_sku)
        except ValueError as error:
            return error 
        
        product = product_dict['product']
        attributes = container.product_repo.get_variant_attribute(product)
        quantity = int(quantity)
        
        if product.sku not in self.cart:
            self.cart[product.sku] = {
                'sku' : product.sku,
                'category' : str(product.category) if product_dict['product_type'] == 'base' else str(product.product.category),
                'title' : product.name if product_dict['product_type'] == 'base' else product.identifiant,
                'price' : float(product.price),
                'old_price' : float(product.old_price),
                'stock' : int(product.stock),
                'image' : container.product_repo.get_product_image(product.sku),
                'quantity' : quantity if quantity > 0 else 1
            }
        else:
            self.cart[product.sku]['quantity'] += quantity
                
        if self.cart[product.sku]['quantity'] > int(product.stock): # product quantity will never exceed stock quantity
            self.cart[product.sku]['quantity'] = int(product.stock)

        if len(attributes) > 0:
            self.cart[product.sku]['attributes'] = attributes # attributes for variant products
        
        if float(product.old_price) > 0:
            self.cart[product.sku]['discount'] = f'{product.discount:.2f}'

        self.save()
        
    def clear(self):
        """ Clear cart session and cart attribute """
        self.session[CART_SESSION_ID] = {}
        self.cart = {}
        self.save()

    def remove(self, product_sku):
        """
        Remove product from cart

        Args:
            product_sku (str): product'sku

        """
        product_sku = str(product_sku).strip()
        if product_sku in self.cart:
            del self.cart[product_sku]
            self.save()
            return f'Product with sku "{product_sku}" deleted successfully !'
        else:
            return f'Product with sku "{product_sku}" doesn\'t exist !'
    
    def get_shipping_fee(self):
        """
        Shipping_fee 
        Returns:
            shipping_fee (float) : shipping_fee of all products
        """
        return self.shipping_fee
    
    #### Setters ####
 
    def set_subtotal_price(self):
        """
        Calculate and returns subtotal of all items

        Returns:
            subtotal (float) : sum of all products multiplied by its quantity
        """
        self.subtotal = sum([item['price'] * item['quantity'] for item in self.cart.values()])
        return self.subtotal
    
    def set_items_count(self):
        """
        return all of distinct items in the cart
        Returns:
            items_count (int): number of all distinct items

        """
        self.items_count = len(self.cart)
        return self.items_count

    def set_taxes(self):
        """
        Calculate and returns taxes
        Returns:
            taxes (float) attribute 

        """
        self.taxes = (self.subtotal * 20) / 100
        return self.taxes
    
    def set_total_items(self):
        """
        Calculate and returns the number of items (non-distinct) inside the cart

        Returns:
            total_items (float) , number of all items

        """
        self.total_items = sum(item['quantity'] for item in self.cart.values() if isinstance(item, dict))
        return self.total_items
    
    def set_shipping_fee(self, amount):
        """
        Set the new value of shipping_fee

        Args:
            amount (float): amount of desired shipping_fee

        Returns:
            shipping_fee for cart summary 
        """
        self.shipping_fee = amount 
        return self.shipping_fee

    def set_total_amount(self):
        """
        Set the total of amount for checkout

        Returns:
            total_amount (float): amount of money that will be paid when checkout

        """
        self.total_amount =  self.subtotal + self.taxes + self.shipping_fee
        return self.total_amount
    
    def get_cart_summary(self):
        """
        Represents the summary of a purchase

        Returns:
            summary (dict) => a dictionnary that contains the following pair key-value items : 
                - count : number of distinct items 
                - total_items : number of all items
                - taxes : vat of all products
                - shipping_fee : delivery costs
                - total_amount : amount of money for checkout

        """
        self.set_items_count()
        self.set_total_items()
        self.set_subtotal_price()
        self.set_taxes()
        self.set_shipping_fee(120) if self.items_count > 0 else self.set_shipping_fee(0)
        self.set_total_amount()

        summary =  {
            'count':self.items_count,
            'total_items' : self.total_items,
            'subtotal_price' : self.subtotal,
            'taxes' : self.taxes,
            'shipping_fee' : self.shipping_fee,
            'total_price' : self.total_amount
        }

        return summary

    def update_product_quantity(self, product_sku, product_quantity):
        """
        Update the quantity of a product

        Args:
            product_sku (str) : product' sku
            product_quantity (int): desired quantity

        Returns:
            message(str) : 1 if the product exists in cart else None

        """
        product_quantity = int(str(product_quantity).strip())
        product_name = str(product_sku).strip()
        cart = self.cart
        if product_name in cart:
            cart[product_sku]['quantity'] = product_quantity
            self.save()

        message = 1 if product_name in self.cart else None

        self.save()

        return message
    
    @classmethod
    def from_request(cls, request):
        """_summary_

        Args:
            request (): _description_

        Returns:
            (class) : _description_
        """
        return cls(request.session)

    def __len__(self):
        """
        Custom len() method for cart Class

        Returns:
            int : size of cart attribute

        """
        return len(self.cart)

    def __str__(self):
        """ String representation of Cart class """
        return f'Cart Class'


    

        
        
