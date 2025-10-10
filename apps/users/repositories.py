from .models import User
from django.db.models import Q
from django.contrib.auth.models import User as UserAnnotation

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

        


    
