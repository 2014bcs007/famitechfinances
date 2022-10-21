from django.contrib.auth.password_validation import validate_password
from django import forms
from django.contrib.auth.models import Group,Permission
from allauth.account.forms import LoginForm,SignupForm,ResetPasswordForm,SetPasswordForm,ResetPasswordKeyForm,SetPasswordField, PasswordField
from django.conf import settings
from .models import *
from django.contrib.admin import widgets

from core.models import Term

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Div


excludedContentTypePermissions=["payrollaprover","employmentdonor","requisitionapproval","termmeta","leavehistory","requisitionapprover","requisitionitem","logentry","log","emailaddress","emailconfirmation","config","notification","socialaccount","socialapp","socialtoken","permission","contenttype","session"]

class UserRoleForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UserRoleForm, self).__init__(*args, **kwargs)
        perms=Permission.objects.filter().exclude(content_type__model__in=excludedContentTypePermissions)
        if 'permissions' in self.fields:self.fields['permissions'].queryset=perms
        # Arrange columns as in crispy
        self.helper = FormHelper()
    class Meta:
        model=Group
        fields='__all__'
        widgets={
            'name':forms.TextInput(attrs={'class':'form-control'}),
            # 'permissions':forms.SelectMultiple(attrs={'class':'form-control'}),
            'permissions':forms.CheckboxSelectMultiple(),
        }


class AddUserForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, label='First Name',required=True)
    last_name = forms.CharField(max_length=30, label='Last Name',required=True)
    col1_fields=['first_name','last_name','email','username','password']
    col2_fields=['gender','designation','phone','date_joined']
    # col3_fields=['nssf_number','bank','branch_location','account_number','account_name','tin']
    col3_fields=['department','nin','dob','marital_status','country']
    row2_fields=['profile_pic','is_superuser','is_active','clients','groups','user_permissions']
    def __init__(self, *args, **kwargs):
        super(AddUserForm, self).__init__(*args, **kwargs)
        if 'password' in self.fields and 'initial' in kwargs and kwargs['initial'].get("pop-password",None):
            del self.fields['password']
        if 'groups' in self.fields:
            self.fields['groups'].label="Role(s)"
        if 'department' in self.fields:
            self.fields['department'].queryset=Term.objects.filter(type='departments')
        if 'bank' in self.fields:
            self.fields['bank'].queryset=Term.objects.filter(type='banks')
        
        perms=Permission.objects.filter().exclude(content_type__model__in=excludedContentTypePermissions)
        if 'user_permissions' in self.fields:self.fields['user_permissions'].queryset=perms
        
        if 'first_name' in self.fields:self.fields['first_name'].widget = forms.TextInput(attrs={'type': 'text', 'class': 'form-control'})
        if 'last_name' in self.fields:self.fields['last_name'].widget = forms.TextInput(attrs={'type': 'text', 'class': 'form-control'})
        # if 'country' in self.fields:self.fields['country'].widget = forms.Select(attrs={'class': 'form-control form-control-lg'},choices=settings.COUNTRIES_CHOICES)
        if 'username' in self.fields:self.fields['username'].widget = forms.TextInput(attrs={'type': 'text', 'class': 'form-control'})
        if 'email' in self.fields:self.fields['email'].widget = forms.TextInput(attrs={'type': 'email', 'class': 'form-control'})
        if 'password' in self.fields:
            self.fields['password'].widget = forms.PasswordInput(attrs={'class': 'form-control'})
            self.fields['password'].required=False
            self.fields['password'].validators=[validate_password]
        if 'password1' in self.fields:self.fields['password1'].widget = forms.PasswordInput(attrs={'class': 'form-control'})
        if 'password2' in self.fields:self.fields['password2'].widget = forms.PasswordInput(attrs={'class': 'form-control'})

        

        # Arrange columns as in crispy
        self.helper = FormHelper()
        # self.helper.form_id = 'id_intake_form'
        # self.helper.form_method = 'POST'
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(
                Div(*self.col1_fields, css_class='col-sm-4'),
                Div(*self.col2_fields, css_class='col-sm-4'),
                Div(*self.col3_fields, css_class='col-sm-4'), css_class='row'
            ),
            Div(
                Div(Div(*self.row2_fields), css_class='col-md-12'), css_class='row'
            )
        )

    class Meta:
        model=User
        # exclude=['username','last_login']
        fields='__all__'
        # fields=['clients','country','first_name','last_name','email','username','password','is_active','employee_number','phone','department','gender','designation','nin','profile_pic','dob','marital_status','nssf_number','bank','branch_location','account_number','account_name','tin','date_joined','is_superuser','groups','user_permissions']
        widgets={
            # 'date_joined':forms.DateInput(attrs={'type': 'datetime-local'}),
            'dob':forms.DateInput(attrs={'type': 'date'}),
            'groups':forms.SelectMultiple(attrs={'class':'select2'}),
        }
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if 'password' in self.cleaned_data:
            password = self.cleaned_data.pop('password')
            if password and password!="":
                instance.set_password(password)
        if commit:
            instance.save()
            self.save_m2m()
        return instance


class EmployeeForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, label='First Name',required=True)
    last_name = forms.CharField(max_length=30, label='Last Name',required=True)
    col1_fields=['first_name','last_name','gender','designation','email','username','phone','client']
    col2_fields=['date_joined','is_employee','employee_number','payroll_type','department','nin','dob','marital_status','country']
    col3_fields=['payment_center','nssf_number','bank','branch_location','account_number','account_name','tin','mobile_money_number']
    row2_fields=['profile_pic','employment_attachment','is_active']
    def __init__(self, *args, **kwargs):
        super(EmployeeForm, self).__init__(*args, **kwargs)
        if 'password' in self.fields and 'initial' in kwargs and kwargs['initial'].get("pop-password",None):
            del self.fields['password']
        if 'department' in self.fields:
            self.fields['department'].queryset=Term.objects.filter(type='departments')
        if 'bank' in self.fields:
            self.fields['bank'].queryset=Term.objects.filter(type='banks')
        
        if 'employee_number' in self.fields:self.fields['employee_number'].required=True
        if 'client' in self.fields:self.fields['client'].required=True
        if 'gender' in self.fields:self.fields['gender'].required=True
        if 'first_name' in self.fields:self.fields['first_name'].widget = forms.TextInput(attrs={'type': 'text', 'class': 'form-control'})
        if 'last_name' in self.fields:self.fields['last_name'].widget = forms.TextInput(attrs={'type': 'text', 'class': 'form-control'})
        # if 'country' in self.fields:self.fields['country'].widget = forms.Select(attrs={'class': 'form-control form-control-lg'},choices=settings.COUNTRIES_CHOICES)
        if 'username' in self.fields:self.fields['username'].widget = forms.TextInput(attrs={'type': 'text', 'class': 'form-control'})
        if 'email' in self.fields:self.fields['email'].widget = forms.TextInput(attrs={'type': 'email', 'class': 'form-control'})
        if 'password' in self.fields:
            self.fields['password'].widget = forms.PasswordInput(attrs={'class': 'form-control'})
            self.fields['password'].required=False
            self.fields['password'].validators=[validate_password]
        if 'password1' in self.fields:self.fields['password1'].widget = forms.PasswordInput(attrs={'class': 'form-control'})
        if 'password2' in self.fields:self.fields['password2'].widget = forms.PasswordInput(attrs={'class': 'form-control'})

        

        # Arrange columns as in crispy
        self.helper = FormHelper()
        # self.helper.form_id = 'id_intake_form'
        # self.helper.form_method = 'POST'
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(
                Div(*self.col1_fields, css_class='col-sm-4'),
                Div(*self.col2_fields, css_class='col-sm-4'),
                Div(*self.col3_fields, css_class='col-sm-4'), css_class='row'
            ),
            Div(
                Div(Div(*self.row2_fields), css_class='col-md-12'), css_class='row'
            )
        )

    class Meta:
        model=User
        # exclude=['username','last_login']
        fields='__all__'
        # fields=['client','employment_attachment','country','payment_center','is_employee','mobile_money_number','payroll_type','first_name','last_name','email','username','password','is_active','employee_number','phone','gender','designation','nin','profile_pic','dob','marital_status','nssf_number','bank','branch_location','account_number','account_name','tin','date_joined']
        widgets={
            # 'date_joined':forms.DateInput(attrs={'type': 'datetime-local'}),
            'dob':forms.DateInput(attrs={'type': 'date'}),
            'is_active':forms.HiddenInput(),
            'is_employee':forms.HiddenInput(),
        }
    
    def clean_employee_number(self):
        return self.cleaned_data['employee_number'] or None
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if 'password' in self.cleaned_data:
            print("Password found")
            password = self.cleaned_data.pop('password')
            if password and password!="":
                instance.set_password(password)
        if commit:
            instance.save()
            self.save_m2m()
        return instance

class CustomLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        super(CustomLoginForm, self).__init__(*args, **kwargs)
        if 'login' in self.fields:self.fields['login'].widget = forms.TextInput(attrs={'type': 'text', 'class': 'form-control form-control-lg','autofocus':'true'})
        if 'password' in self.fields:self.fields['password'].widget = forms.PasswordInput(attrs={'class': 'form-control form-control-lg'})


class CustomSignupForm(SignupForm):
    first_name = forms.CharField(max_length=30, label='First Name')
    last_name = forms.CharField(max_length=30, label='Last Name')
    # country = forms.ChoiceField(label='Country',choices=settings.COUNTRIES_CHOICES)
    def __init__(self, *args, **kwargs):
        super(CustomSignupForm, self).__init__(*args, **kwargs)
        if 'first_name' in self.fields:self.fields['first_name'].widget = forms.TextInput(attrs={'type': 'text', 'class': 'form-control form-control-lg'})
        if 'last_name' in self.fields:self.fields['last_name'].widget = forms.TextInput(attrs={'type': 'text', 'class': 'form-control form-control-lg'})
        # if 'country' in self.fields:self.fields['country'].widget = forms.Select(attrs={'class': 'form-control form-control-lg'},choices=settings.COUNTRIES_CHOICES)
        if 'username' in self.fields:self.fields['username'].widget = forms.TextInput(attrs={'type': 'text', 'class': 'form-control form-control-lg'})
        if 'email' in self.fields:self.fields['email'].widget = forms.TextInput(attrs={'type': 'email', 'class': 'form-control form-control-lg'})
        if 'password1' in self.fields:self.fields['password1'].widget = forms.PasswordInput(attrs={'class': 'form-control form-control-lg'})
        if 'password2' in self.fields:self.fields['password2'].widget = forms.PasswordInput(attrs={'class': 'form-control form-control-lg'})

    
    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        # user.country = self.cleaned_data['country']
        user.save()
        return user


class CustomLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        super(CustomLoginForm, self).__init__(*args, **kwargs)
        if 'login' in self.fields:self.fields['login'].widget = forms.TextInput(attrs={'type': 'text', 'class': 'form-control form-control-lg','autofocus':'true'})
        if 'password' in self.fields:self.fields['password'].widget = forms.PasswordInput(attrs={'class': 'form-control form-control-lg'})


class CustomSignupForm(SignupForm):
    first_name = forms.CharField(max_length=30, label='First Name')
    last_name = forms.CharField(max_length=30, label='Last Name')
    def __init__(self, *args, **kwargs):
        super(CustomSignupForm, self).__init__(*args, **kwargs)
        if 'first_name' in self.fields:self.fields['first_name'].widget = forms.TextInput(attrs={'type': 'text', 'class': 'form-control form-control-lg'})
        if 'last_name' in self.fields:self.fields['last_name'].widget = forms.TextInput(attrs={'type': 'text', 'class': 'form-control form-control-lg'})
        # if 'country' in self.fields:self.fields['country'].widget = forms.Select(attrs={'class': 'form-control form-control-lg'},choices=settings.COUNTRIES_CHOICES)
        if 'username' in self.fields:self.fields['username'].widget = forms.TextInput(attrs={'type': 'text', 'class': 'form-control form-control-lg'})
        if 'email' in self.fields:self.fields['email'].widget = forms.TextInput(attrs={'type': 'email', 'class': 'form-control form-control-lg'})
        if 'password1' in self.fields:self.fields['password1'].widget = forms.PasswordInput(attrs={'class': 'form-control form-control-lg'})
        if 'password2' in self.fields:self.fields['password2'].widget = forms.PasswordInput(attrs={'class': 'form-control form-control-lg'})

    
    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        # user.country = self.cleaned_data['country']
        user.save()
        return user


class CustomResetPasswordForm(ResetPasswordForm):
    def __init__(self, *args, **kwargs):
        super(CustomResetPasswordForm, self).__init__(*args, **kwargs)
        if 'email' in self.fields:self.fields['email'].widget = forms.TextInput(attrs={'type': 'email', 'class': 'form-control form-control-lg'})


class CustomSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super(CustomSetPasswordForm, self).__init__(*args, **kwargs)
        if 'password1' in self.fields:self.fields['password1'].widget = forms.PasswordInput(attrs={'class': 'form-control form-control-lg'})
        if 'password2' in self.fields:self.fields['password2'].widget = forms.PasswordInput(attrs={'class': 'form-control form-control-lg'})

class CustomResetPasswordKeyForm(ResetPasswordKeyForm):
    def __init__(self, *args, **kwargs):
        super(CustomResetPasswordKeyForm, self).__init__(*args, **kwargs)
        if 'password1' in self.fields:self.fields['password1'].widget = forms.PasswordInput(attrs={'class': 'form-control form-control-lg-'})
        if 'password2' in self.fields:self.fields['password2'].widget = forms.PasswordInput(attrs={'class': 'form-control form-control-lg-'})



class CustomSocialPasswordedSignupForm(SignupForm):

    password1 = SetPasswordField(max_length=6,label=("Password"))
    password2 = PasswordField(max_length=6, label=("Password (again)"))
    def clean_password2(self):
        if ("password1" in self.cleaned_data and "password2" in self.cleaned_data):
            if (self.cleaned_data["password1"] != self.cleaned_data["password2"]):
                raise forms.ValidationError(("You must type the same password each time."))
        return self.cleaned_data["password2"]

    def signup(self, request, user):
        user.set_password(self.user, self.cleaned_data["password1"])
        user.save()


class UserSignatureForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UserSignatureForm, self).__init__(*args, **kwargs)
        if 'signature' in self.fields:self.fields['signature'].help_text="If you want to remove the signature, just click clear and then save"
        # Arrange columns as in crispy
        self.helper = FormHelper()
    class Meta:
        model=User
        fields=['signature']


class EmployeeTerminationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EmployeeTerminationForm, self).__init__(*args, **kwargs)
        if 'termination_attachment' in self.fields:self.fields['termination_attachment'].required=True
        if 'date_terminated' in self.fields:self.fields['date_terminated'].required=True
        self.helper = FormHelper()
        self.helper.form_tag = False
    class Meta:
        model=User
        fields=['date_terminated','termination_attachment']
        widgets={'date_terminated':forms.DateInput(attrs={'type':'date'})}
