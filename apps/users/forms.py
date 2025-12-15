from django import forms
from django.contrib.auth.models import User
from apps.users.models import UserProfile

class SignupForm(forms.Form):
    username = forms.CharField(
        widget = forms.TextInput(
            attrs = {
                'class' : 'form-control input-sm',
                'placeholder' : 'Username'
            },   
        ),
        error_messages = {
                'required' : 'Username field is required'
            }
    )

    email = forms.EmailField(
        widget = forms.EmailInput(
            attrs = {
                'class' : 'form-control input-sm',
                'placeholder' : 'Email'
            }
        ),
        error_messages = {
                'required' : 'Email field is required'
            }
    )

    password = forms.CharField(
        widget = forms.PasswordInput(
            attrs = {
                'class' : 'form-control input-sm',
                'placeholder' : 'Password',
                'id' : 'password'
            }
        ),
        error_messages = {
                'required' : 'Password field is required'
            }
    )

    confirm_password = forms.CharField(
        widget = forms.PasswordInput(
            attrs = {
                'class' : 'form-control input-sm',
                'placeholder' : 'Password',
                'id' : 'confirm-password'
            }
        ),
        error_messages = {
                'required' : 'Confirm Password field is required'
            }
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not username:
            raise forms.ValidationError('Username is required.')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Username already exist')
        return username.lower().strip()
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email.strip()

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not password:
            raise forms.ValidationError('Password is required.')
        return password

    def clean_confirm_password(self):
        confirm_password = self.cleaned_data.get('confirm_password')
        if not confirm_password:
            raise forms.ValidationError('Confirm Password is required.')
        return confirm_password
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError('Passwords do not match')

class LoginForm(forms.Form):
    identifier = forms.CharField(
        widget = forms.TextInput(
            attrs = {
                'class' : 'form-control input-sm',
                'placeholder' : 'azeaze',
                
            }
        )
    )

    password = forms.CharField(
        widget = forms.PasswordInput(
            attrs = {
                'class' : 'form-control input-sm',
                'placeholder' : 'password',
                'id' : 'password'
            
            }
        ),
    )

   
    
class ProfilePictureForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_picture']

class VerifyPasswordForm(forms.Form):
    password = forms.CharField(
        max_length=254,
        widget = forms.PasswordInput(
            attrs = {
                'class' : 'form-control',
                'placeholder' : 'Password',
            }
        ),
        required = True
    )

class UpdateEmailForm(forms.Form):
    email = forms.EmailField(
        max_length=254,
        widget = forms.EmailInput(
            attrs = {
                'class' : 'form-control',
                'placeholder' : 'user@email.com',
            }
        ),
        required = True
    )