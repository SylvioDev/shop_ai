import pytest 
from apps.container import container
from apps.conftest import valid_user
from apps.users.models import User
from apps.users.models import Address
from django.urls import reverse

pytestmark = pytest.mark.django_db

class TestSignupRepository:
    def test_user_creation(self):
        user = container.signup_repo.create(
            username='test',
            email='testing@gmail.com'
        )
        assert isinstance(user, User)
        assert user.username == 'test'
        assert user.email == 'testing@gmail.com'
    
    def test_get_by_email_success(self, valid_user):
        user = container.signup_repo.get_by_email(valid_user.email)
        assert isinstance(user, User)
    
    def test_get_by_email_failure(self):
        user = container.signup_repo.get_by_email('false@example.com')
        assert user is None
    
class TestLoginRepository:
    @pytest.mark.parametrize('identifier', [
        'test@example.com',
        'test'
    ])
    def test_login_successful(self, valid_user, identifier):
        user = container.login_repo.get_by_email_or_username(
            identifier=identifier,
            password='123'
        )
        assert isinstance(user, User)
        assert user.username == 'test'
        assert user.email == valid_user.email
    
    @pytest.mark.parametrize('identifier, password', [
        ('unknown', '123'),
        ('unknown@email.com', '123'),
        ('test@example.com', '548')
    ])
    def test_login_failure(self, valid_user, identifier, password):
        user = container.login_repo.get_by_email_or_username(
            identifier=identifier,
            password=password
        )
        assert user is None
        
class TestUserRepository:
    def test_retrieve_user_success(self, valid_user):
        user = container.user_repo.retrieve_user(valid_user.id)
        assert isinstance(user, User)
        
    def test_retrieve_user_failure(self, valid_user):
        user = container.user_repo.retrieve_user(8)
        assert isinstance(user, User) is False
        assert user is None
        
    def test_retrieve_address(self, valid_user):
        address = container.user_repo.retrieve_adress(valid_user)
        assert isinstance(address, Address)
    
    def test_retrieve_address_failure(self):
        user = User.objects.create(
            username='rakoto',
            email='rakoto@gmail.com'
        )
        with pytest.raises(Address.DoesNotExist) as exc_info:
            address = container.user_repo.retrieve_adress(user)
        assert 'Address matching query does not exist.' == str(exc_info.value)
        
    def test_update_user_credentials(self, valid_user):
        data = {
            'username' : 'rakoto',
            'phone-number' : '036 98 745 78',
            'first_name' : 'aa',
            'last_name' : 'bb',
            'facebook' : 'Test profile'
        }
        user = container.user_repo.update_user_credentials(valid_user, data)
        
        assert valid_user.username == data.get('username')
        assert valid_user.first_name == data.get('first_name')
        assert valid_user.last_name == data.get('last_name') 
        assert valid_user.userprofile.phone_number == data.get('phone-number')
        assert isinstance(user, User)
    
    def test_update_user_credentials_missing_keys(self, valid_user):
        data = {}
        with pytest.raises(KeyError) as exc_info:
            user = container.user_repo.update_user_credentials(valid_user, data)    
        assert 'Missing keys' in str(exc_info.value)
    
    def test_update_user_address(self, valid_user):
        data = {
            'street_address' : 'Rue 78 Bis Antananarivo',
            'city' : 'Antananarivo',
            'state' : 'Tanà',
            'zip-code' : '105' 
        }
        updated_address = container.user_repo.update_user_address(valid_user, data)
        
        assert updated_address.street_address == data.get('street_address')
        assert updated_address.city == data.get('city')
        assert updated_address.state == data.get('state')
        assert updated_address.zip_code == data.get('zip-code')
        assert isinstance(updated_address, Address)
        
    def test_update_user_address_failure(self, valid_user):
        data = {}
        with pytest.raises(KeyError) as exc_info:
            updated_address = container.user_repo.update_user_address(valid_user, data)
        assert 'Missing keys' in str(exc_info.value)
    