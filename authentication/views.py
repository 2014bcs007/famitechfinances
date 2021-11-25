from django.shortcuts import render,redirect
from django.views import View
from django.http import JsonResponse
from django.contrib.auth.models import User
import json
from validate_email import validate_email
from django.contrib import messages
from django.core.mail import EmailMessage
from django.urls import reverse

from django.utils.encoding import force_bytes,force_text,DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from .utils import token_generator
from django.contrib import auth
from django.contrib.auth.tokens import PasswordResetTokenGenerator
import threading
# Create your views here.
# Handle multi threading to send emails

class EmailThread(threading.Thread):
    def __init__(self,email):
        self.email = email
        threading.Thread.__init__(self)
    def run(self):
        self.email.send(fail_silently=False)
# logout LogoutView
class LogoutView(View):
    def post(self,request):
        auth.logout(request)
        messages.success(request,'You are now Logged out')
        return redirect('login')

class LoginView(View):
    def get(self,request):
        return render(request, 'authentication/login.html')
    
    def post(self,request):
        username = request.POST['username']
        password = request.POST['password']

        if username and password:
            user = auth.authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    auth.login(request, user)
                    messages.success(request, 'Welcome '+user.username +'You are now logged in')
                    return redirect('index')

                messages.error(request, 'Account is not activated')
                return render(request, 'authentication/login.html')
            messages.error(request, 'Invalid credentials')
            return render(request, 'authentication/login.html')

        return render(request, 'authentication/login.html')

class RegistrationView(View):
    def get(self,request):
        return render(request, 'authentication/register.html')

    def post(self,request):
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirmPassword = request.POST['confirmPassword']

        context ={
            'fieldValues': request.POST
        }

        if not User.objects.filter(username=username).exists():
            if not User.objects.filter(email=email).exists():
                if len(password) < 6:
                    messages.error(request, 'Password too short')
                    return render(request, 'authentication/register.html',context)
                user = User.objects.create_user(username=username, email=email)
                user.set_password(password)
                user.is_active = False
                user.save()
                email_subject ='Activate Your Account Please'
                '''' The domain
                    The relative url to verification
                    The uid64
                '''
                uidb64 = urlsafe_base64_encode(force_bytes(user.pk))

                domain = get_current_site(request).domain
                link = reverse('activate',kwargs={
                    'uidb64':uidb64,
                    'token':token_generator.make_token(user),
                    })
                activation_link = 'http://'+domain+link
                # path = 
                email_body ='Hello'+username+'Thanks for choosing famitech finances'+',Please use this link to verify your account' +activation_link

                email = EmailMessage(
                            email_subject,
                            email_body,
                            'noreply@seymcolon.com',
                            [email],
                        )
                EmailThread(email).start()

                messages.success(request, 'Account Successfully Created, Visit your email to verify your account')
                return render(request, 'authentication/register.html')
        return render(request, 'authentication/register.html')

class VerificationView(View):
    def get(self,request,uidb64,token):

        try:
            id = force_text(urlsafe_base64_encode(uidb64))
            user = User.objects.get(pk=id)

            if not token_generator.check_token(user,token):
                return redirect('login'+'?message='+'User Already Activated')
            if user.is_active:
                return redirect('login')
            user.is_active=True
            user.save()

            messages.success(request, 'Account Activated Successfully')
            return redirect('login')

        except Exception as ex:
            pass

        return redirect('login')
class ResetPasswordView(View):
    def get(self,request):
        return render(request, 'authentication/resetpassword.html')
    def post(self,request):
        email = request.POST['email']
        context = {
            'fieldValues':request.POST
        }
        if not validate_email(email):
            messages.success(request,'Please Supply a valid Email')
            return render(request, 'authentication/resetpassword.html',context)
        
        email_subject ='Password Reset link'
        user = User.objects.filter(email=email)
        uidb64 = urlsafe_base64_encode(force_bytes(user[0].pk))

        domain = get_current_site(request).domain
        link = reverse('reset-user-password',kwargs={
                    'uidb64':uidb64,
                    'token':PasswordResetTokenGenerator().make_token(user[0]),
                    })
        activation_link = 'http://'+domain+link
                # path = 
        email_content ='Password there, Please click the this link to reset your account' +activation_link
        
        if user.exists():
            email = EmailMessage(
                                email_subject,
                                email_content,
                                'noreply@seymcolon.com',
                                [email],
                            )
            EmailThread(email).start()
        messages.success(request, 'We have sent a link to your email to Reset your password')
        
        return render(request, 'authentication/resetpassword.html')
    

class SetPasswordView(View):
    def get(self,request):
        return render(request, 'authentication/setnewpassword.html')
# username validation
class UsernameValidationView(View):
    def post(self,request):
        data = json.loads(request.body)

        username = data['username']

        if not str(username).isalnum():
            return JsonResponse({'username_error':'username should only contain alpha numeric characters'},status=400)
        if User.objects.filter(username=username).exists():
            return JsonResponse({'username_valid':'Username already in Use'},status=409)
        return JsonResponse({'username_valid':True})
#  email validation       
class EmailValidationView(View):
    def post(self,request):
        data = json.loads(request.body)

        email = data['email']

        if not validate_email(email):
            return JsonResponse({'email_error':'Email is Invalid'},status=400)
        if User.objects.filter(email=email).exists():
            return JsonResponse({'email_valid':'Email already in Use'},status=409)
        return JsonResponse({'email_valid':True})

class CompletePasswordReset(View):
    # reset-user-password CompletePasswordReset 
    def get(self,request,uidb64,token):
        context={
            'uidb64':uidb64,
            'token':token,
        }


        try:            
            user_id= force_text(urlsafe_base64_decode(uidb64))  # use force_text to create a string
            user = User.objects.get(pk=user_id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                messages.info(request, 'Password link already used, please request a new one')
                return render(request, 'authentication/resetpassword.html')
        except Exception as identifier:
            pass
        return render(request, 'authentication/setnewpassword.html',context)

    def post(self,request,uidb64,token):
        context={
            'uidb64':uidb64,
            'token':token,
        }
        password = request.POST['password']
        confirmPassword = request.POST['confirmPassword']
        if password!=confirmPassword:
            messages.error(request, 'Password Could not match')
            return render(request, 'authentication/setnewpassword.html',context)

        if len(password) < 6:
            messages.error(request, 'Password too short')
            return render(request, 'authentication/setnewpassword.html',context)

        try:  
            # base64.b64decode(s, altchars="-_")
            # user_id= force_text(urlsafe_base64_decode(uidb64).decode())          
            user_id= force_text(urlsafe_base64_decode(uidb64))  # use force_text to create a string
            user = User.objects.get(pk=user_id)
            user.set_password(password)
            user.save()
            messages.success(request,'Password reset successfully, You can login with your new Password')
            redirect('login')
            # return render(request, 'authentication/setnewpassword.html',context)
        except Exception as identifier:
            # import pdb
            # pdb.set_trace()
            messages.info(request, 'Something went wrong, try again')
            return render(request, 'authentication/setnewpassword.html',context)
        