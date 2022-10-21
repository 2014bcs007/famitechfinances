
import django_filters
from .models import *

class ChartOfAccountsFilter(django_filters.FilterSet):
    # target_model__model = django_filters.DateFilter(field_name='date')
    class Meta:
        model=ChartOfAccount
        fields='__all__'
        # fields=['model_id','account_number','target_model__model','opendate','status','branch']
        # exclude=['is_active','created_by']

class TransactionsFilter(django_filters.FilterSet):
    # target_model__model = django_filters.DateFilter(field_name='date')
    class Meta:
        model=Transaction
        # fields=['till_session','till','date','till_session__teller','target_model__model','target_id','branch']
        exclude=['is_active','created_by']