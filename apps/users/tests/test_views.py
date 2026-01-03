import pytest
from django.core import mail
from django.urls import reverse
from apps.users.models import User
from apps.users.forms import LoginForm
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
import re 
from django.contrib.auth.tokens import default_token_generator
from time import sleep
from apps.conftest import pytestmark

@pytest.fixture
def valid_user():
    return User.objects.create_user(
        username='test',
        email='test@example.com',
        password='mypassword'
    ).save()

@pytest.fixture
def inactive_user():
    user = User.objects.create_user(
        username='test',
        email='test@example.com',
        password='mypassword'
    )
    user.is_active = False
    user.save()
    return user

@pytest.fixture
def login_url():
    return reverse('login')

#### LoginTest ####

class TestLoginView:
    def test_login_page_get_view(self, client, login_url):
        response = client.get(login_url)
        template = response.content.decode()
        assert response.status_code == 200
        assert 'Please log in into your account' in template
    
    def test_login_page_has_form_in_context(self, client, login_url):
        response = client.get(login_url)
        form = response.context.get('form')
        assert isinstance(form, LoginForm)
        assert form.fields['identifier']
        assert form.fields['password']
        
    def test_login_page_invalid_username(self, client, valid_user, login_url):
        data = {
            'identifier' : 'paul',
            'password' : 'mypassword'
        }
        response = client.post(login_url, data)
        template = response.content.decode()
        assert 'Invalid username' in template

    def test_login_page_invalid_password(self, client, valid_user, login_url):
        data = {
            'identifier' : 'test',
            'password' : 'otherpassword'
        }
        response = client.post(login_url, data)
        template = response.content.decode()
        assert 'Invalid username' in template
    
    def test_login_page_with_inactive_user(self, login_url, client, inactive_user):
        data = {
            'identifier' : 'test',
            'password' : 'mypassword'
        }
        response = client.post(login_url, data)
        template = response.content.decode()
        assert 'Account disabled' in template
    
    def test_login_page_success(self, login_url, client, valid_user):
        data = {
            'identifier' :  'test',
            'password' : 'mypassword'
        }
        response = client.post(login_url, data)
        assert response.status_code == 302
        assert 'products' in response.url 

#### LoginTest ####

#### SignupTest ####

@pytest.fixture
def signup_url():
    return reverse('signup')

@pytest.fixture
def data():
    return {
        'username' : 'rakoto',
        'email' : 'rakoto@example.com',
        'password' : '123',
        'confirm_password' : '565'
    }
class TestSignupView:
    def test_signup_page_get_view(self, signup_url, client, valid_user):
        response = client.get(signup_url)
        html = response.content.decode()
        form = response.context['form']
        assert response.status_code == 200
        assert 'Signup to Shop AI' in html
        assert form.fields['username']
        assert form.fields['email']
        assert form.fields['password']
        assert form.fields['confirm_password']

    def test_signup_page_invalid_existing_username(self, signup_url, client, valid_user):
        data = {
            'username' : 'test',
            'email' : 'rakott@example.com',
            'password' : '123',
            'confirm_password' : '123'

        }
        response = client.post(signup_url, data)
        error_message = response.context['form'].errors.get_json_data()['username'][0]['message']
        assert response.status_code == 200
        assert error_message == 'Username already exist'
    
    def test_signup_page_invalid_existing_email(self, signup_url, client, valid_user):
        data = {
            'username' : 'paul',
            'email' : 'test@example.com',
            'password' : '123',
            'confirm_password' : '123'

        }
        response = client.post(signup_url, data)
        assert response.status_code == 200
        assert 'An account with this email already exists.' in response.context['form'].errors['email']
    
    def test_signup_page_invalid_password_mismatch(self, signup_url, client, data):
        response = client.post(signup_url, data)
        form = response.context['form']
        assert response.status_code == 200
        assert 'Passwords do not match' in form.errors['__all__'].as_text()
    
    def test_signup_page_invalid_token_has_expired(self, signup_url, client, valid_user):
        data = {
            'username' : 'ratrema',
            'email' : 'ratrema@example.com',
            'password' : '123',
            'confirm_password' : '123'
        }
        response = client.post(signup_url, data)
        html = response.content.decode()
        assert response.status_code == 200
        assert f'Thanks for signing up, "{data['username']}"!' in html
        assert len(mail.outbox) == 1
        body = mail.outbox[0].body
        assert f'Hi {data['username']}' in mail.outbox[0].body
        pattern = r"http://testserver/accounts/activate-account/[A-Za-z0-9_\-]+/[A-Za-z0-9_\-]+"
        activation_url = ''.join(re.findall(pattern, body))
        assert activation_url in body
        account_validattion = client.get(activation_url) # simulate user clicking activation_link once
        duplicate_click = client.get(activation_url) # duplicate link click
        html = duplicate_click.content.decode()
        assert 'The activation link has expired' in html
        user = User.objects.get(username=data['username'])
        assert user.is_active is True
    
    def test_signup_page_invalid_token_is_invalid(self, signup_url, client, inactive_user):
        user = User.objects.get(username='test')
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        invalid_token = 'invalid_token'
        new_response = client.get(reverse('activate-account', kwargs={'uidb64': uid, 'token':invalid_token}))
        assert 'The activation link is invalid' in new_response.content.decode()
        assert user.is_active == False 
    
    def test_signup_page_success(self, signup_url, client, inactive_user):
        data = {
            'username':'success',
            'email' : 'success@example.com',
            'password' : '123',
            'confirm_password' : '123'
        }
        response = client.post(signup_url, data)
        inactive_user = User.objects.get(username='success')
        assert inactive_user.is_active == False
        html = response.content.decode()
        assert response.status_code == 200
        assert len(mail.outbox) == 1
        
        body = mail.outbox[0].body                
        pattern = r"http://testserver/accounts/activate-account/[A-Za-z0-9_\-]+/[A-Za-z0-9_\-]+"
        activation_url = ''.join(re.findall(pattern, body))
        new_response = client.get(activation_url)
        html = new_response.content.decode()
        assert new_response.status_code == 200
        assert 'Welcome, ! Your account has been activated.' in html
        active_user = User.objects.get(username='success')
        assert active_user.is_active is True        
        
#### SignupTest ####

#### PasswordResetTest ####

@pytest.fixture
def reset_password_url():
    return reverse('password_reset')
class TestPasswordResetView:    
    def test_password_reset_get(self, client, reset_password_url):
        response = client.get(reset_password_url)
        html = response.content.decode()
        assert response.status_code == 200
        assert 'Enter your e-mail address below :' in html 

    def test_password_reset_invalid_fake_email(self, reset_password_url, client, valid_user):
        fake_email = {'email':'fake@email.com'}
        response = client.post(reset_password_url, fake_email)
        error_message = response.context['form'].errors.get_json_data().get('email')[0]['message']
        assert error_message == f"Email fake@email.com doesn't exist"
            
    def test_password_reset_invalid_email(self, reset_password_url, client, valid_user):
        fake_email = {'email':'invalid_email'}
        response = client.post(reset_password_url, fake_email)
        html = response.content.decode()
        assert f"Enter a valid email address" in html 
    
    def test_password_reset_success(self, reset_password_url, client, valid_user):
        real_email = {'email' : 'test@example.com'}
        response = client.post(reset_password_url, real_email)
        html = response.content.decode()
        assert response.status_code == 302
        assert response.url == '/accounts/password-reset/done/'
    
#### PasswordResetTest ####

#### TestPasswordResetDoneView  ####

@pytest.fixture
def password_reset_done_url():
    return reverse('password_reset_done')
class TestPasswordResetDoneView:
    def test_password_reset_done_get(self, password_reset_done_url, client, valid_user):
        response = client.get(password_reset_done_url)
        html = response.content.decode()
        assert 'We’ve emailed you instructions for setting your password' in html

#### TestPasswordResetDoneView  ####

#### TestPasswordResetConfirmView ####

@pytest.fixture 
def password_reset_confirm_url():
    return reverse('password_reset_confirm')

@pytest.fixture
def get_token_and_user_id(reset_password_url, client):
    real_email = {'email' : 'test@example.com'}
    before_response = client.post(reset_password_url, real_email)
    assert len(mail.outbox) == 1
    body = mail.outbox[0].body
    pattern = r'http://testserver/accounts/password-reset-confirm/[A-Za-z0-9_\-]+/[A-Za-z0-9_\-]+'
    reset_link = ''.join(re.findall(pattern, body))
    uidb64 = reset_link.split('/')[5]
    token = reset_link.split('/')[6]
    return  {
        'uidb64' : uidb64,
        'token' : token
    }
class TestPasswordResetConfirmView:
    def test_password_reset_confirm_get(self, reset_password_url, client, valid_user, get_token_and_user_id):
        response = client.get(reverse('password_reset_confirm', kwargs=get_token_and_user_id))
        assert response.status_code == 200
        html = response.content.decode()
        assert 'New password:' in html

    def test_password_reset_confirm_invalid_link_or_expired(self, reset_password_url, client, valid_user, get_token_and_user_id):
        uidb64 = get_token_and_user_id['uidb64']
        token = 'invalid-token'
        url = reverse('password_reset_confirm', kwargs={'uidb64':uidb64, 'token': token})
        response = client.get(url)
        html = response.content.decode()
        assert 'Invalid link or expired !' in html
            
    def test_password_reset_confirm_password_mismatch(self, reset_password_url, client, valid_user, get_token_and_user_id):
        url = reverse('password_reset_confirm', kwargs=get_token_and_user_id)
        data = {
            'new_password1' : 'programming',
            'new_password2' : 'programing'
        }
        new_response = client.post(url, data)
        html = new_response.content.decode('utf-8')
        assert new_response.status_code == 200
        assert 'Password doesn\'t match !'

    def test_password_reset_confirm_password_success(self, client, valid_user, get_token_and_user_id):
        url = reverse('password_reset_confirm', kwargs=get_token_and_user_id)
        data = {
            'new_password1' : 'programming',
            'new_password2' : 'programming'
        }
        new_response = client.post(url, data)
        html = new_response.content.decode()
        assert new_response.status_code == 302
        assert new_response.url == '/accounts/password-reset-complete/'

#### TestPasswordResetConfirmView ####

#### TestVerifyPasswordView ####

@pytest.fixture
def verify_password_url():
    return reverse('verify-password')

class TestVerifyPasswordView:
    def test_verify_password_get(self, verify_password_url, client, valid_user):
        response = client.get(verify_password_url)
        html = response.content.decode()
        form = response.context['form']
        assert response.status_code == 200
        assert 'Enter your password here :' in html
        assert form.fields['password']
    
    def test_verify_password_invalid(self, verify_password_url, client, valid_user):
        data = {'password' : 'invalid'}
        response = client.post(reverse('login'), {'identifier':'test', 'password':'mypassword'})
        new_response = client.post(verify_password_url, data)
        html = response.content.decode()
        error = new_response.context['error']
        assert error == 'Invalid password ! '
        
    def test_verify_password_success(self, verify_password_url, client, valid_user):
        data = {'password' : 'mypassword'}
        response = client.post(reverse('login'), {'identifier':'test', 'password':'mypassword'})
        new_response = client.post(verify_password_url, data)
        assert new_response.status_code == 302
        assert new_response.url == '/'

#### TestVerifyPasswordView ####

#### TestUpdateEmailView ####

@pytest.fixture
def update_email_url():
    return reverse('update-email')

@pytest.fixture 
def login_and_verify_user(client, verify_password_url):
    login_data = {
        'identifier' : 'test',
        'password' : 'mypassword'
    }
    data = {'password':'mypassword'}
    response = client.post(reverse('login'), login_data)
    other_response = client.post(verify_password_url, data)

@pytest.fixture 
def get_token(client, update_email_url, valid_user , login_and_verify_user):
    response = client.post(update_email_url, {'new_email':'mail@gmail.com'})
    body = mail.outbox[0].body 
    pattern = r"[A-Za-z0-9]+/"
    token = ''.join(re.findall(pattern, body)).split('/')[-2]
    return {'token':token}

class TestUpdateEmailView:
    def test_update_email_get_redirected(self, update_email_url, client, valid_user):
        response = client.get(update_email_url)
        assert response.status_code == 302 # user must be verified to change email
        assert 'verify-password' in response.url

    def test_update_email_get_not_redirected(self, update_email_url, client, valid_user, login_and_verify_user):
        new_response = client.get(update_email_url)
        html = new_response.content.decode()
        assert new_response.status_code == 200
        assert 'Enter your new e-mail address below : ' in html
            
    def test_update_email_success(self, update_email_url, client, valid_user, login_and_verify_user):
        data = {'new_email':'mail@gmail.com'}
        response = client.get(update_email_url)
        new_response = client.post(update_email_url, data)
        html = response.content.decode()
        assert len(mail.outbox) == 1
        body = mail.outbox[0].body
        assert 'Click the link to confirm' in body
        assert new_response.url == reverse('update-email-done')  
    
#### TestUpdateEmailView ####

#### TestUpdateEmailConfirmView ####

class TestUpdateEmailConfirmView:
    def test_update_email_confirm_invalid_token(self, client,):
        token = 'invalid_token'
        response = client.get(reverse('update-email-confirm', kwargs={'token':'invalid_token'}))
        assert response.status_code == 200
        assert 'Invalid or expired link' in response.content.decode()

    def test_update_email_confirm_success(self, client, valid_user, get_token):
        token = get_token['token']
        response = client.post(reverse('update-email-confirm', kwargs={'token':token}))
        assert response.status_code == 200
        html = response.content.decode()
        assert 'Your email has been updated successfully.' in html
        
#### TestUpdateEmailConfirmView ####
