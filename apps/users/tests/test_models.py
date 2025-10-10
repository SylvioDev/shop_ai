from django.db import models 
import pytest
from apps.users.tests.factories import UserFactory, UserProfileFactory
from apps.users.models import user_directory_path

pytestmark = pytest.mark.django_db

#### TestUserProfileModel ####

class TestUserProfileModel:
    def test_userprofile_str_returns_correctly(self, user_profile):
        assert str(user_profile) == 'testuser0 Profile'

    @pytest.mark.parametrize("filename", ["avatar.png", "photo.jpg", "image.jpeg"])
    def test_user_directory_path_various_filenames(self, user_profile, filename):
        path = user_directory_path(user_profile, filename)
        assert path == f"media/profile_pics/user_{user_profile.user.id}/{filename}"

#### TestUserProfileModel ####
