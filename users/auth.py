from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from core.models import Client
from django.contrib.auth.hashers import check_password,make_password

# Whatever the user types into the username field is passed into the standard backend and then here
# If my email is another user's username and I try logging in with my email
# It will match the other user's account before mine as the standard authentication backend is used first
# So I can only log in with my username
# Hence, we will now allow '@' in usernames - peep the RegexValidator in models.py

class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(email=username)
        except UserModel.DoesNotExist:
            return None
        else:
            if user.check_password(password):
                return user
        return None


class ClientAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = Client.objects.get(email=username)
            if user and user.login_active and user.password and check_password(password, user.password):
                return user
        except Client.DoesNotExist:
            return None
        return None
    
    def get_user(self, user_id):
        try:
            user= Client.objects.get(pk=user_id)
            user.is_authenticated=True
            user.is_superuser=False
            user.is_user=False
            user.is_employee=False
            return user
        except: return None

class EmployeeAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        userModel = get_user_model()
        try:
            user = userModel.objects.get(employee_number=username,is_employee=True)
            return user
        except userModel.DoesNotExist:
            return None
        return None
    
    def get_user(self, user_id):
        userModel = get_user_model()
        try:
            user= userModel.objects.get(pk=user_id)
            user.is_client=False
            user.is_user=False
            return user
        except: return None