from django.db import models
import datetime
from django.utils import timezone
from django.conf import settings
from django.contrib.contenttypes.fields import ContentType,GenericForeignKey
from django.db.models import Max

# Create your models here.

class Task(models.Model):
    owner_model = models.ForeignKey(ContentType, blank=True, null=False,
                                    related_name='task',
                                    on_delete=models.CASCADE,
                                    # limit_choices_to=models.Q(app_label='users', model='user') | models.Q(app_label='projects', model='activity')
                                    )
    owner_id = models.PositiveIntegerField(null=False, blank=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    title = models.CharField(max_length=255,blank=True,null=True)
    completed = models.BooleanField(default=False,blank=True,null=True)
    startdate = models.DateField(max_length=255, blank=True, null=False,default=datetime.date.today)
    enddate = models.DateField(max_length=255, blank=True, null=True)
    time_completed = models.DateTimeField(blank=True, null=True)
    order = models.DecimalField(max_digits=30,decimal_places=15, blank=True, null=True)
    assigned_to = models.ManyToManyField('users.User', blank=True)
    is_active= models.BooleanField(default=True,editable=False,db_index=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    def __str__(self):
        return str(self.title)
    
    def save(self, *args, **kwargs):
        filtered_objects = Task.objects.filter(is_active=True)
        if not self.order and filtered_objects.count() == 0:
            self.order = 2 ** 16 - 1 
        elif not self.order:
            self.order = filtered_objects.aggregate(Max('order'))[
                'order__max'] + 2 ** 16 - 1
        return super().save(*args, **kwargs)


class TaskUpdate(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    task = models.ForeignKey('Task', on_delete=models.CASCADE)
    updates=models.TextField(null=True,blank=True)
    challenges=models.TextField(null=True,blank=True)
    remarks=models.TextField(null=True,blank=True)
    is_active= models.BooleanField(default=True,editable=False,db_index=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    def __str__(self):
        return str(self.task)+" "+str(self.user)