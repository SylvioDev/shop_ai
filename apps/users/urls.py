from django.urls import path
from django.contrib.auth import views as auth_views
from .views import(
    SignupView,
    LoginView,
    logout,
    activate_account,
    social_login_error,
    ProfileView,
    EditProfileView,
    verify_password,
    UpdateEmailView,
    update_email_done,
    confirm_email_change,
    CustomPasswordResetView,
    password_reset_confirm
)


urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('signup/', SignupView.as_view(), name='signup'),
    path('login-error/', social_login_error, name='login-error'),
    path('logout/', logout, name='logout'),
    path('activate-account/<uidb64>/<token>', activate_account, name='activate-account'),
    path('password-reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', password_reset_confirm, name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/edit/', EditProfileView.as_view(), name='edit-profile'),
    path('verify-password/', verify_password, name='verify-password'),
    path('update-email/', UpdateEmailView.as_view(), name='update-email'),
    path('update-email/done', update_email_done, name='update-email-done'),
    path('update-email-confirm/<str:token>/', confirm_email_change, name='update-email-confirm'),
    #path('<str:page>/', GetTemplateView.as_view(),name=''),
]