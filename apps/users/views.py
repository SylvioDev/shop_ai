import os
import uuid
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.views.generic import UpdateView
from django.contrib.auth.views import PasswordResetView
from .forms import SignupForm
from .forms import LoginForm
from .forms import VerifyPasswordForm
from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, get_backends
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import FormView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from .tools.tools import parse_date
from .tools.tools import full_name
from django.contrib.auth.hashers import check_password
from .tools.tools import require_password_verification
from django.utils.decorators import method_decorator
from django.utils.http import url_has_allowed_host_and_scheme
from .models import PendingEmailChange, UserProfile
from django.conf import settings 
from django.urls import reverse
from django.contrib.auth.views import PasswordResetConfirmView
from django.http import HttpResponse
from .services import SignupService
from .services import LoginService
from django.utils.http import urlsafe_base64_decode
from django.core.mail import send_mail

def activate_account(request, uidb64, token):
    """
    Activate new user account

    Args:
        uidb64 (str) : user encoded id
        token (str) : 64-bit encoded token 

    Returns:
        HttpResponse with message according to the activation status
    """
    user_id = urlsafe_base64_decode(uidb64).decode('utf-8') 
    user = User.objects.get(id=user_id)
    token_is_valid = default_token_generator.check_token(user, token) # checks token validation
    if token_is_valid:
        if user.is_active is False:
            user.is_active = True # activate user
            user.save()
        else:
            return HttpResponse(f'The activation link has expired')
    else:
        return HttpResponse('The activation link is invalid')
    
    return render(request, 'signup_success.html')

class LoginView(FormView):
    """
    Login class reponsible of user authentication

    Attributes:
        template_name (str) : HTML page to render
        form_class (class) : Login Form to render
        success_url () : 

    Methods :
        dispatch(request) : 
            Preprocess request
        
        get(request):
            Handle get requests
        
        post(request):
            Handle post requests

    """
    
    template_name = 'login.html'
    form_class = LoginForm
    success_url = reverse_lazy('products') 

    def dispatch(self, request, *args, **kwargs):
        """
        Preprocess request before it being processed by the GET method

        Returns:
            redirect to products page if there is already an authenticated user connected
        """
        if request.user.is_authenticated:
            return redirect(self.success_url)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        """ Display the login page with LoginForm """
        form = self.form_class()
        return render(request, self.template_name, {'form' : form})
    
    def post(self, request):
        """
        Handle post requests. 

        Returns:
            Redirects user to products if success or send an error to template

        """
        form = self.form_class(request.POST)
        if form.is_valid():
            obj_user = LoginService().valid_user(form_data=form.cleaned_data)
            if obj_user.get('user'):
                auth_login(self.request, obj_user.get('user'))
                return redirect(self.success_url)
            else:
                error = LoginService().valid_user(form.cleaned_data).get('error')
                return render(self.request, self.template_name, {'form' : form, 'error':error})
        
        return render(self.request, self.template_name, {'form' : form})
        
class SignupView(FormView):
    """
    Signup class responsible of user registration.
    
    Attributes:
        template_name (str) : HTML to render
        form_class (class) : Login Form to render
        success_url () : url to process for successful signup

    Methods :        
        get(request):
            Handle get requests
        
        post(request):
            Handle post requests

        
    """
    template_name = 'signup.html'
    form_class = SignupForm
    success_url = reverse_lazy('login')

    def get(self, request):
        """ Display signup page with SignupForm form """
        form = self.form_class()
        return render(request, self.template_name, {'form' : form})
        
    def post(self, request):
        """
        Handle post requests. Create a new user and redirects it to products if successful
        """
        form = self.form_class(request.POST)
        if form.is_valid():
            domain = get_current_site(request).domain
            new_user = SignupService().signup_user(domain, form.cleaned_data)
            return render(request, 'check_email.html', {'user' : new_user})
        return render(request, self.template_name, {'form' : form})

def social_login_error(request):
    return render(request, 'login_error.html', {
        'message' : 'An account with this email already exists'
    })

@login_required
def logout(request):
    """Disconnect connected user with a message """
    user = request.user
    auth_logout(request)
    return render(request, 'logout.html', {'username' : user.username})

def verify_password(request):
    """
    Function that ask user's password for verification.
    It prevents unauthorized access to sensitive request 

    Returns:
        redirects to the next_protected_url for valid password.
        sends a message to verify_password template for invalid password.

    """
    user = request.user
    success_url = request.GET.get('next') or request.session.get('next_protected_url') or '/'

    # Security: make sure it's safe
    if not url_has_allowed_host_and_scheme(success_url, allowed_hosts={request.get_host()}):
        success_url = '/'

    if request.method == 'GET':
        form = VerifyPasswordForm()
        return render(request, 'verify_password.html', {'form':form})
    else:
        form = VerifyPasswordForm(request.POST)
        password = request.POST.get('password')

        valid_password = check_password(password, user.password)
        if valid_password:
            request.session['password_verified'] = True
            return redirect(success_url)
            
        error = None if valid_password else 'Invalid password ! '
        return render(request, 'verify_password.html', {'error' : error})

@method_decorator(require_password_verification, name='dispatch')
class UpdateEmailView(UpdateView):
    """
    Class responsible of email update request.

    Args:
        UpdateView (class) : Django's built-in email update which UpdateEmailView inherits

    Attributes:
        model (class) 
        template_name (str) : HTML page for presentation

    Methods:
        get(request):
            Handle get requests
        
        post(request):
            Handle post requests
        
    """
    model = User 
    template_name = 'update-email.html'

    def get(self, request):
        """Handle get requests """
        return render(request, 'update-email.html')

    def post(self, request):
        """
        Handle post requests. 
        Send an email with to the new email for verification.

        Returns:
            redirect to email done 

        """
        new_email = request.POST.get('new_email')
        
        if User.objects.filter(email=new_email).exists():
            error = f'email "{new_email}" already exists'
            return render(request, self.template_name, {'error' : error})

        token = uuid.uuid4().hex


        PendingEmailChange.objects.create(
            user=request.user,
            new_email=new_email,
            token=token
        )

        confirm_url = request.build_absolute_uri(
            reverse('update-email-confirm', args=[token])
        )

        send_mail(
            subject="Confirm your email change",
            message=f"Click the link to confirm your email change: {confirm_url}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[new_email],
        )

        return redirect('update-email-done')
        
def update_email_done(request):
    return render(request, 'update-email-done.html')

def confirm_email_change(request, token):
    """
    Function that confirms verified new email

    Args:
        token (str): 64-bit encoded token

    Returns:
        An message for email change confirmation
    """
    try:
        pending = PendingEmailChange.objects.get(token=token)
    except PendingEmailChange.DoesNotExist:
        return render(request, "update-email-complete.html", {
            "error": "Invalid or expired link."
        })

    if pending.is_expired():
        pending.delete()
        return render(request, "update-email-complete.html", {
            "error": "This confirmation link has expired."
        })

    user = pending.user
    user.email = pending.new_email
    user.save()
    pending.delete()

    return render(request, "update-email-complete.html", {
        "success": "Your email has been updated successfully."
    })

### Password reset in one time ###

class CustomPasswordResetView(PasswordResetView):
    def form_valid(self, form):
        email = form.cleaned_data["email"]
        try:
            user = UserProfile.objects.get(user__email=email)
        except UserProfile.DoesNotExist:
            form.add_error('email', f"Email {email} doesn't exist")
            return super().form_invalid(form)
        user.save()
        return super().form_valid(form)
    
def password_reset_confirm(request, uidb64, token): 
    try:
        user_id = urlsafe_base64_decode(uidb64).decode('utf-8')
        user = User.objects.get(id=user_id)
    except (UnicodeDecodeError, User.DoesNotExist):
        return HttpResponse('Invalid link or expired !')
    if request.method == 'GET':
        token_is_valid = default_token_generator.check_token(user, token)
        if not token_is_valid:
            return HttpResponse('Invalid link or expired !')
        return render(request, 'registration/password_reset_confirm.html')
    else:
        password = request.POST.get('new_password1')
        confirm_password = request.POST.get('new_password2')
        if password == confirm_password:
            user.set_password(password) 
            user.save()
            backend = get_backends()[0]
            user.backend = f"{backend.__module__}.{backend.__class__.__name__}"
            auth_login(request, user)
            return redirect('password_reset_complete')
        else:
            error = 'Password doesn\'t match !'    
        return render(request, 'registration/password_reset_confirm.html', {'error' : error})

#### Profile and Edit Profile Views ####

class ProfileView(LoginRequiredMixin, TemplateView):
    """
    View for displaying user profile information.

    This view handles the display of user profile data including personal information,
    profile picture.

    LoginRequiredMixin make sure only authenticated users can access this view.

    Args:
        LoginRequiredMixin (class) : django built-in decorators similar to login_required.
        TemplateView (class) : django built-in view for displaying content on a HTML page

    Returns:
        A context data with user informations and User instance model
    """

    model = User
    template_name = 'profile.html'
    
    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)

    def get(self, request):
        user = request.user
        return render(request, 
                      self.template_name, 
                      {
                          'user':user, 
                          'membership_date' : parse_date(str(user.date_joined)),
                          'full_name' : full_name(user),
                          'social_media' : user.userprofile.social_media_username if user.userprofile.social_media_username != None else ''
                      }
                    )

class EditProfileView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'edit-profile.html'

    def get(self, request):
        user = request.user
        return render(request, 
                      self.template_name,
                      {
                          'user' : user,
                          'full_name' : full_name(user),
                          'membership_date' : parse_date(str(user.date_joined))
                      }
                    )
    
    def post(self, request):
        user = request.user
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        profile_picture = request.FILES['profile-pic'] if request.FILES else None
        facebook_username = request.POST.get('facebook')
        user.username = username
        user.userprofile.social_media_username = facebook_username
        user.first_name = first_name
        user.last_name = last_name
        if profile_picture:
            save_path = os.path.join(settings.MEDIA_ROOT, f'profile_pics\\user_{user.id}\\{profile_picture.name}')
            with open(save_path, 'wb') as output_file:
                for chunk in profile_picture.chunks():
                    output_file.write(chunk)
            user.userprofile.profile_picture = f'profile_pics/user_{user.id}/{profile_picture.name}'
        user.save()
        return redirect('profile')