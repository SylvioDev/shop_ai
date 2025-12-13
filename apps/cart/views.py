from django.http import JsonResponse
from django.http import HttpRequest
from django.shortcuts import render
from .cart import Cart

def cart_count(request : HttpRequest) -> dict:
    """
    Retrieve number of distinct items inside cart

    Args:
        request (WSGIRequest) : user's request  

    Returns:
        A json dict that contains the number of distinct items

    """
    cart = request.session.get('cart', {})
    if not isinstance(cart, dict):
        cart = {}
    total_items = len(cart.values())    
    return JsonResponse({'count' : total_items})

def add_to_cart(request : HttpRequest, product_sku : str, product_quantity : int) -> dict:
    """
    Add product to the cart

    Args:
        request (HttpRequest): a request to call delete view
        product_sku (str): product' sku
        product_quantity (int) : desired quantity to update

    Returns:
        JsonResponse (dict) = a json dict that contains the following :
            - status : status_code (useful for frontend) => "success" or "error"
            - count : number of distinc items inside the cart
            - message : tells the result of add to cart function (whether the product exists in database or not)

    """
    cart = None
    if not isinstance(cart, Cart):
        cart = Cart.from_request(request)
    
    message = str(cart.add(product_sku, product_quantity))
    status = "error" if "Product with SKU" in message else "success"

    if status == 'success':
        return JsonResponse(
            {
                'status' : status, 
                'count' : len(cart),
                'cart' : cart.cart
            })
    else:
        return JsonResponse({
            'status' : status,
            'message' : message
        })
        
def cart_detail(request : HttpRequest):
    """
    List all products inside the cart with cart' summary
    
    Args:
        request (HttpRequest) : request that calls  cart_detail view

    Returns:
        JsonResponse (dict) : 
            - cart : cart attribute
            - count : number of distincts items inside the cart
            - cart_summary : cart'summary
        
    """
    cart = Cart.from_request(request)
    return render(
        request, 
        'cart.html', 
        {
            'cart' : cart.cart, 
            'count' : len(cart),
            'cart_summary' : cart.get_cart_summary()
        }
    )

def update_quantity(request : HttpRequest, product_sku : str, product_quantity : int) -> dict:
    """
    Update the quantity of a particular product

    Args:
        request (HttpRequest): a request that calls update_quantity view
        product_sku (str): product' sku
        product_quantity (int) : desired quantity to update

    Returns:
        JsonResponse (dict) = a json dict that contains the following :
            - status : status_code (useful for frontend) => "success" | "error"
            - message : tells the result of updating function => "Quantity of {product_sku} ..." or "product .. doesn't exist!"
            - cart_summary : summary of the cart
            - cart : cart system

    """
    cart = Cart.from_request(request)
    message = cart.update_product_quantity(product_sku, product_quantity)
    cart_summary = cart.get_cart_summary()
    
    if message == 1:
        return JsonResponse({
            'status' : 'success',
            'message' : f'Quantity of "{product_sku} updated successfully',
            'cart_summary' : cart_summary,
            'cart' : cart.cart
        }, status=200)
    else:
        return JsonResponse({
            "status" : "error",
            "message" : f"product '{product_sku}' doesn't exist"
        }, status=400)    

def delete_product(request : HttpRequest, product_sku : str) -> dict:
    """
    Delete a product from the cart session

    Args:
        request (HttpRequest): a request that calls delete view
        product_sku (str): SKU of the product
    
    Returns:
        JsonResponse (dict) : a json dict that contains the following :
            if success: 
                - status : status code of the request => success
                - count : number of distinct items inside the cart
                - message : a log that helps for testing
                - cart_summary : summary of the cart
            
            if failed (unexisting product):
                - status => error
                - message => tells that an invalid sku is provided
    """
    cart = Cart.from_request(request)
    message = cart.remove(product_sku)
    status = 'success' if 'successfully' in message else 'error'
    if status == 'success' :
        cart_summary = cart.get_cart_summary()
        return JsonResponse({
            'status':'success',
            'count':len(cart),
            'message':message,
            'cart_summary' : cart_summary
        })
    else:
        return JsonResponse({
            'status' : status,
            'message' : message
        })