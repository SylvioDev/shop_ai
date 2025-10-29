    // Payment method selection
    document.querySelectorAll('.payment-method').forEach(method => {
        method.addEventListener('click', function() {
            document.querySelectorAll('.payment-method').forEach(m => m.classList.remove('active'));
            this.classList.add('active');
        });
    });

    // Card number formatting
    document.getElementById('cardNumber')?.addEventListener('input', function(e) {
        let value = e.target.value.replace(/\s/g, '');
        let formattedValue = value.match(/.{1,4}/g)?.join(' ') || value;
        e.target.value = formattedValue;
    });

    // Expiry date formatting
    document.getElementById('expiry')?.addEventListener('input', function(e) {
        let value = e.target.value.replace(/\D/g, '');
        if (value.length >= 2) {
            value = value.slice(0, 2) + '/' + value.slice(2, 4);
        }
        e.target.value = value;
    });

    // CVV validation (numbers only)
    document.getElementById('cvv')?.addEventListener('input', function(e) {
        e.target.value = e.target.value.replace(/\D/g, '');
    });

    // Form submission
    document.getElementById('checkoutForm').addEventListener('submit', function(e) {
        e.preventDefault();
        
        const btn = e.target.querySelector('.btn-place-order');
        const originalText = btn.innerHTML;
        
        // Show loading state
        btn.disabled = true;
        btn.innerHTML = '<span class="spinner"></span> Processing Payment...';
        
        // Simulate payment processing
        setTimeout(() => {
            btn.disabled = false;
            btn.innerHTML = originalText;
            
            // Simulate random success/failure (90% success rate)
            const isSuccess = Math.random() > 0.1;
            
            if (isSuccess) {
                showSuccessModal();
            } else {
                showErrorModal();
            }
        }, 2500);
    });

    function showSuccessModal() {
        const modal = document.getElementById('resultModal');
        const icon = document.getElementById('modalIcon');
        const title = document.getElementById('modalTitle');
        const message = document.getElementById('modalMessage');
        const orderNum = document.getElementById('orderNumber');
        
        icon.className = 'modal-icon success';
        icon.innerHTML = '<i class="bi bi-check-circle-fill"></i>';
        title.textContent = 'Payment Successful!';
        message.textContent = "Your order has been placed successfully. We'll send you a confirmation email shortly.";
        orderNum.textContent = `Order #ORD-${new Date().getFullYear()}-${Math.floor(Math.random() * 900000 + 100000)}`;
        orderNum.style.display = 'block';
        
        modal.classList.add('show');
    }

    function showErrorModal() {
        const modal = document.getElementById('resultModal');
        const icon = document.getElementById('modalIcon');
        const title = document.getElementById('modalTitle');
        const message = document.getElementById('modalMessage');
        const orderNum = document.getElementById('orderNumber');
        
        icon.className = 'modal-icon error';
        icon.innerHTML = '<i class="bi bi-x-circle-fill"></i>';
        title.textContent = 'Payment Failed';
        message.textContent = 'There was an issue processing your payment. Please check your payment details and try again.';
        orderNum.style.display = 'none';
        
        modal.classList.add('show');
    }

    function goToOrders() {
        // Redirect to orders page (à adapter selon vos URLs Django)
        window.location.href = "{% url 'profile' %}";
    }

    function continueShopping() {
        // Redirect to products page
        window.location.href = "{% url 'products' %}";
    }

    // Close modal when clicking outside
    document.getElementById('resultModal').addEventListener('click', function(e) {
        if (e.target === this) {
            this.classList.remove('show');
        }
    });