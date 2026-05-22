import pytest
from apps.conftest import pytestmark
from apps.conftest import valid_user
import json
from django.urls import reverse
from .api_fixtures import token

class TestToken:
    def test_invalid_credentials(self, client, valid_user):
        data = {'username':'test', 'password':'wrong_credentials'}
        response = client.post(reverse('get-token'), data=data)
        assert response.status_code == 401
        assert response.json().get('detail') == 'No active account found with the given credentials'

    def test_valid_credentials(self, client, valid_user):
        data = {'username':'test', 'password':'mypassword'}
        response = client.post(reverse('get-token'), data=data)
        assert response.status_code == 200
        json_response = response.json()
        assert json_response.get('access') is not None
        assert json_response.get('refresh') is not None
        
class TestRegister:
    def test_duplicate_email(self, client, valid_user, token):
        data = {'username' : 'test', 'password' : 'mypassword'}
        extra_headers = {'HTTP_AUTHORIZATION':f'Bearer {token}'}
        user_data = {'username':'example', 'email':'test@example.com', 'password':'1234'}
        response = client.post(
            reverse('register'), 
            data=json.dumps(user_data), 
            content_type='application/json',
            **extra_headers
        )
        assert response.status_code == 400
        assert ''.join(response.json().get('email')) == 'Email already in use.'
    
    def test_valid_credentials(self, client, valid_user, token):
        data = {'username' : 'test', 'password' : 'mypassword'}
        extra_headers = {'HTTP_AUTHORIZATION':f'Bearer {token}'}
        user_data = {'username':'example', 'email':'example@gmail.com', 'password':'1234'}
        response = client.post(
            reverse('register'), 
            data=json.dumps(user_data), 
            content_type='application/json',
            **extra_headers
        )
        assert response.status_code == 201
        assert response.json().get('message') == 'User successfully registered via JSON'

class TestUnauthorizedAccess:
    def test_protected_endpoints(self, client):
        response = client.post(reverse('register'))
        assert response.status_code == 401
        assert response.json().get('detail') == 'Authentication credentials were not provided.'