function IncreaseQuantity(element){
    let productQuantity = element.previousElementSibling;
    if (parseInt(productQuantity.value) < parseInt(productQuantity.getAttribute("max"))) {
        productQuantity.value++;
    }
}

function DecreaseQuantity(element){
    let productQuantity = element.nextElementSibling;
    if (parseInt(productQuantity.value) > 1) {
        productQuantity.value--;
    }  
}

function updateCartSummary(data){
    let cartItems = document.getElementById("items-count");
    let subtotalItems = document.getElementById("subtotal-items");
    let subtotalPrice = document.getElementById("subtotal-price");
    let taxes = document.getElementById("vat");
    let totalPrice = document.getElementById("final-total");
    let shippingFee = document.getElementById("shipping");
    document.getElementById("cart-items").innerHTML = data['count'];
    cartItems.innerHTML = `Shopping Cart : ${data['count']} items`;
    subtotalItems.innerHTML = `Subtotal (${data['total_items']}) units `;
    subtotalPrice.innerHTML = `$${data['subtotal_price']}`;
    taxes.innerHTML = `$${data['taxes']}`;
    shippingFee.innerHTML = `$${data['shipping_fee']}`;
    totalPrice.innerHTML = `$${data['total_price']}`;
        
}

// Remove item function
function removeItem(element) {
    const csrftoken = getCookie('csrftoken');
    if (confirm('Are you sure you want to remove this item?')) {
        
        cart = element.parentElement.previousElementSibling.previousElementSibling.parentElement;
        let productSku = cart.childNodes[3].childNodes[1].value;
        const request = new Request(
        
            `/cart/delete/${productSku}`,
                {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrftoken,
                        'Content-Type': 'application/json' 
                    },
                    mode: 'same-origin', 
                    body: JSON.stringify({
                        'sku' : productSku
                    })
                }
            );
        
        
        fetch(request)
        .then(response => response.json())
        .then(data => {
        
        if (data.status == "success"){
            
            cart.remove();
            updateCartSummary(data.cart_summary);
        
                
        }
        
        })
        .catch(error => {
            
        })

        
        
        
        
        
        
    }



}


function updateQuantity(element){
    const csrftoken = getCookie('csrftoken');
    let a = element.parentElement.previousElementSibling;
    let productTitleHTML = a.childNodes[9];
    let productTitle = productTitleHTML.innerHTML;
    
    let productQuantity = a.childNodes[15].childNodes[3].value;
    let productSku = a.childNodes[1].value;
    
    const request = new Request(
        
        `/cart/update-quantity/${productSku}&${productQuantity}`,
            {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'Content-Type': 'application/json' 
                },
                mode: 'same-origin', 
                body: JSON.stringify({
                    "title" : productTitle,
                    "quantity" : productQuantity
                })
            }
        );
    
    fetch(request)
    .then(response => response.json())
    .then(data => {

        if (data.status == "success"){
            updateCartSummary(data.cart_summary);
        }

    })
    .catch(error => {

    })
    
    
}

// Proceed to checkout
function proceedToCheckout() {
    // Add loading animation
    const checkoutBtn = document.querySelector('.btn-primary');
    const originalText = checkoutBtn.textContent;
    checkoutBtn.textContent = 'Processing...';
    checkoutBtn.style.background = '#a0aec0';
    
    setTimeout(() => {
        alert('Redirecting to checkout...');
        checkoutBtn.textContent = originalText;
        checkoutBtn.style.background = '';
        checkoutAddress = location.protocol + "//" + location.host  + "/" + 'checkout';
        window.location.href = checkoutAddress;

    }, 2000);
    
}

// Continue shopping
function continueShopping() {
    alert('Redirecting to shop...');
    window.location.href = 'http://localhost:8000/products'
}

// Add hover effects to buttons
document.addEventListener('DOMContentLoaded', function() {
    const buttons = document.querySelectorAll('.qty-btn');
    buttons.forEach(btn => {
        btn.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.1)';
        });
        btn.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
        });
    });
});