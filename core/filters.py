import django_filters
from django_filters import *
from django.contrib.admin.models import LogEntry

class LogsFilter(django_filters.FilterSet):
    # date_range = django_filters.DateRangeFilter(field_name='startdate')
    startdate = django_filters.DateFilter(field_name='action_time',lookup_expr='gte')
    enddate = django_filters.DateFilter(field_name='action_time',lookup_expr='lte')
    title = django_filters.CharFilter(field_name='object_repr', lookup_expr='icontains')
    class Meta:
        model=LogEntry
        fields='__all__'
