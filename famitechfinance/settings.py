"""
Django settings for famitechfinance project.

Generated by 'django-admin startproject' using Django 3.2.7.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""
from dotenv import load_dotenv
import os

import django_heroku
from pathlib import Path
from django.contrib import messages

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-0pms543s7u8y*@ehqyjeya93sb03f^$w-wy+(7arq3+$nx_s$g'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

DEFAULT_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'whitenoise.runserver_nostatic',
    
]

LOCAL_APPS=[
    'core',
    'users',
    'finances',
    'todolist',]

THIRD_PARTY_APPS=[
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'crispy_forms',
    'django_filters',
    'django_htmx',
    'rest_framework',
]

INSTALLED_APPS=DEFAULT_APPS+LOCAL_APPS+THIRD_PARTY_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    "django_htmx.middleware.HtmxMiddleware",                        #HTMX middleware for handling HTMX requests
    'django_currentuser.middleware.ThreadLocalUserMiddleware',      #From django_currentuser library
]

ROOT_URLCONF = 'famitechfinance.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR,'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                "core.context_processors.core_configurations",
            ],
        },
    },
]

WSGI_APPLICATION = 'famitechfinance.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases
load_dotenv()
DATABASES = {
    # 'default': {
    #     'ENGINE': 'django.db.backends.sqlite3',
    #     'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    # }
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD':os.environ.get('DB_USER_PASSWORD',''),
        'HOST':os.environ.get('DB_HOST'),
        'PORT':'3306'
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True
AUTH_USER_MODEL = 'users.User'


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

STATIC_URL='/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR,'static')]
STATIC_ROOT = os.path.join(BASE_DIR,'/static')

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = 'media/'

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

django_heroku.settings(locals())

MESSAGE_TAGS={
    messages.ERROR:'danger'
}


# Gender options
GENDER_CHOICES=[('Male','Male'),('Female','Female')]

TERMS_CHOICES=(("banks","Bank"),("departments","Department"),("jobs","Jobs"),("allowances","Allowance"),
                ("leave-categories","Leave Categories"),("holidays","Holidays"),
                ("deductions","Deductions"),("taxes","Tax"),("sections","Sections"),
                )

AVAILABLE_TERMSLIST=[
    { "key": "departments", "title": "Departments" },
    { "key": "banks", "title": "Banks" },
    { "key": "jobs", "title": "Jobs" },
    { "key": "onboarding-areas", "title": "Onboarding Areas" },
    { "key": "sections", "title": "Sections" },
    { "key": "leave-categories", "title": "Leave Categories", "meta_keys": [{ "meta_key": "days", "type": 'number' }, { "meta_key": "enable_holidays", "type": 'checkbox','no_class':True }] },
    { "key": "allowances", "title": "Allowances", "meta_keys": [{ "meta_key": "is_taxable", "type": 'checkbox','no_class':True }] },
    { "key": "deductions", "title": "Deductions", "meta_keys": [{ "meta_key": "is_taxable", "type": 'checkbox','no_class':True }] },
    { "key": "taxes", "title": "Taxes", "meta_keys": [{ "meta_key": "is_deductable", "type": 'checkbox','no_class':True },{ "meta_key": "is_formula", "type": 'checkbox','no_class':True }, { "meta_key": "formula", "type": 'formula' }] },
    { "key": "replies", "title": "Replies" },
    { "key": "asset-categories", "title": "Asset Categories" ,"meta_keys":[{"meta_key":"color","type":"color"},{"meta_key":"depreciation_rate","type":"number"}]},
    { "key": "asset-statuses", "title": "Asset Status" ,"meta_keys":[{"meta_key":"color","type":"color"}]},
    { "key": "license-categories", "title": "License Categories" ,"meta_keys":[{"meta_key":"color","type":"text"}]},
    {"key":"manufacturers","title":"Manufacturers","meta_keys": [{"meta_key":"address","type":"text"},{ "meta_key": "email", "type": 'email' },{"meta_key":"phone","type":"text"},{"meta_key":"website","type":"url"}] },
    {"key":"suppliers","title":"Suppliers","meta_keys": [{"meta_key":"address","type":"text"},{ "meta_key": "email", "type": 'email' },{"meta_key":"phone","type":"text"},{"meta_key":"website","type":"url"}] },
    {"key":"procurement-item-categories","title":"Procurement Item Categories" },
]



#Email Stuff

EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL')
EMAIL_PORT = os.environ.get('EMAIL_PORT')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')

NOTIFICATION_TEMPLATES=[]

# check whether something is coming # print(os.environ.get('EMAIL_HOST'))


ACCOUNT_FORMS = {
    'login': 'users.forms.CustomLoginForm',
    'signup': 'users.forms.CustomSignupForm',
    'add_email': 'allauth.account.forms.AddEmailForm',
    'change_password': 'allauth.account.forms.ChangePasswordForm',
    'set_password': 'users.forms.CustomSetPasswordForm',
    'reset_password': 'users.forms.CustomResetPasswordForm',
    'reset_password_from_key': 'users.forms.CustomResetPasswordKeyForm',
    'disconnect': 'allauth.socialaccount.forms.DisconnectForm',
}
SOCIALACCOUNT_FORMS = {
    # 'signup': 'users.forms.CustomSocialPasswordedSignupForm'
}

ACCOUNT_ADAPTER = 'users.adapters.CustomAccountAdapter'
SOCIALACCOUNT_ADAPTER = "users.adapters.SocialAccountAdapter"


ACCOUNT_LOGOUT_ON_GET=True  #Logout the user whenever click on a logout url (Via get)
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True
# ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_ALLOW_SIGNUPS = False
ACCOUNT_AUTHENTICATION_METHOD = 'username_email'
ACCOUNT_LOGOUT_REDIRECT_URL =LOGIN_URL ="/auth/login"
LOGIN_REDIRECT_URL = "/"
ACCOUNT_LOGIN_ATTEMPTS_LIMIT =5
ACCOUNT_LOGIN_ATTEMPTS_TIMEOUT=300
ACCOUNT_SESSION_REMEMBER =None

# CRISPY SETTINGS
CRISPY_TEMPLATE_PACK='bootstrap4'
