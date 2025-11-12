const promoInput = document.getElementById('promoCode');
const applyBtn = document.getElementById('applyBtn');
const messageDiv = document.getElementById('message');
const csrftoken = getCookie('csrftoken');

        // Valid promo codes (you can modify these)
        /*
        const validPromoCodes = {
            'SAVE10': { discount: 10, message: '10% discount applied successfully!' },
            'SAVE20': { discount: 20, message: '20% discount applied successfully!' },
            'WELCOME': { discount: 15, message: 'Welcome discount of 15% applied!' },
            'FREESHIP': { discount: 0, message: 'Free shipping applied!' }
        };
        */

        function showMessage(text, type) {
            messageDiv.textContent = text;
            messageDiv.className = `message ${type} show`;
            
            /*
            setTimeout(() => {
                messageDiv.classList.remove('show');
            }, 5000);
            */
        }

        function applyPromoCode() {
            const code = promoInput.value.trim().toUpperCase();
            
            if (!code) {
                showMessage('⚠️ Please enter a promo code', 'error');
                return;
            }

            applyBtn.disabled = true;
            applyBtn.textContent = 'Applying...';

            // Simulate API call
            setTimeout(() => {
                
                // defining request variable
                const request = new Request(
                    `promo-code/verify/`,
                    {
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': csrftoken,
                            'Content-Type': 'application/json' 
                        },
                        mode: 'same-origin', 
                        body: JSON.stringify({ 'promo_code' : code})
                    }
                );
                
                fetch(request)
                    .then(response => response.json())
                    .then(data => {
                        
                        if (data['status'] == 'success'){
                            showMessage(`✓ ${data['message']}`, 'success');
                            promoInput.value = '';      
                        }
                        else {
                            showMessage(`✗ ${data['error']}`, 'error');   
                        }

                    })
                    .catch(error => {
                        console.log('Error : ', error);
                    });

                
                applyBtn.disabled = false;
                applyBtn.textContent = 'Apply';
                
            }, 1000);
        }

        applyBtn.addEventListener('click', applyPromoCode);

        promoInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                applyPromoCode();
            }
        });

        // Convert input to uppercase as user types
        promoInput.addEventListener('input', (e) => {
            e.target.value = e.target.value.toUpperCase();
        });