from django.db import models
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey,ContentType
from django.conf import settings
from core.models import BaseModel
from django.shortcuts import reverse

# Create your models here.

class ChartOfAccount(BaseModel):
    title=models.CharField(max_length=255,null=False,blank=True)
    code=models.CharField(max_length=255,null=False,blank=True)
    account_type=models.CharField(max_length=255,null=False,blank=True,choices=(('asset',"Assets"),('liability',"Liabilities"),('income',"Income"),('expense',"Expenses"),('capital',"Capital")))
    description=models.TextField(null=True,blank=True)
    status=models.PositiveIntegerField(null=False,blank=True,default=1,choices=((1,"Active"),(2,"Inactive")))
    parent=models.ForeignKey('ChartOfAccount',null=True,blank=True,on_delete=models.SET_NULL)
    is_active= models.BooleanField(default=True,editable=False)
    def __str__(self):
        return "%s | %s (%s)"%(self.account_type,self.title,self.code)

    @property
    def name(self):
        return self.title

class Transaction (BaseModel):
    transaction_code=models.CharField(max_length=255,null=False,blank=True)
    # target_model = models.ForeignKey(ContentType, blank=True, null=True, on_delete=models.CASCADE)  #Say User/Member,Account, Loan, Group etc
    # target_id = models.PositiveIntegerField(null=True, blank=True)   #Actual parent ID
    # target = GenericForeignKey('target_model', 'target_id')
    date=models.DateField(null=False,blank=True)
    transaction_type=models.CharField(max_length=255,null=False,blank=True)
    transaction_mode=models.CharField(max_length=45,null=False,blank=True,default="Cash",choices=(("Cash","Cash"),("Cheque","Cheque")))
    cheque_number=models.CharField(max_length=255,null=True,blank=True)
    amount=models.FloatField(null=False,blank=True,default=0)
    payee=models.CharField(max_length=255,null=True,blank=True)
    gl_account=models.ForeignKey("ChartOfAccount",null=True,blank=True,on_delete=models.SET_NULL)
    client=models.ForeignKey("core.Client",null=True,blank=True,on_delete=models.SET_NULL)
    comment=models.TextField(null=True,blank=True)
    is_active= models.BooleanField(default=True,editable=False)
    def __str__(self):
        return str(self.transaction_code)

    def get_url(self):
        return reverse("transaction",kwargs={'pk':self.pk})
