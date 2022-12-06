from django import forms
from .models import *
from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Div

class TermForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(TermForm, self).__init__(*args, **kwargs)
        self.fields['name'].required = True
    class Meta:
        model=Term
        fields=['name','type','description']
        widgets={
            'type':forms.HiddenInput(),
            'name':forms.TextInput(attrs={'class':'form-control'}),
            'description':forms.Textarea(attrs={'class':'form-control','rows':3}),
        }



class TemplateForm(forms.ModelForm):
    class Meta:
        model=Template
        fields=['code','title','subject','message']
        widgets={
            'code':forms.HiddenInput(),
            'title':forms.TextInput(attrs={'class':'form-control'}),
            'subject':forms.TextInput(attrs={'class':'form-control'}),
            'message':forms.Textarea(attrs={'class':'form-control summernote','rows':10}),
        }

class ClientForm(forms.ModelForm):

    create_client_folder=forms.BooleanField(required=False)
    col1_fields=['name','email','phone','box_number']
    col2_fields=['currency_location','currency_symbol','address1','address2']
    row2_fields=['logo']

    def __init__(self, *args, **kwargs):
        super(ClientForm, self).__init__(*args, **kwargs)
        # Arrange columns as in crispy
        self.helper = FormHelper()
        self.helper.form_tag = False

        self.helper.layout = Layout(
            Div(
                Div(*self.col1_fields, css_class='col-sm-6'),
                Div(*self.col2_fields, css_class='col-sm-6'), css_class='row'
            ),
            Div(
                Div(Div(*self.row2_fields), css_class='col-md-12'), css_class='row'
            )
        )
    class Meta:
        model=Client
        fields='__all__'
        widgets={
            'address1':forms.Textarea(attrs={'rows':3}),
            'address2':forms.Textarea(attrs={'rows':3}),
            'password':forms.PasswordInput(),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        if 'password' in self.cleaned_data:
            password = self.cleaned_data.pop('password')
            if password and password!="":
                from django.contrib.auth.hashers import make_password
                instance.password=make_password(password)
        instance.save()