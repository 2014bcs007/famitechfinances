from django.db import models
from django.utils import timezone
from django_currentuser.db.models import CurrentUserField
from datetime import datetime
from django.contrib.contenttypes.fields import GenericForeignKey,ContentType
from django.conf import settings
from django.utils.translation import ugettext, ugettext_lazy as _
from django.shortcuts import reverse
from django.contrib.auth.models import AbstractUser
# Create your models here.

class RightsSupport(models.Model):
    class Meta:
        managed=False
        default_permissions=()#Disable default add edit and delete permissions
        permissions = (
            ("administration_module", "Administration Module"),
            ("projects_module", "Projects Module"),
            ("hr_module", "HR Module"),
            ("reports_module", "Reports Module"),
            ("manage_archiving", "Manage Archiving"),
        )


class BaseModel(models.Model):
    created_by = CurrentUserField(editable=False,related_name="%(app_label)s_%(class)s_created_by",
        related_query_name="%(app_label)s_%(class)ss")
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_by = CurrentUserField(on_update=True,related_name="%(app_label)s_%(class)s_updated_by",
        related_query_name="%(app_label)s_%(class)ss",verbose_name='last updated by')
    updated_at = models.DateTimeField(auto_now=True,null=True,blank=True, editable=False,verbose_name='last updated on')

    class Meta:
        abstract=True

# Log table
class Log(models.Model):
    user = CurrentUserField(editable=True,null=True,blank=True,related_name="user_logs")
    content_type = models.ForeignKey(ContentType, blank=True, null=True,on_delete=models.SET_NULL)
    object_id=models.TextField(blank=True,null=True)
    object_repr=models.TextField(blank=True,null=True)
    action_flag=models.PositiveSmallIntegerField(default=4,choices=([1,"Addition"],[2,"Change"],[3,"Deletion"],[4,"Other Action"]))
    change_message=models.TextField(blank=True,null=True)
    action_time = models.DateTimeField(default=timezone.now, editable=False)
    is_active = models.BooleanField(default=True,editable=False,db_index=True)
    model = GenericForeignKey('content_type', 'object_id')
    def __str__(self):
        return '%s %s'%(self.user,self.change_message)

    class Meta:
        verbose_name = _('log')
        verbose_name_plural = _('logs')
        ordering = ('-action_time',)

class Term(BaseModel):
    name=models.CharField(max_length=255,null=False,blank=True)
    description=models.CharField(max_length=255,null=True,blank=True)
    parent=models.ForeignKey('self',null=True,blank=True, on_delete=models.SET_NULL)
    type=models.CharField(max_length=255,db_index=True,null=False,blank=True,choices=settings.TERMS_CHOICES)
    is_formula=models.BooleanField(default=False,blank=True)
    formula=models.TextField(blank=True,null=True)
    is_active= models.BooleanField(default=True,editable=False,db_index=True)

    def __str__(self):
        return str(self.name)
    
    class Meta:
        unique_together=['name','type','is_active']
        ordering = ('name',)
    
    @property
    def totals(self):
        if self.type=="asset-categories":
            contentType=ContentType.objects.get(model="asset")
            return contentType.model_class().objects.filter(category=self,is_active=True).count()
        elif self.type=="license-categories":
            contentType=ContentType.objects.get(model="license")
            return contentType.model_class().objects.filter(category=self,is_active=True).count()
        return 0

    def get_meta(self):
        m = TermMeta.objects.filter(term=self,is_active=True)
        data = {}
        if m is not None and len(m)>0:
            for f in m:
                data[f.meta_key] = f.meta_value
        return data

class TermMeta(BaseModel):
    term=models.ForeignKey('term',null=False,blank=True,on_delete=models.CASCADE)
    meta_key=models.CharField(max_length=255,null=False,blank=True)
    meta_value=models.TextField(blank=True,null=True)
    is_active = models.BooleanField(default=True,editable=False,db_index=True)
    def __str__(self):
        return '%s %s'%(self.term,self.meta_key)


class Config(BaseModel):
    name=models.CharField(max_length=255,null=False,blank=True,db_index=True)
    value=models.TextField(null=True,blank=True)
    is_active= models.BooleanField(default=True,editable=False,db_index=True)

    def __str__(self):
        return str(self.value)

class Template(BaseModel):
    code=models.CharField(max_length=100,null=False,blank=True, editable=True)
    title=models.CharField(max_length=255,null=False,blank=True)
    subject=models.CharField(max_length=255,null=False,blank=True)
    message=models.TextField(null=False,blank=True)
    is_active= models.BooleanField(default=True,editable=False,db_index=True)

    def __str__(self):
        return str(self.code)



class Client(models.Model):
    locations=(("right","Right"),("left","Left"))
    name=models.CharField(max_length=255,null=False,blank=False)
    email=models.CharField(max_length=255,null=False,blank=False,unique=True)
    address1 = models.CharField(max_length=255, blank=True, null=True)
    address2 = models.CharField(max_length=255, blank=True, null=True)
    zipcode = models.CharField(max_length=255, blank=True, null=True)
    client_contact_reference = models.CharField(max_length=255, blank=True, null=True)
    phone=models.CharField(max_length=255,null=True,blank=True)
    box_number=models.CharField(max_length=255,null=True,blank=True)
    # address=models.TextField(blank=True,null=True)
    logo=models.ImageField(null=True,blank=True,upload_to="clients/logos")
    currency_symbol=models.CharField(max_length=255,null=True,blank=True)
    currency_location=models.CharField(max_length=10,choices=locations,default=locations[0])
    is_active=models.BooleanField(default=True,editable=False)

    def username(self):
        return self.email
    
    # def is_employee(self):
    #     return False
    
    @property
    def thumbnail(self):
        if self.logo:
            return "<div title='%s' class='member member--image'><img src='%s'/></div>"%(self.name,self.logo.url)
        else:
            colors = ["red", "yellow", "blue"]
            val=ord(self.email[:1])
            return "<div title='%s' class='member member--%s'>%s</div>"%(self.email,colors[val%len(colors)],self.email[:1])
    

    def __str__(self):
        return str(self.name)

    def get_url(self):
        return reverse("client",kwargs={'pk':self.pk})
    
    def has_perms(self, perm, obj=None):
        for p in perm:
            if not p in settings.CLIENT_PERMISSIONS:
                return False
        return True

    def has_perm(self, perm, obj=None):
        return perm in settings.CLIENT_PERMISSIONS

    def has_module_perms(self, app_label):
        return self.is_superuser