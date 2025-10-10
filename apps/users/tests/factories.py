# accounts/tests/factories.py
import factory
from django.contrib.auth.models import User
from apps.users.models import UserProfile

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        skip_postgeneration_save=True
        
    # Controlled usernames for tests; auto-increment to avoid duplicates
    username = factory.Sequence(lambda n: f"testuser{n}")
    email = factory.Sequence(lambda n: f"testuser{n}@example.com")
    password = factory.PostGenerationMethodCall('set_password', 'password123')

class UserProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserProfile
        skip_postgeneration_save=True  # avoids the warning

    # Create a fresh user by default
    user = factory.SubFactory(UserFactory)
    social_media_username = factory.Sequence(lambda n: f"social{n}")
    profile_picture = None
    reset_token_used = False

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        user = kwargs.get("user")
        if user:
            # Prevent UNIQUE constraint: reuse existing profile if it exists
            profile, created = model_class.objects.get_or_create(user=user, defaults=kwargs)
            return profile
        return super()._create(model_class, *args, **kwargs)
