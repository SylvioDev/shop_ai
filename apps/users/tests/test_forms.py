import pytest
from django.contrib.auth.models import User
from apps.users.forms import SignupForm
from apps.conftest import pytestmark

#### SignupForm Test ####

def test_empty_username():
    """
    Test for empty username field
    """
    form = SignupForm(data={
        'username' : '',
        'email' : 'example@gmail.com',
        'password' : '123',
        'confirm_password' : '123'
    })

    assert form.is_valid() is False 
    assert 'Username field is required' in ''.join(form.errors['username'])

def test_empty_email():
    """
    Test for empty email field
    """
    form = SignupForm(data={
        'username' : 'rakoto',
        'email' : '',
        'password' : '123',
        'confirm_password' : '123'
    })

    assert form.is_valid() is False 
    assert 'Email field is required' in ''.join(form.errors['email'])

def test_empty_password():
    """
    Test for empty password field
    """
    form = SignupForm(data={
        'username' : 'rakoto',
        'email' : 'test@example.com',
        'password' : '',
        'confirm_password' : '123'
    })

    assert form.is_valid() is False 
    assert 'Password field is required' in ''.join(form.errors['password'])

def test_empty_confirm_password():
    """
    Test for empty confirm_password field
    """
    form = SignupForm(data={
        'username' : 'rakoto',
        'email' : 'test@example.com',
        'password' : '123',
        'confirm_password' : ''
    })

    assert form.is_valid() is False 
    assert 'Confirm Password field is required' in ''.join(form.errors['confirm_password'])

def test_user_already_exists_by_username():
    """ 
    Test signup view, creates a user and 
    verify existing user by its username
    """
    User.objects.create_user(
        username='rakoto',
        email='example@gmail.com',
        password='123',
    )

    form = SignupForm(data={
        'username' : 'rakoto',
        'email' : 'rakoto@example.com',
        'password' : '123',
        'confirm_password' : '123'
    })

    assert form.is_valid() is False 
    assert 'Username' in ''.join(form.errors['username'])  

def test_user_already_exists_by_email():
    """ 
    Test signup view, creates a user and 
    verify existing user by its email
    """
    User.objects.create_user(
        username='rakoto',
        email='example@gmail.com',
        password='123',
    )

    form = SignupForm(data={
        'username' : 'paul',
        'email' : 'example@gmail.com',
        'password' : '123',
        'confirm_password' : '123'
    })

    assert form.is_valid() is False 
    assert 'An account with this email' in ''.join(form.errors['email'])

def test_passwords_do_not_match():
    """ 
    Test for password and confirm_password do not match
    """
    form = SignupForm(data={
        'username' : 'rakoto',
        'email' : 'rakoto@example.com',
        'password' : '456',
        'confirm_password' : '789'
    })

    assert form.is_valid() is False 
    assert 'do not match' in ''.join(form.errors['__all__'])

def test_valid_signup_form():
    """ 
    Test for valid signup form form.is_valid() == True
    """
    form = SignupForm(data={
        'username' : 'rakoto',
        'email' : 'rakoto@example.com',
        'password' : '456',
        'confirm_password' : '456'
    })

    assert form.is_valid() is True
    assert form.cleaned_data['username'] == 'rakoto'
    assert form.cleaned_data['email'] == 'rakoto@example.com'
    assert form.cleaned_data['password'] == form.cleaned_data['confirm_password']

#### SignupForm Test ####


