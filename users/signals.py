from django.db.models.signals import post_save,pre_save
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from .models import User
from django.contrib.contenttypes.models import ContentType
from core.utils import send_email

@receiver(pre_save, sender=User)
def user_change_hook(sender, instance, **kwargs):
    user = instance
    if user:
        new_password = user.password
        try:
            old_password = User.objects.get(pk=user.pk).password
        except User.DoesNotExist:
            old_password = None
        if new_password != old_password:
            pass
            # send_email(subject="Password Change",body="Dear %s, your password has been reset."%(instance.full_name),mail_to=[instance.email])

