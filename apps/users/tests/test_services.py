import pytest
from django.contrib.auth.models import User
from apps.container import container
from apps.conftest import pytestmark
from apps.users.services import SignupService
from apps.users.models import Address

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
    def test_credentials_inexisting_user(self, active_user):
        result = container.login_service.valid_user({'identifier':'paul', 'password':'123'})
        assert 'Invalid username' in result.get('error')

    def test_credentials_wrong_password(self, active_user):
        result = container.login_service.valid_user({'identifier':'rakoto', 'password':'888'})
        assert 'Invalid username' in result.get('error')

    def test_credentials_inactive_user(self, inactive_user):
        result = container.login_service.valid_user({'identifier':'rakoto', 'password':'123'})
        assert 'Account disabled' in result.get('error')

    def test_credentials_username_success(self, active_user):
        result = container.login_service.valid_user({
            'identifier':'rakoto',
            'password' : '123'
        })
        assert 'user' in result
        
    def test_credentials_email_success(self, active_user):
        result = container.login_service.valid_user({
            'identifier':'test@example.com',
            'password' : '123'
        })
        assert 'user' in result
class TestSignupService:
    def test_repo_initialization(self):
        repo = container.signup_service
        assert isinstance(repo, SignupService)

    def test_signup_user_valid(self):
        data = {
            'username':'test', 
            'password':'123',
            'email':'test@gmail.com'
        }
        user = container.signup_service.signup_user('localhost', data)
        assert isinstance(user, User)
        address = container._user_repo.retrieve_adress(user)
        assert isinstance(address, Address)

    def test_signup_user_invalid(self):
        data = {'userne':'toto', 'password':'8789', 'email':'toto@gmail.com'}
        with pytest.raises(KeyError) as exc_info:
            user = container.signup_service.signup_user('localhost', data)
        assert str(exc_info.value) == "'username'"