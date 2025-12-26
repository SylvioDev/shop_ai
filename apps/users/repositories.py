from .models import (
    User,
    Address
)
from django.db.models import Q
from django.contrib.auth.models import User as UserAnnotation
from apps.container import container
from django.core.files.uploadedfile import UploadedFile
class SignupRepository:
    """
    Handles database interactions for signup workflow.

    Methods:
        - create (**kwargs : dict) -> UserAnnotation : create new user inside database.
        - get_by_email (email : str) -> UserAnnotation : retrieve user instance by email
        
    """
    def create(self, **kwargs : dict) -> UserAnnotation:
        """Create new user and add it inside database."""
        return User.objects.create_user(**kwargs)

    def get_by_email(self, email:str) -> UserAnnotation | None:
        """Retrieve user by email """
        return User.objects.filter(email=email).first()

class LoginRepository:
    """
    Handles database interactions for login workflow.

    Methods:
        - get_by_email_or_username (**kwargs : dict) -> UserAnnotation :
            Retrieve user by username or email.
    
    """
    def get_by_email_or_username(self, **kwargs) -> UserAnnotation:
        """
        Retrieve user instance by email or username.
        Check provided password with user password for verification.
        
        Returns:
            User instance model or None  
        """
        identifier = kwargs['identifier']
        try:
            user = User.objects.get(Q(username__iexact=identifier) | Q(email__iexact=identifier))
        except User.DoesNotExist:
            user = None
        
        if user and user.check_password(kwargs['password']):
            return user
        return None
    
class UserRepository:
    """
    Service for handling user data retrieval.
    
    Methods:
        - retrieve_user (user_id) -> User : Retrieve user instance by ID.
        - retrieve_address (user_instance : User) -> Address : Retrieve address for given user. 
        
    """
    def retrieve_user(self, user_id) -> User:
        """
        Retrieve user instance by ID.
        """
        return User.objects.filter(id=user_id).first()

    def retrieve_adress(self, user_instance : User):
        """
        Retrieve address for given user.
        """
        user_address = Address.objects.get(user=user_instance)
        return user_address
    
    def update_user_credentials(self, user_instance : User, data : dict) -> User:
        """
        Update user credentials
        
        Args:
            user_instance (User): The user instance whose profile picture is to be updated.
            data (dict) : Dictionary that contains user informations to update.
        
        Returns:
            User: The updated user instance with the new informations.
        
        """
        username = data.get('username')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        facebook_username = data.get('facebook')
        phone_number = data.get('phone-number')
    
        user_instance.username = username
        user_instance.first_name = first_name
        user_instance.last_name = last_name
        user_instance.userprofile.social_media_username = facebook_username
        user_instance.userprofile.phone_number = phone_number
        user_instance.save()
    
        return user_instance
    
    def update_user_picture(self, user_instance : User, profile_pic : UploadedFile) -> User:
        """
        Update user's profile picture.
        
        Args:
            user_instance (User): The user instance whose profile picture is to be updated.
            profile_pic (UploadedFile): The new profile picture file to upload.
            
        Returns:
            User: The updated user instance with the new profile picture.
        
        """
        user_instance.userprofile.profile_picture.save(profile_pic.name, profile_pic)
        user_instance.userprofile.save()

        return user_instance
    
    def update_user_address(self, user_instance : User, data : dict) -> Address:
        """
        Update user address information
        
        Args:
            user_instance (User): The user instance whose profile picture is to be updated.
            data (dict) : Dictionary that contains user informations to update.
        
        Returns:
            User: The updated address instance with the new informations.
        """
        address = container.user_service.get_user_address(user_instance)
        address.street_address = data.get('street_address')
        address.city = data.get('city')
        address.state = data.get('state')
        address.zip_code = data.get('zip-code')
        address.save()
        
        return address        


    
