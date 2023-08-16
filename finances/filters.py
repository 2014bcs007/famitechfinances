
import django_filters
from django_filters import *
from .models import *
from django_filters.widgets import RangeWidget

class ChartOfAccountsFilter(django_filters.FilterSet):
    # target_model__model = django_filters.DateFilter(field_name='date')
    class Meta:
        model=ChartOfAccount
        fields='__all__'
        # fields=['model_id','account_number','target_model__model','opendate','status','branch']
        # exclude=['is_active','created_by']

class TransactionsFilter(django_filters.FilterSet):
    transaction_type=django_filters.ChoiceFilter(choices=(('income',"Income"),('expense',"Expenses")))
    date=DateFromToRangeFilter(field_name='date', widget=RangeWidget(attrs={'type':'date'}))
    amount=RangeFilter(field_name='amount',label='amount', widget=RangeWidget(attrs={'type':'number'}))
    
    class Meta:
        model=Transaction
        exclude=['is_active','updated_by','updated_at','created_at']

class InvoicesFilter(django_filters.FilterSet):
    class Meta:
        model=Invoice
        exclude=['is_active','created_by']

class FinancialReportFilter(django_filters.FilterSet):
    date=DateFromToRangeFilter(field_name='date', widget=RangeWidget(attrs={'type':'date'}))
    year = django_filters.NumberFilter(field_name='date',label='Year',lookup_expr='year')
    
    class Meta:
        model=Transaction
        fields=['date','year']