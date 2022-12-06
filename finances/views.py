from django.shortcuts import render

# Create your views here.
from django.shortcuts import render,HttpResponse,reverse,redirect
from django.views import View
from .models import *
import json
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from .filters import *
from .forms import*
import datetime
from django.contrib.auth.mixins import LoginRequiredMixin,PermissionRequiredMixin

from django.forms.models import inlineformset_factory

# Create your views here.
class TransactionList(LoginRequiredMixin,View):
    filter_class=TransactionsFilter
    template_name='finances/transactions.html'

    def get(self, request, *args, **kwargs):
        context={}
        if request.htmx:
            self.template_name='finances/partials/transactions-list.html'
            if 'action' in request.GET and request.GET['action']=='get-form':
                self.template_name='finances/partials/transaction-form.html'
                pre_filled_data={
                'transaction_code':str(datetime.datetime.now().strftime('%Y%m%d%H%M%S') ),
                'date':datetime.datetime.today(),
                'transaction_type':request.GET.get('transaction_type',None),
                'content_type':request.GET.get('content_type',None)
                }
                if 'account_type' in request.GET:
                    pre_filled_data['account_type']=request.GET['account_type']
                context={
                    'form':TransactionForm(initial=pre_filled_data),
                    'transaction_type':request.GET.get('transaction_type',None),
                    'content_type':request.GET.get('content_type',None),
                    'account_type':request.GET.get('account_type',None),
                }
                return render(request, self.template_name,context)

        queryset= Transaction.objects.filter(is_active=True)
        if not request.user.is_superuser:
            queryset=queryset.filter(created_by=request.user)
        qs_values=('transaction_code','date','amount','transaction_type','transaction_mode')
        txt=self.filter_class(request.GET,queryset).qs.values('id','transaction_code','date','amount','transaction_type','gl_account__title','transaction_mode','cheque_number','client__name','payee','created_by__username','comment')
        context['transactions']=txt
        return render(request, self.template_name,context)
    def post(self,request,*args,**kwargs):
        context={}
        form = TransactionForm(request.POST)
        if form.is_valid():
            ser=form.save()
            return HttpResponse(status=204,headers={'HX-Trigger':'listChanged'})
        else:
            self.template_name='finances/partials/transaction-form.html'
            context['form']=form
            return render(request, self.template_name,context)

class TransactionDetail(LoginRequiredMixin,View):
    
    form_class=TransactionForm
    model_class=Transaction
    template_name='finances/partials/transaction.html'
    
    def get(self, request, pk,*args,**kwargs):
        transaction = get_object_or_404(self.model_class,pk=pk)
        context={'transaction':transaction}
        if 'action' in request.GET and request.GET['action']=='get-form':
            context['form']=self.form_class(instance=transaction)
            self.template_name="finances/partials/transaction-form.html"
        return render(request, self.template_name,context)
    def post(self, request, pk):
        transaction = self.model_class.objects.get(pk=pk)
        form=self.form_class(request.POST,instance=transaction)
        context={'form':form,'transaction':transaction}
        if form.is_valid():
            form.save()
            return HttpResponse(status=204,headers={'HX-Trigger':'listChanged'})
        else:
            self.template_name="finances/partials/transaction-form.html"
            return render(request, self.template_name,context)
    def delete(self,request,pk):
        transaction = get_object_or_404(self.model_class,pk=pk)
        transaction.is_active=False
        transaction.save()
        return HttpResponse(status=204,headers={'HX-Trigger':'listChanged'})


class ChartOfAccountList(LoginRequiredMixin,View):
    template_name='finances/gl-accounts.html'
    form_class=ChartOfAccountForm
    
    def get_queryset(self, *args, **kwargs):
        return ChartOfAccount.objects.filter(is_active=True).order_by('title')

    def get(self, request, *args, **kwargs):
        context={}
        if 'action' in request.GET and request.GET['action']=='get-form':
            self.template_name='finances/partials/gl-account-form.html'
            context['form']=self.form_class()
            return render(request, self.template_name,context)
        accounts=self.get_queryset()
        context['list']=accounts
        if request.htmx:
            self.template_name='finances/partials/gl-accounts-list.html'
        return render(request, self.template_name,context)

    def post(self, request, *args, **kwargs):
        form =self.form_class(request.POST)
        context={'form':form}

        if form.is_valid():
            ser=form.save()
            return HttpResponse(status=204,headers={'HX-Trigger':'listChanged'})
        else:
            self.template_name="finances/partials/gl-account-form.html"
            context['form']=form
            return render(request, self.template_name,context)

class ChartOfAccountDetail(LoginRequiredMixin,View):
    form_class=ChartOfAccountForm
    template_name='finances/partials/gl-accounts.html'
    
    def get(self, request, pk,*args,**kwargs):
        account = get_object_or_404(ChartOfAccount,pk=pk)
        context={'account':account}
        if 'action' in request.GET and request.GET['action']=='get-form':
            context['form']=self.form_class(instance=account)
            self.template_name="finances/partials/gl-account-form.html"
        return render(request, self.template_name,context)
    def post(self, request, pk):
        account = ChartOfAccount.objects.get(pk=pk)
        form=self.form_class(request.POST,instance=account)
        context={'form':form,'account':account}
        if form.is_valid():
            form.save()
            return HttpResponse(status=204,headers={'HX-Trigger':'listChanged'})
        else:
            self.template_name="finances/partials/gl-account-form.html"
            return render(request, self.template_name,context)
    def delete(self,request,pk):
        account = get_object_or_404(ChartOfAccount,pk=pk)
        account.is_active=False
        account.save()
        return HttpResponse(status=204,headers={'HX-Trigger':'listChanged'})


class InvoicesView(LoginRequiredMixin,View):
    filter_class=InvoicesFilter
    model_class=Invoice
    form_class=InvoiceForm
    child_model_class=Item
    child_form_class=ItemForm
    template_name='finances/invoices.html'

    itemFormsets = inlineformset_factory(model_class, child_model_class,extra=1,
            form=ItemForm,
            can_delete=True
        )

    def get(self, request, *args, **kwargs):
        context={}
        if request.htmx:
            self.template_name='finances/partials/invoices-list.html'
            if 'action' in request.GET and request.GET['action']=='get-form':
                self.template_name='finances/partials/invoice-form.html'
                pre_filled_data={
                'invoice_number':str(datetime.datetime.now().strftime('%Y%m%d%H%M%S') ),
                'date':datetime.datetime.today(),
                'invoice_type':request.GET.get('invoice_type',None),
                'content_type':request.GET.get('content_type',None)
                }
                if 'account_type' in request.GET:
                    pre_filled_data['account_type']=request.GET['account_type']
                context={
                    'formsets':self.itemFormsets,
                    'form':self.form_class(initial=pre_filled_data),
                    'invoice_type':request.GET.get('invoice_type',None),
                    'content_type':request.GET.get('content_type',None),
                    'account_type':request.GET.get('account_type',None),
                }
                return render(request, self.template_name,context)

        queryset= self.model_class.objects.filter(is_active=True)
        if not request.user.is_superuser:
            queryset=queryset.filter(created_by=request.user)
        txt=self.filter_class(request.GET,queryset).qs.values('id','invoice_number','date','invoice_type','gross_amount','discount_amount','net_amount','client__name','description')
        context['list']=txt
        return render(request, self.template_name,context)
    def post(self,request,*args,**kwargs):
        form = self.form_class(request.POST)
        context={'form':form}
        if form.is_valid():
            req=form.save(commit=False)

            formsets=self.itemFormsets(request.POST,instance=req)
            context['formsets']=formsets
            if not formsets.is_valid():
                context['formsets']=self.itemFormsets
                self.template_name='finances/partials/invoice-form.html'
                print(formsets.errors)
                return render(request, self.template_name,context)
            req=form.save()

            formsets=self.itemFormsets(request.POST,instance=req)
            context['formsets']=formsets
            if formsets.is_valid():
                formsets.save()
                return HttpResponse(status=204,headers={'HX-Trigger':'listChanged'})
        else:
            print(form.errors)
            context['formsets']=self.itemFormsets
            self.template_name='finances/partials/invoice-form.html'
            context['form']=form
            return render(request, self.template_name,context)

class InvoiceDetailView(LoginRequiredMixin,View):
    
    model_class=Invoice
    form_class=InvoiceForm
    child_model_class=Item
    child_form_class=ItemForm
    template_name='finances/invoices.html'

    itemFormsets = inlineformset_factory(model_class, child_model_class,extra=1,
            form=ItemForm,
            can_delete=True
        )
    
    def get(self, request, pk,*args,**kwargs):
        invoice = get_object_or_404(self.model_class,pk=pk)
        context={'invoice':invoice,'formsets':self.itemFormsets(instance=invoice)}
        if 'action' in request.GET and request.GET['action']=='get-form':
            context['form']=self.form_class(instance=invoice)
            self.template_name="finances/partials/invoice-form.html"
        return render(request, self.template_name,context)
    def post(self, request, pk):
        invoice = self.model_class.objects.get(pk=pk)
        form=self.form_class(request.POST,instance=invoice)
        context={'form':form,'invoice':invoice}
        if form.is_valid():
            invoice=form.save()
            formsets=self.itemFormsets(request.POST,instance=invoice)
            context['formsets']=formsets
            if formsets.is_valid():
                formsets.save()
                return HttpResponse(status=204,headers={'HX-Trigger':'listChanged'})
            else:
                self.template_name='finances/partials/invoice-form.html'
                print(formsets.errors)
                return render(request, self.template_name,context)
        else:
            context['formsets']=self.itemFormsets
            self.template_name="finances/partials/invoice-form.html"
        return render(request, self.template_name,context)
    def delete(self,request,pk):
        invoice = get_object_or_404(self.model_class,pk=pk)
        invoice.is_active=False
        invoice.save()
        return HttpResponse(status=204,headers={'HX-Trigger':'listChanged'})
