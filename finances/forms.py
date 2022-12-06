from django import forms
from django.urls import reverse_lazy
from .models import *
from core.models import Term
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
import datetime
from core.models import *
from core.fields import RelatedFieldWidgetCanAdd

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Div


class ChartOfAccountForm(forms.ModelForm):
    row1_col1=['title','code','account_type','status']
    row1_col2=['parent','description']
    def __init__(self, *args, **kwargs):
        super(ChartOfAccountForm, self).__init__(*args, **kwargs)
        if 'title' in self.fields:self.fields['title'].required=True
        if 'code' in self.fields:self.fields['code'].required=True
        if 'account_type' in self.fields:self.fields['account_type'].required=True
        if 'branches' in self.fields:
            self.fields['branches'].queryset=Term.objects.filter(is_active=True,type="branches")

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(
                Div(*self.row1_col1, css_class='col-md-6'),
                Div(*self.row1_col2, css_class='col-md-6'), css_class='row'
            ),
        )
    class Meta:
        model=ChartOfAccount
        fields=['title','code','account_type','description','parent','status']
        widgets={
            'startdate':forms.DateInput(attrs={'type':'date'}),
            'description':forms.Textarea(attrs={'rows':2}),
        }



class TransactionForm(forms.ModelForm):
    col1=['date','transaction_code','amount','transaction_mode','cheque_number','client']
    col2=['transaction_type','payee','gl_account','comment']

    def __init__(self, *args, **kwargs):
        super(TransactionForm, self).__init__(*args, **kwargs)
        if 'date'in self.fields:self.fields['date'].required = True
        if 'amount'in self.fields:self.fields['amount'].required = True

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(
                Div(*self.col1, css_class='col-md-6'),
                Div(*self.col2, css_class='col-md-6'), css_class='row'
            ),
        )
    class Meta:
        model=Transaction
        # fields='__all__'
        fields=['date','transaction_mode','client','transaction_code','transaction_type','cheque_number','amount','gl_account','payee','comment']
        widgets={
            'transaction_type':forms.HiddenInput(),
            'transaction_code':forms.HiddenInput(),
            'date':forms.DateInput(attrs={'class':'form-control','type':'date'}),
            'amount':forms.NumberInput(attrs={'class':'form-control','type':'number','min':0}),
            'comment':forms.Textarea(attrs={'class':'form-control','rows':3}),
            'client':RelatedFieldWidgetCanAdd(Client,attrs={'class':'form-control'}),
            'gl_account':RelatedFieldWidgetCanAdd(ChartOfAccount,attrs={'class':'form-control'}),
        }

    # Validate amount submitted
    def clean_amount(self):
        amount = self.cleaned_data.get('amount',None)
        if amount<=0:
            raise forms.ValidationError("Cannot make a Zero amount transaction")
        return amount


class InvoiceForm(forms.ModelForm):
    allFields=['date','invoice_number','invoice_type','due_days','is_credited','is_credit_for','discount_amount','description','client']

    def __init__(self, *args, **kwargs):
        super(InvoiceForm, self).__init__(*args, **kwargs)
        if 'date'in self.fields:self.fields['date'].required = True
        if 'amount'in self.fields:self.fields['amount'].required = True

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(
                *self.allFields, css_class='mb-3 form-inline'
            ),
        )
    class Meta:
        model=Invoice
        fields='__all__'
        widgets={
            'invoice_type':forms.HiddenInput(),
            'invoice_number':forms.HiddenInput(),
            'date':forms.DateInput(attrs={'class':'form-control','type':'date'}),
            'discount_amount':forms.NumberInput(attrs={'class':'form-control','type':'number','min':0}),
            'description':forms.TextInput(attrs={'class':'form-control','rows':1}),
            'client':RelatedFieldWidgetCanAdd(Client,attrs={'class':'form-control'}),
        }

    # Validate discount amount submitted
    def clean_discount_amount(self):
        amount = self.cleaned_data.get('discount_amount',None)
        if amount<0:
            raise forms.ValidationError("Cannot make a qoute with lessa than zero discount amount")
        return amount
    
class ItemForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ItemForm, self).__init__(*args, **kwargs)
        if 'quantity' in self.fields:self.fields['quantity'].required=True
    class Meta:
        model=Item
        fields=['quantity','unit_price','description']
        # exclude=['purchase_order','budgetlineitem','quotation','parent']
        widgets={
                'quantity':forms.NumberInput(attrs={'class':'form-control','oninput':'validateFields(this)','required':True,'min':'0'}),
                'unit_price':forms.NumberInput(attrs={'class':'form-control','oninput':'validateFields(this)','required':True,'min':'0'}),
                'description':forms.TextInput(attrs={'class':'form-control'})
            }