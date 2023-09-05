from django.shortcuts import render

# Create your views here.
from django.shortcuts import render,HttpResponse,reverse,redirect
from django.views import View
from .models import *
import json
from django.db.models import Q,Sum
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from .filters import *
from .forms import*
import datetime
from django.contrib.auth.mixins import LoginRequiredMixin,PermissionRequiredMixin

from django.forms.models import inlineformset_factory
from core.utils import calculateCashAtHand,calculateNetProfit

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
        txt=self.filter_class(request.GET,queryset).qs
        values=txt.values('id','transaction_code','date','amount','transaction_type','gl_account__title','transaction_mode','cheque_number','client__name','payee','created_by__username','comment')
        context['transactions']=values
        context['totals']=txt.aggregate(total_amount=(Sum("amount") )).get('total_amount',0) if values else 0
        context['filters']=self.filter_class(request.GET)
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
                print(request.GET.get('invoice_type',None))
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
            req=form.save(commit=True)

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
    template_name='finances/partials/invoice.html'

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

class IncomeExpenseReport(LoginRequiredMixin,View):
    filter_class = FinancialReportFilter
    form_class = TransactionForm
    model_class = Transaction
    template_name = "finances/reports/income-expenses-report.html"

    def get(self, request, *args, **kwargs):
        startdate=request.GET.get('date_min',None)
        enddate=request.GET.get('date_max',None)
        if not startdate:startdate=str(datetime.date.today().replace(day=1))
        if not enddate:enddate=datetime.date.today()
        year=request.GET.get('year',None)
        if year:
            startdate="%s-01-01"%(year)
            enddate="%s-12-31"%(year)
        mainAccounts=ChartOfAccount.objects.filter(parent__isnull=True)

        items=[]
        for chart in mainAccounts:
            items.append(get_ledger_account_children(chart,startdate=startdate,enddate=enddate))
            

        context={'filters':self.filter_class,'list':items,'title':("Income-Expenses report as at the end of the period between %s and %s"%(startdate,enddate)).upper()}
        if request.htmx:
            self.template_name='finances/reports/partials/income-expenses-report-section.html'
        return render(request,self.template_name,context)

def get_ledger_account_children(chart,startdate=None,enddate=None):
    children = list()
    children.append(chart)
    items=[]
    income,expenses=0,0

    for child in chart.children.all():
        items.append(get_ledger_account_children(child,startdate=startdate,enddate=enddate))
        # ids.append(child.pk)
    allTransactions=Transaction.objects.filter(gl_account__in=chart.get_children,date__lte=enddate,date__gte=startdate)
    expensesAmount=allTransactions.filter(transaction_type='expense').aggregate(total=Sum('amount'))
    expensesAmount=expensesAmount.get('total',0) if expensesAmount else 0
    expenses+=expensesAmount if expensesAmount else 0

    incomeAmount=allTransactions.filter(transaction_type='income').aggregate(total=Sum('amount'))
    incomeAmount=incomeAmount.get('total',0) if incomeAmount else 0
    income+=incomeAmount if incomeAmount else 0
    balance=income-expenses
        # children.extend(child.get_children(child))
    segment={'title':chart,'items':items,'income':income,'expenses':expenses,'balance':balance if balance>=0 else "(%s)"%(abs(balance))}
    return segment

class CashFlowView(LoginRequiredMixin, View):
    filter_class = FinancialReportFilter
    form_class = TransactionForm
    model_class = Transaction
    template_name = "finances/reports/cashflow-statement.html"

    def get(self, request, *args, **kwargs):
        action = request.GET.get("action", None)
        startdate=request.GET.get('date_min',None)
        enddate=request.GET.get('date_max',None)
        if not startdate:startdate=str(datetime.date.today().replace(day=1))
        if not enddate:enddate=datetime.date.today()
        year=request.GET.get('year',None)
        if year:
            startdate="%s-01-01"%(year)
            enddate="%s-12-31"%(year)
        context = {
            "title": ("Cashflow statement as at the end of the period between %s and %s"%(startdate,enddate)).upper(),
            "filters": self.filter_class(request.GET),
        }
        queryset = self.model_class.objects.filter(is_active=True,date__lte=enddate,date__gte=startdate)
        transactions_data = []
        transactions = queryset
        incomes=""
        expenses=""
        dividends=""        
        liabilities=""
        investing_activities=""
        financing_activities=""

        try:
            # This has all incomes and all expenses
            operating_activities_transactions=transactions.filter(gl_account__account_type__in=["Revenue","Operating expenses","Capital expenses","Purchases"])
            operating_activities_transactions_grouped=(
                operating_activities_transactions
                .values("gl_account__title")
                .annotate(amount=(Sum("amount") ))
            )
            # Combination of transactions related to assets
            investing_activities=(
                transactions.filter(gl_account__account_type__in=["Current assets","Fixed assets"])
                .values("gl_account__title")
                .annotate(amount=(Sum("amount") ))
            )
            # Transactions related to Owner's equity, longterm creditors
            financing_activities=(
                transactions.filter(gl_account__account_type__in=["Owners equity"])
                .values("gl_account__title")
                .annotate(amount=(Sum("amount") ))
            )
            data=[
                {'title':'Operating Activities','total':'','accounts':operating_activities_transactions_grouped},
                {'title':'Investing Activities','total':'','accounts':investing_activities},
                {'title':'Financing Activities','total':'','accounts':financing_activities},
            ]
            # transactions_data = chain(investing_activities,financing_activities)
            context['report']=data
            # context["transactions"] = transactions_data

        except Exception as e:
            print(e)
        
        
        context["headers"] = ["Account Name", "Amount"]
        context["filters"] = self.filter_class(request.GET, queryset)
        if request.htmx:
            self.template_name = (
                "finances/reports/partials/cashflow-statement-section.html"
            )

        return render(request, self.template_name, context)


class TrialBalanceView(LoginRequiredMixin, View):
    filter_class = FinancialReportFilter
    form_class = TransactionForm
    model_class = Transaction
    template_name = "finances/reports/trial-balance.html"

    def get(self, request, *args, **kwargs):
        action = request.GET.get("action", None)
        startdate=request.GET.get('date_min',None)
        enddate=request.GET.get('date_max',None)
        if not startdate:startdate=datetime.date.today().replace(day=1)
        if not enddate:enddate=datetime.date.today()
        year=request.GET.get('year',None)
        if year:
            startdate="%s-01-01"%(year)
            enddate="%s-12-31"%(year)

        context = {
            "title": ("Trial Balance statement as at the end of the period between %s and %s"%(startdate,enddate)).upper(),
            "filters": self.filter_class(request.GET),
        }
        transactions = self.model_class.objects.filter(is_active=True,date__lte=enddate,date__gte=startdate,gl_account__appear_on_trial_balance=True)
        transactions_data = []
        credits=transactions.filter(gl_account__account_type__in=["Revenue", "Current liabilities", "Long term liabilities", "Owners equity"])
        debits=transactions.filter(gl_account__account_type__in=["Current assets","Fixed assets", "Operating expenses","Capital expenses","Purchases"])


        try:
            total_debits,total_credits=debits.aggregate(Sum("amount")).get('amount__sum',0) if debits else 0,credits.aggregate(Sum("amount")).get('amount__sum',0) if credits else 0
            credits = list(
                credits
                .values("gl_account__title")
                .annotate(debits=(Sum("amount") - Sum("amount")))
                .annotate(credits=Sum("amount"))
            )
            debits = list(
                debits
                .values("gl_account__title")
                .annotate(debits=(Sum("amount")))
                .annotate(credits=(Sum("amount") - Sum("amount")))
            )
            # Calculate cash at hand at end of period
            cash_at_hand=calculateCashAtHand(startdate,enddate,'trial-balance')
            if total_credits>total_debits:
                debits.append({'gl_account__title':'Cash at hand','debits':cash_at_hand,'credits':0})
                total_debits=total_credits
            elif total_credits<total_debits:
                debits.append({'gl_account__title':'Creditors/Loans','credits':total_debits-total_credits,'debits':0})
                total_credits=total_debits
            context["footers"]=[{'title':'TOTALS','debits':total_debits,'credits':total_credits}]
            transactions_data = chain(credits, debits)

        except Exception as e:
            print(e)
        context["transactions"] = transactions_data
        context["headers"] = ["Account Name", "Debit", "Credit"]
        if request.htmx:
            self.template_name = (
                "finances/reports/partials/trial-balance-section.html"
            )

        return render(request, self.template_name, context)


class IncomeStatementReportView(LoginRequiredMixin, View):
    filter_class = FinancialReportFilter
    model_class = Transaction
    template_name = "finances/reports/income-statement.html"

    def get(self, request, *args, **kwargs):
        action = request.GET.get("action", None)
        context = {
            "filters": self.filter_class(request.GET),
        }
        startdate=request.GET.get('date_min',None)
        enddate=request.GET.get('date_max',None)
        if not startdate:startdate=str(datetime.date.today().replace(day=1))
        if not enddate:enddate=datetime.date.today()
        year=request.GET.get('year',None)
        if year:
            startdate="%s-01-01"%(year)
            enddate="%s-12-31"%(year)
        transactions = self.model_class.objects.filter(is_active=True,date__gte=startdate,date__lte=enddate)
        transactions_data = []
        # transactions = self.filter_class(request.GET, Transaction.objects.filter()).qs
        income_list=[]
        expense_list=[]
        purchases_list=[]
        try:
            income_list=transactions.filter(gl_account__account_type__in=["Revenue"]).values("gl_account__title").annotate(amount=Sum("amount") )
            expense_list=transactions.filter(gl_account__account_type__in=["Operating expenses","Capital Expenses"]).values("gl_account__title").annotate(amount=Sum("amount") )
            purchases_list=(transactions.filter(gl_account__account_type__in=["Purchases"]).values("gl_account__title").annotate(assets=(Sum("amount") )))
            # owners_equity_list=(
            #     transactions.filter(gl_account__account_type__in=["Owners equity"])
            #     .values("gl_account__title")
            #     .annotate(equity=(Sum("amount") ))
            # )
        except Exception as e:
            print(e)
        if transactions:
            total_income=income_list.aggregate(Sum("amount")).get('amount__sum',0) if income_list else 0
            
            # To be considered as the closing from the previous period calculations reports
            opening_stock=transactions.filter(gl_account__is_opening_stock=True)
            opening_stock=opening_stock.aggregate(Sum("amount")).get('amount__sum',0) if opening_stock else 0
            # calculateCashAtHand(None,datetime.datetime.strptime(startdate, "%Y-%m-%d")-datetime.timedelta(days=1))
            total_purchases=purchases_list.aggregate(Sum('amount')).get('amount__sum',0) if purchases_list else 0

            # Need to be grabbed from the Trial Balance (as cash at hand at end of period). In case the value is negative then it means it is credit (therefore need to use Zero)
            closing_stock=transactions.filter(gl_account__is_closing_stock=True)
            closing_stock=closing_stock.aggregate(Sum("amount")).get('amount__sum',0) if closing_stock else 0
            # calculateCashAtHand(startdate,enddate)
            goods_available_for_sale=(opening_stock+total_purchases)-closing_stock
            total_expenses=expense_list.aggregate(Sum("amount")).get('amount__sum',0) if expense_list else 0
            gross_profit=total_income-goods_available_for_sale
            net_profit=gross_profit-(total_expenses)
            context['report']={
                'income_list':income_list,
                'total_income':total_income,
                'cost_of_sales':[
                    {'title':'Opening Stock','amount':opening_stock if opening_stock>=0 else "(%s)"%(abs(opening_stock))},
                    {'title':'Purchases','amount':total_purchases},
                ],
                'closing_stock':"(%s)"%(abs(closing_stock)) if closing_stock!=0 else 0,
                'goods_available_for_sale':goods_available_for_sale if goods_available_for_sale>=0 else "(%s)"%(abs(goods_available_for_sale)),
                'gross_profit':gross_profit if gross_profit>=0 else "(%s)"%(abs(gross_profit)),
                'expense_list':expense_list,
                'total_expenses':total_expenses,
                'net_profit':net_profit if net_profit>=0 else "(%s)"%(abs(net_profit)),
                'title':("Statement of comprehensive account for the period between %s and %s"%(startdate, enddate)).upper()
            }
            
        if request.htmx:
            self.template_name = (
                "finances/reports/partials/income-statement-section.html"
            )

        return render(request, self.template_name, context)



class BalanceSheetView(LoginRequiredMixin, View):
    filter_class = FinancialReportFilter
    form_class = TransactionForm
    model_class = Transaction
    template_name = "finances/reports/balancesheet.html"

    def get(self, request, *args, **kwargs):
        action = request.GET.get("action", None)
        startdate=request.GET.get('date_min',None)
        enddate=request.GET.get('date_max',None)
        if not startdate:startdate=str(datetime.date.today().replace(day=1))
        if not enddate:enddate=datetime.date.today()
        year=request.GET.get('year',None)
        if year:
            startdate="%s-01-01"%(year)
            enddate="%s-12-31"%(year)
        context = {
            "title": "Balance Sheet",
            "filters": self.filter_class(request.GET),
        }
        
        transactions = self.model_class.objects.filter(is_active=True,date__gte=startdate,date__lte=enddate)
        transactions_data = []
        # transactions = self.filter_class(request.GET, Transaction.objects.filter()).qs
        incomes=""
        expenses=""
        dividends=""        
        liabilities=""
        investing_activities=""
        financing_activities=""
        current_assets_list,non_current_assets_list,current_liabilities_list,non_current_liabilities_list,owners_equity_list=[],[],[],[],[]

        try:
            current_assets_list=(
                transactions.filter(gl_account__account_type__in=["Current assets"])
                .values("gl_account__title")
                .annotate((Sum("amount") ))
            )
            non_current_assets_list=(
                transactions.filter(gl_account__account_type__in=["Fixed assets"])
                .values("gl_account__title")
                .annotate((Sum("amount") ))
            )
            dividends=(
                transactions.filter(gl_account__account_type__in=["Dividends"])
                .values("gl_account__title")
                .annotate((Sum("amount") ))
            )
            current_liabilities_list=(
                transactions.filter(gl_account__account_type__in=["Current liabilities"])
                .values("gl_account__title")
                .annotate(assets=(Sum("amount") ))
            )
            non_current_liabilities_list=(
                transactions.filter(gl_account__account_type__in=["Long term liabilities"])
                .values("gl_account__title")
                .annotate(assets=(Sum("amount") ))
            )
            owners_equity_list=(
                transactions.filter(gl_account__account_type__in=["Owners equity"])
                .values("gl_account__title")
                .annotate(equity=(Sum("amount") ))
            )
        except Exception as e:
            print(e)
        if transactions:
            assetsAmmount=(current_assets_list.aggregate(Sum("amount")).get('amount__sum',0) if current_assets_list else 0)+(non_current_assets_list.aggregate(Sum("amount")).get('amount__sum',0)if non_current_assets_list else 0)
            liabilitiesAmmount=(current_liabilities_list.aggregate(Sum("amount")).get('amount__sum',0) if current_liabilities_list else 0)+(non_current_liabilities_list.aggregate(Sum("amount")).get('amount__sum',0) if non_current_liabilities_list else 0)+(owners_equity_list.aggregate(Sum("amount")).get('amount__sum',0) if owners_equity_list else 0)
            
            # Picked from the PnL report
            net_profit=calculateNetProfit(startdate,enddate)
            liabilitiesAmmount+=net_profit
            owners_equity_list=list(owners_equity_list)

            
            owners_equity_list.append(
                {'gl_account__title':'Net Profit','amount':net_profit if net_profit>=0 else "(%s)"%(abs(net_profit))}
            )

            # To be picked from the Trial Balance
            cash_at_hand=calculateCashAtHand(startdate,enddate,'trial-balance')
            assetsAmmount+=cash_at_hand
            current_assets_list=list(current_assets_list)
            current_assets_list.append(
                {'gl_account__title':'Cash at hand','amount':cash_at_hand if cash_at_hand>=0 else "(%s)"%(abs(cash_at_hand))}
            )
            context['data']=[
                {'title':'ASSETS','items':[
                    {"title":"Current Assets","items":current_assets_list},
                    {"title":"Non-Current Assets","items":non_current_assets_list},
                ],'totals':assetsAmmount if assetsAmmount>=0 else "(%s)"%(abs(assetsAmmount))},
                {'title':'LIABILITIES & EQUITY','items':[
                    {"title":"Current Liabilities","items":current_liabilities_list},
                    {"title":"Non-Current Liabilities","items":non_current_liabilities_list},
                    {"title":"Equity","items":owners_equity_list}
                ],'totals':liabilitiesAmmount if liabilitiesAmmount>=0 else "(%s)"%(abs(liabilitiesAmmount))},
            ]
            context['report_title']=("Balance sheet for the period from %s to %s"%(startdate, enddate)).upper()
        context["filters"] = self.filter_class(request.GET)
        
        if request.htmx:
            self.template_name = (
                "finances/reports/partials/balancesheet-section.html"
            )

        return render(request, self.template_name, context)
