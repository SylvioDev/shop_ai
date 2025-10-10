let category = document.getElementById('categorySelect');
let form = document.getElementById('form-category');


if (category && form) {
    const csrftoken = getCookie('csrftoken');

    category.onchange = (e) => {

        const request = new Request(
            `filter-category/${category.value}`,
            {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'Content-Type': 'application/json' 
                },
                mode: 'same-origin', 
                body: JSON.stringify({ 'category' : category.value})
            }
        );
        

        fetch(request)
            .then(response => response.json())
            .then(data => {
                const container = document.getElementById('productContainer');
                container.innerHTML = '';
                if (data.status == 'success'){
                
                    data.products.forEach(product => {
                        
                        const discountBadge = product.discount > 0 ? `<span class="badge-discount">-${product.discount}%</span>` : '';
                        const oldPrice = product.old_price > 0 ? `<span class="old-price">$${product.old_price}</span>` : '';
    
                        const productHTML = `
              <div class="product-card position-relative">
                ${discountBadge}
                <img src="${product.image_url}" alt="${product.name}" class="product-img">
                <div class="p-3">
                  <small class="text-muted">${product.category}</small>
                  <h6 class="mt-1 mb-1">${product.name}</h6>
                  <p class="mb-1 text-muted" style="font-size: 0.9rem;">In Stock : ${product.stock}</p>
                  <div class="d-flex align-items-center justify-content-between">
                    <span class="price">$${product.price}</span>
                    ${oldPrice}
                  </div>
                </div>
                
                <button stlyle="padding-left:15px" class="btn btn-primary btn-sm">
                    <a href="${product['product-url']}" class="text-white text-decoration-none">
                    View product
                    </a> 
                    <i class="bi bi-eye text-white"></i>
                </button>
                <br>
                <br>
              </div>
            `;
    
                container.insertAdjacentHTML('beforeend', productHTML);

                    });
                
                    
                }

            })
            .catch(error => {
                console.error('Error:', error);
            });
        

    };
       
}