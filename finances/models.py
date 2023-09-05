from django.db import models
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey,ContentType
from django.conf import settings
from core.models import BaseModel
from django.shortcuts import reverse
import decimal
from datetime import timedelta

# Create your models here.

class ChartOfAccount(BaseModel):
    title=models.CharField(max_length=255,null=False,blank=True)
    code=models.CharField(max_length=255,null=False,blank=True)
    account_type=models.CharField(max_length=255,null=False,blank=True,choices=(('Fixed assets',"Fixed assets"),("Current assets","Current assets"),('Current liabilities',"Current liabilities"),("Long term liabilities","Long term liabilities"),('Revenue',"Revenue"),('Operating expenses',"Operating expenses"),("Capital expenses","Capital expenses"),('Owners equity',"Owners equity"),("Retained earnings","Retained earnings"),("Bank","Bank"),('Dividends',"Dividends"),("Accounts payable","Accounts payable"),("Accounts receivable","Accounts receivable"),("Cost of goods sold","Cost of goods sold"),("Purchases","Purchases")))
    description=models.TextField(null=True,blank=True)
    status=models.PositiveIntegerField(null=False,blank=True,default=1,choices=((1,"Active"),(2,"Inactive")))
    parent=models.ForeignKey('ChartOfAccount',null=True,blank=True,on_delete=models.SET_NULL,related_name='children')
    appear_on_trial_balance=models.BooleanField(default=True,blank=True)
    is_opening_stock=models.BooleanField(default=False,blank=True)
    is_closing_stock=models.BooleanField(default=False,blank=True)
    is_active= models.BooleanField(default=True,editable=False)
    def __str__(self):
        return "%s | %s (%s)"%(self.account_type,self.title,self.code)
    
    @property
    def get_children(self):
        children = list()
        children.append(self)
        for child in self.children.all():
            children.extend(child.get_children)
        return children

    @property
    def name(self):
        return self.title

class Transaction (BaseModel):
    transaction_code=models.CharField(max_length=255,null=False,blank=True)
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



class Invoice(BaseModel):
    INVOICE = 'invoice'
    CREDIT_NOTE = 'credit_note'
    QUOTE='quote'

    CHOICES_TYPE = (
        (INVOICE, 'Invoice'),
        (CREDIT_NOTE, 'Credit note'),
        (QUOTE, 'Quote')
    )

    invoice_number = models.CharField(max_length=255,null=True,blank=True)
    date=models.DateField(null=True,blank=True)
    sender_reference = models.CharField(max_length=255, blank=True, null=True)
    invoice_type = models.CharField(max_length=20, choices=CHOICES_TYPE, default=INVOICE)
    due_days = models.IntegerField(default=14)
    is_credit_for = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)
    is_credited = models.BooleanField(default=False)
    is_sent = models.BooleanField(default=False)
    is_paid = models.BooleanField(default=False)
    bank_account = models.CharField(max_length=266, blank=True, null=True)
    gross_amount = models.FloatField(default=0,null=True,blank=True)
    vat_amount = models.FloatField(null=True,blank=True,default=0)
    net_amount = models.FloatField(blank=True,null=True,default=0)
    discount_amount = models.FloatField(blank=True,default=0,null=True)
    description=models.TextField(null=True,blank=True)
    client = models.ForeignKey('core.Client', related_name='invoices', on_delete=models.CASCADE)
    is_active= models.BooleanField(default=True,editable=False)

    class Meta:
        ordering = ('-created_at',)
    
    def get_due_date(self):
        return self.created_at + timedelta(days=self.due_days)
    
    def get_due_date_formatted(self):
        return self.get_due_date().strftime("%d.%m.%Y")

    
    def __str__(self):
        return str(self.invoice_number)

    def get_url(self):
        return reverse("invoice",kwargs={'pk':self.pk})
    
    # def save_(self, *args, **kwargs):
    #     try:
    #         disc=0
    #         net=0
    #         gross=0
    #         for i in self.items.all():
    #             disc+=i.discount
    #             net=(i.quantity*i.unit_price)-i.discount
    #             gross=i.quantity*i.unit_price
    #         if not self.discount_amount:
    #             self.discount_amount=disc
    #         self.net_amount=net
    #         self.gross_amount=gross
    #     except:
    #         print("Exception occured")
        # self.contact_person = Employee.objects.filter(sections__in=[self.section],client=self.client).first()

class Item(BaseModel):
    invoice = models.ForeignKey('Invoice', related_name='items', on_delete=models.CASCADE)
    quantity = models.FloatField(default=1)
    unit_price = models.FloatField(default=0,blank=True,null=True)
    net_amount = models.FloatField(default=0,blank=True,null=True)
    vat_rate = models.FloatField(default=0)
    discount = models.FloatField(default=0)
    description=models.TextField(null=True,blank=True)

    def save(self, *args, **kwargs):
        self.net_amount=(self.quantity*self.unit_price)-self.discount

    def get_gross_amount(self):
        vat_rate = self.vat_rate/100
        return ((self.quantity*self.unit_price)-self.discount) + (((self.quantity*self.unit_price)-self.discount) * vat_rate)
