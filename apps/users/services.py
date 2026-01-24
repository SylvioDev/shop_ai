from django.contrib.auth import get_backends
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.contrib.auth.models import User
from apps.container import container
from apps.users.models import Address

def get_backend(user : User):
    backend = get_backends()[0]
    user.backend = f"{backend.__module__}.{backend.__class__.__name__}"

def send_mail_confirm(request_domain : str, user : User):
    """
    Sends email confirmation to new user's email address for verfication.

    Args:
        request_domain (str) : website's full domain
        user (User) : User instance 
     
    """
    domain = request_domain
    user_id = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    confirmation_link = f'accounts/activate-account/{user_id}/{token}'
    full_url = f'http://{domain}/{confirmation_link}'
    subject = 'Confirm your account'
    html_message = \
    f"""
        <h3>Hi {user.username} </h3>,
        Please confirm your email address by clicking the link below:
        {full_url}
        If you didn't sign up, you can ignore this email.

    """

    message = \
    f"""
        Hi {user.username},
        Please confirm your email address by clicking the link below:
        {full_url}
        If you didn't sign up, you can ignore this email.
    """ 
    send_mail(subject, message, 'no-reply@localhost', [user.email], html_message=html_message)

class SignupService:
    """
    Service layer handling business logic for signup-related operations.

    This service manages the complete user signup workflow including 
    account creation and email verification.

    Attributes:
        repo (SignupRepository) : The repository instance used for database interactions.

    Methods:
        signup_user (domain : str, domain : str, form_data : dict) -> User:

    """
    
    def __init__(self, signup_repo):
        self.repo = signup_repo

    def signup_user(self, domain : str, form_data : dict) -> User:
        """
        Creates a new user in the database.

        Args:
            domain (str): full website domain eg : https://www.shopai.com
            form_data (dict) : a dict that contains the submitted form fields from the POST request

        Returns:
            User model instance. The new user is verified and is active.

        """
        username = form_data['username']
        password = form_data['password']
        email = form_data['email']
        data = {
            'username' : username,
            'email' : email,
            'password' : password,
            'is_active' : False
        }
        user = self.repo.create(**data)
        send_mail_confirm(domain, user)
        return user

class LoginService:
    """
    Handles user authentication and login operations

    This service manages complete login workflow including credentials validation,
    session management and verification (whether if user is active or not).
    Email or username can be used to authenticate users.

    Attributes:
        repo (LoginRespository) : The repository instance used for database interactions.
    
    """
    def __init__(self, login_repo):
        self.repo = login_repo

    def valid_user(self, form_data:dict):
        """
        Authenticate user 

        Args:
            form_data (dict): a dict that contains the submitted form fields from the POST request

        Returns :
        dict : The user authentication result:
            - User model instance => successful 
            - Account disabled, please activate it first => user is inactive.
            - Invalid username or password => invalid credentials provided such as wrong password or 
                unexisting username.

        """
        login_data = {
            'identifier' : form_data['identifier'],
            'password' : form_data['password']
        }
        existing_user = self.repo.get_by_email_or_username(**login_data)
        if existing_user: # valid username and password 
            get_backend(existing_user)
            if existing_user.is_active:
                return {'user':existing_user}
            else:
                return {'error':'Account disabled, please activate it first'}
        else:
            return {'error' : 'Invalid username or password'}

class UserService:
    """
    Service layer handling business logic for user-related operations.
    This service manages user data retrieval and profile management.
    
    Attributes:
        repository (UserRepository) : The repository instance used for database interactions.
    
    Methods:
        get_user_credentials(user_id : int) -> User:
            Retrieves user credentials by user ID.

        get_user_address(user_instance) -> Address:
            Retrieves the address associated with a user instance. 
    """
    def __init__(self, user_repo):
        self.repository = user_repo
        
    def get_user_credentials(self, user_id : int) -> User:
        """
        Retrieve user credentials by user ID.
        
        Args:
            user_id (int): The user ID. 
            
        Returns:
            User instance corresponding to the given user ID.       
        """
        user = self.repository.retrieve_user(user_id)
        return user
    
    def get_user_address(self, user_instance):
        """
        Retrieve the address associated with a user instance.
        
        Args:
            user_instance (int): The user instance or user ID.
            
        Returns:
            Address instance associated with the user.
        """
        try:
            user_address = self.repository.retrieve_adress(user_instance)
            return user_address
        except Address.DoesNotExist as error:
            return error
        
    def update_profile(self, user_instance : User, data : dict):
        """
        Update user profile informations
        
        Args:
            user_instance (user) : The user instance to update.
            data (dict) : Dictionary that contains user informations to update from request.
            
        """
        address = container.user_repo.update_user_address(user_instance, data)
        profile = container.user_repo.update_user_credentials(user_instance, data)
        
        if data['profile-pic'] is not None:
            profile_picture = container.user_repo.update_user_picture(user_instance, data['profile-pic'])

        