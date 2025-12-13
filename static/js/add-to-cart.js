
const csrftoken = getCookie('csrftoken');

function cleanStock(stock){
    return parseInt(stock.split("-")[1].split(" ")[1]);
}

function getAttributes(class_){
    let attributes = document.getElementsByClassName(class_);
    let attributes_array = new Map();
    let output = {};
        
    if (attributes.length > 0){
        for (let attribute of attributes){
            attributes_array.set(attribute.firstElementChild.innerText, attribute.lastElementChild.innerHTML)
        }

        for (let item of attributes_array){
            output[item[0]] = item[1]
        }
    
    }
    
    return output

}

function addToCart(element){
    
    //let attributes = document.getElementsByClassName('list-group-item d-flex justify-content-between align-items-center');
    let quantity = parseInt(document.getElementById('product-quantity').value);
    let productTitle = document.getElementById('product-title').innerText;
    let product_image = document.getElementById('image-active').src;
    let productSku = document.getElementById('product-sku').value;

    if (quantity == "0") {
        alert("Product quantity could not be 0");
    }
    
    else {

        let bodyValue = {
            'sku' : new String(productSku),
            'image' : product_image,            
            'quantity' : quantity,
            'attributes' : getAttributes('list-group-item d-flex justify-content-between align-items-center')    
        }

        
        const request = new Request(
        
        `/cart/add/${productSku}/${quantity}`,
            {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'Content-Type': 'application/json' 
                },
                mode: 'same-origin', 
                body: JSON.stringify(bodyValue)
            }
        );
    
        
        fetch(request)
        .then(response => response.json())
        .then(data => {

            
    
            if (data.status == "success"){
                const el = document.querySelectorAll("#cart-items")[0];
                el.innerHTML = data['count'];
                
                
            }
    
    
        })
        .catch(error => {
            console.log(`An error occured : ${error}`);
        })
    
    
    

    }

    
}

