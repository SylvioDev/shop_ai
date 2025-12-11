from django.db import models 
import pytest
from apps.users.tests.factories import (
    UserFactory, 
    UserProfileFactory
)
from apps.users.models import user_directory_path

pytestmark = pytest.mark.django_db

#### TestUserProfileModel ####

class TestUserProfileModel:
    def test_userprofile_str_returns_correctly(self, user_profile):
        assert str(user_profile) == 'testuser0 Profile'

    

#### TestUserProfileModel ####
