// Thumbnail navigation

document.querySelectorAll('.thumbnail').forEach(thumbnail => {
    thumbnail.addEventListener('click', function() {
        document.querySelectorAll('.thumbnail').forEach(thumb => thumb.classList.remove('active'));
        this.classList.add('active');
        let image = document.getElementById('image-active');
        image.src = this.src;
        image.style.transition = 'transform 1.5s ease';
    });
});

// Initialize carousel auto-play pause on hover
        const carousel = document.getElementById('productCarousel');
        if (carousel) {
            carousel.addEventListener('mouseover', () => {
                bootstrap.Carousel.getInstance(carousel);
            });
            
            carousel.addEventListener('mouseleave', () => {
                bootstrap.Carousel.getInstance(carousel)
            });
    
        }
        
        
// filter product variant configuration

let formVariant = document.getElementById("form-variant");
let productVariantSelect = document.getElementById('variantSelect');

if (productVariantSelect){

    productVariantSelect.onchange = (event) => {
        let productSkutoSend = document.getElementById('product-sku');
        const csrftoken = getCookie('csrftoken');
        let productSku = productVariantSelect.value;
        productSkutoSend.value = productSku;
        
        const request = new Request(
            `update-variant/${productSku}`,
            {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'Content-Type': 'application/json' 
                },
                mode: 'same-origin', 
                body: JSON.stringify({ 'productSku' : productSku})
            }
        );
        
        
        fetch(request)
                .then(response => response.json())
                .then(data => {
                    let product_title = document.getElementById('product-title');
                    let product_price = document.getElementById('product-price');
                    let product_old_price = document.getElementById('old-price');
                    let product_stock = document.getElementById('stock');
                    let product_image = document.getElementById('image-active');
                    let product_images = document.getElementById('thumbnail-carousel img').firstElementChild;
                    
                    const liste = document.getElementById('variant-list');
                    
                    if (parseInt(data['old_price']) == 0){
                        product_old_price.innerHTML = "";
                    }
                    else{    
                        product_old_price.innerHTML = "";
                        product_old_price.innerHTML = `$${data['old_price']}`;
                    
                    }

                    if (data['message'] == "variant"){
                    
                    product_image.src = data['image'];
                    product_images.src = data['image'];
                    product_title.innerHTML = data['title'];
                    product_price.innerHTML = `$${data['price']}`;
                    product_stock.innerHTML = `In Stock - ${data['stock']} available`;    
                    document.getElementById("product-quantity").value = 1;
                    liste.innerHTML = '';
                    let attributes = Object.entries(data.attributes);
                    
                    for (let attr of attributes){;
                        const elementHTML = `
                        
                            <li class="list-group-item d-flex justify-content-between align-items-center">
                                <p>${attr[0]}</p>
                                <span id="attribute-value" class="badge rounded-pill bg-warning" >${attr[1]}</span>
                            </li>
    
                        `
                        liste.insertAdjacentHTML('beforeend', elementHTML);
                    
                    };
    
                }
    
                else {
    
                    product_title.innerHTML = data['title'];
                    product_price.innerHTML = `\$${data['price']}`;
                    product_stock.innerHTML = `In Stock - ${data['stock']} available`;    
                    product_image.src = data['image'];
                    product_images.src = data['image'];
                    liste.innerHTML = '';
    
                }
                
    
                });
    
    
    
    }
    

}


function cleanStock(stock){
    let output = new String(stock).split("-")[1].split(" ")[1];
    return parseInt(output);
}

// custom function to fetch quantity of product 

function RetrieveQuantity(){
    let productQuantity = cleanStock(document.getElementById('stock').innerHTML);
    let output = parseInt(productQuantity);
    return output
}

let productQuantityHTML = document.getElementById('product-quantity');

// Increase Product Quantity

function IncreaseQuantity(element){
    let productQuantity = RetrieveQuantity();
    
    productQuantityHTML.setAttribute("max", productQuantity);
    
    if (parseInt(productQuantityHTML.value) >= productQuantity){
        
    }
    else if (parseInt(productQuantityHTML.value) < productQuantity){
        element.disabled = false;
        productQuantityHTML.value++;
    
    }
    
}

// Decrease Product Quantity

function DecreaseQuantity(element){

    if (parseInt(productQuantityHTML.value) == 0){
        element.disabled = false;
    }
    else {
        productQuantityHTML.value--;
    }
}

