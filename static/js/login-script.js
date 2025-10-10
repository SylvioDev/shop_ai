// Password toggle
const togglePassword = document.getElementById('togglePassword');
const passwordField = document.getElementById('password');
if (togglePassword) {
    togglePassword.onclick = () => {
        const type = passwordField.type === 'password' ? 'text' : 'password';
        passwordField.type = type;
        togglePassword.classList.toggle('bi-eye');
        togglePassword.classList.toggle('bi-eye-slash');
    
    }

  }

/*
togglePassword.addEventListener('onclick', (event) => {
  const type = passwordField.type === 'password' ? 'text' : 'password';
  passwordField.type = type;
  togglePassword.classList.toggle('bi-eye');
  togglePassword.classList.toggle('bi-eye-slash');
});
*/

/*
// Form validation
const form = document.getElementById('loginForm');
const username = document.getElementById('username');
const usernameError = document.getElementById('usernameError');
const password = document.getElementById('password');
const passwordError = document.getElementById('passwordError');

form.addEventListener('submit', function (e) {
  let valid = true;

  if (username.value.trim() === '') {
    usernameError.style.display = 'block';
    valid = false;
  } else {
    usernameError.style.display = 'none';
  }

  if (password.value.trim() === '') {
    passwordError.style.display = 'block';
    valid = false;
  } else {
    passwordError.style.display = 'none';
  }

  if (!valid) e.preventDefault();
});
*/