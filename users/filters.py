import django_filters
from django_filters import *
from django.contrib.auth.models import Group
from .models import User

class GroupsFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    class Meta:
        model=Group
        fields=['name']


class UsersFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='first_name', lookup_expr='icontains')
    class Meta:
        model=User
        # fields='__all__'
        exclude=['profile_pic','signature','employment_attachment','termination_attachment']