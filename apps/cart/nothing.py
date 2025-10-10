data = {
    'PC GAMER WIZARD - Ryzen 7' : 
    {
        'category': 'High-Tech', 
        'title': 'PC GAMER WIZARD - Ryzen 7', 
        'price': 1299.0, 
        'stock': 2, 
        'image': 'http://localhost:8000/media/product_images/pc_gamer_wizard/Ryzen%207/LD0006246268.jpg', 
        'quantity': 2, 
        'attributes': 
        {
            'RAM': '16GB', 
            'GPU': 'RTX 5090', 
            'PSU': '650W', 
            'CPU': 'Ryzen 7'
        }, 
        'old_price': 1500.0, 
        'discount': '13.40'
    }, 
    'PC GAMER WIZARD': 
    {
        'category': 'High-Tech', 
        'title': 'PC GAMER WIZARD', 
        'price': 1300.0, 
        'stock': 2, 
        'image': 'http://localhost:8000/media/product_images/pc-gamer-asus/557784_1753182960_1753182961_600x600.png', 
        'quantity': 1, 
        'old_price': 2500.0, 
        'discount': '48.00'}, 
        'Laptop Lenovo 1345': 
        {
            'category': 'High-Tech', 
            'title': 'Laptop Lenovo 1345', 
            'price': 1546.0, 
            'stock': 3, 
            'image': 'http://localhost:8000/media/product_images/laptop-lenovo-1345/lenovo-thinkbook-15-iil-core-i5-1035g1-8-go-r.jpg', 
            'quantity': 1, 
            'old_price': 2000.0, 
            'discount': '22.70'
        }, 
    'Nike Air Max 270': 
    {
        'category': 'Shoes', 
        'title': 'Nike Air Max 270', 
        'price': 129.0, 
        'stock': 6, 
        'image': 'http://localhost:8000/media/product_images/nike-air-max-270/photo-1542291026-7eec264c27ff.jpeg', 
        'quantity': 3, 
        'old_price': 159.0, 
        'discount': '18.87'
    }, 
    'Nike Air Max 270 - Black Size 42': 
    {
        'category': 'Shoes', 
        'title': 'Nike Air Max 270 - Black Size 42', 
        'price': 35.0, 
        'stock': 3, 
        'image': 'http://localhost:8000/media/product_images/nike_air_max_270/Nike%20Air%20Max%20270%20-%20Black%20Size%2042/jd_009289_a.jpeg', 
        'quantity': 1, 
        'attributes': 
        {
            'Color': 'Black', 
            'Size': '42'
        }, 
        'old_price': 0.0
    }, 
    'Blue Jeans': 
    {
        'category': 'Clothing', 
        'title': 'Blue Jeans', 
        'price': 34.0, 
        'stock': 3, 
        'image': 'http://localhost:8000/media/product_images/blue-jeans/1s24i104_1100.jpg', 
        'quantity': 2, 
        'old_price': 0.0
    }
}

total_items = sum([item['quantity'] for item in data.values()])
print(f"Number of items : {total_items}")