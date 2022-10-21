from django.db.models.signals import post_save,pre_save
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver

from users.models import User
from core.utils import save_log,send_email
from core.models import TermMeta,Log,Client
from django.contrib.admin.models import LogEntry
from django.contrib.sessions.models import Session
from django.db import migrations

# Save logs when a user creates any model object
@receiver(post_save)
def track_model_create_logs(sender,instance,*args, **kwargs):
    try:
        if sender in [Log,LogEntry,Session,migrations]:
            return
        if 'created' in kwargs and kwargs['created']:
            if sender==Asset:
                AssetAllocation.objects.create(asset=instance,user=instance.user,department=instance.department,status=instance.status,date=instance.created_at)
            elif sender==Task and instance.owner_model.model=='activity':
                #Try sending a mail to the parent activity supervisor"
                send_email(subject="New Task Created!!!",
                body='''%s has created a new task %s under %s.'''%(instance.created_by.email,instance.title,instance.owner),mail_from=None, mail_to=[instance.owner.supervisor.email],cc=[],bcc=[],)
            elif sender==Client:
                send_email(subject="New Account created!!!",
                body='''Dear %s, your account has been created successfully with email %s, for password please contact the system administrator.'''%(instance.name,instance.email),mail_from=None, mail_to=[instance.email],cc=[],bcc=[],)


            message="Created {} for {} through {}".format(sender._meta.model.__name__,instance,"")
            save_log(message=message)
    except:
        pass

# Track model update logs
@receiver(pre_save)
def track_model_update_logs(sender,instance,*args, **kwargs):
    try:
        if sender in [Log,LogEntry,Session,migrations]:
            return
        if 'created' in kwargs and kwargs['created']:
            pass
        elif instance and instance.pk:
            action_flag=2
            old=sender.objects.get(pk=instance.pk)
            new=instance
            updated_fields=[]
            if sender==User and new.password!=old.password:
                # Send email to owner that the password was reset
                send_email(subject="Password reset!!!",
                body='''There was password reset for the account with %s. if you didn`t request, 
                please report this to the administrator.'''%(old.email),mail_from=None, mail_to=[old.email],cc=[],bcc=[],)
            for field in sender._meta.get_fields():
                field_name=field.name
                try:
                    if getattr(old,field_name)!=getattr(new, field_name) and field_name!="password":
                        updated_fields.append({field_name:getattr(old,field_name),'to':getattr(new, field_name)})
                    if field_name=="is_active" and getattr(new, field_name)==False:
                        action_flag=3
                except Exception as ex:
                    pass
            message="Updated {} for {} changed {}".format(sender._meta.model.__name__,instance,updated_fields)
            if message and updated_fields:
                save_log(message=message,instance=old,action_flag=action_flag)
    except:
        pass
 
@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    message=('user {} logged in through page {}'.format(user.username, request.META.get('HTTP_REFERER')))
    save_log(message=message,action_flag=4)
 
 
@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request, **kwargs):
    message=('user {} log in failed through page {}'.format(credentials.get('username'), request.META.get('HTTP_REFERER')))
    save_log(message=message,action_flag=4)
 
 
@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    message=('user {} logged out through page {}'.format(user.username, request.META.get('HTTP_REFERER')))
    save_log(message=message,action_flag=4)


