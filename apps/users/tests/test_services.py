import pytest
from apps.users.services import LoginService
from django.contrib.auth.models import User

@pytest.fixture
def active_user():
    return User.objects.create_user(
        username='rakoto',
        email='test@example.com',
        password='123'
    )

@pytest.fixture
def inactive_user():
    user = User.objects.create_user(
        username='rakoto',
        email='test@example.com',
        password='123'
    )
    user.is_active = False 
    user.save()
    return user

class TestLoginService:
    @pytest.mark.django_db
    def test_credentials_inexisting_user(self, active_user):
        result = LoginService().valid_user({'identifier':'paul', 'password':'123'})
        assert 'Invalid username' in result.get('error')

    @pytest.mark.django_db
    def test_credentials_wrong_password(self, active_user):
        result = LoginService().valid_user({'identifier':'rakoto', 'password':'888'})
        assert 'Invalid username' in result.get('error')

    @pytest.mark.django_db
    def test_credentials_inactive_user(self, inactive_user):
        result = LoginService().valid_user({'identifier':'rakoto', 'password':'123'})
        assert 'Account disabled' in result.get('error')

    @pytest.mark.django_db
    def test_credentials_username_success(self, active_user):
        result = LoginService().valid_user({
            'identifier':'rakoto',
            'password' : '123'
        })
        assert 'user' in result
        
    @pytest.mark.django_db
    def test_credentials_email_success(self, active_user):
        result = LoginService().valid_user({
            'identifier':'test@example.com',
            'password' : '123'
        })
        assert 'user' in result
    