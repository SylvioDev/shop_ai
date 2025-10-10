# accounts/tests/conftest.py
import pytest
from apps.users.tests.factories import UserFactory, UserProfileFactory
from django.contrib.auth.models import User

@pytest.fixture
def user():
    return UserFactory()

@pytest.fixture
def user_profile():
    return UserProfileFactory()
