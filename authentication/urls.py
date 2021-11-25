from django.urls import path
from .views import *
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('login', LoginView.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('register', RegistrationView.as_view(), name='register'),
    path('UsernameValidationView', csrf_exempt(UsernameValidationView.as_view()), name='UsernameValidationView'),
    path('EmailValidationView', csrf_exempt(EmailValidationView.as_view()), name='EmailValidationView'),
    path('activate/<uidb64><token>', VerificationView.as_view(), name='activate'),
    path('reset-user-password/<uidb64><token>', CompletePasswordReset.as_view(), name='reset-user-password'),
    path('resetpassword', ResetPasswordView.as_view(), name='resetpassword'),
    path('setnewpassword', SetPasswordView.as_view(), name='setnewpassword')
]
#  