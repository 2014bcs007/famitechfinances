from django.conf import settings

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from users.models import User
from allauth.exceptions import ImmediateHttpResponse
from django.shortcuts import HttpResponse


class CustomAccountAdapter(DefaultAccountAdapter):

    def is_open_for_signup(self, request):
        """
        Whether to allow sign ups.
        """
        allow_signups = super(
            CustomAccountAdapter, self).is_open_for_signup(request)
        # Override with setting, otherwise default to super.
        return getattr(settings, 'ACCOUNT_ALLOW_SIGNUPS', allow_signups)


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def is_open_for_signup(self, request, sociallogin):
        return False

    def pre_social_login(self, request, sociallogin): 
        if sociallogin.is_existing:
            return
        if 'email' not in sociallogin.account.extra_data:
            # logger.info("'Email' field not in extra_data")
            raise ImmediateHttpResponse(HttpResponse('Email missing from social login - cannot verify user.'))
        try:
            email = sociallogin.account.extra_data['email'].lower()
            user = User.objects.get(email=email)

        except User.DoesNotExist:
            # logger.info(f"User associated with {email} does not exist - preventing login.")
            raise ImmediateHttpResponse(HttpResponse('Must have pre-existing account for social login.'))

        sociallogin.connect(request, user)