
from django.contrib import admin
from django.conf import settings

from django.conf.urls.static import static
from django.urls import include, path, re_path
from users.views import *
from core.views import *
from django.shortcuts import reverse,redirect

from .views import Dashboard

urlpatterns = [
    # path('',Dashboard.as_view(),name='dashboard'),
    path('', HomeView.as_view(), name='home'),
    path('stats/', StatsView.as_view(), name='stats'),
    path('events/', EventsList.as_view(), name='events'),
    path ('auth/',include('allauth.urls')),#Linking to allAuth Library
    path('user-management/', include('users.urls')),
    path('logs/', LogsList.as_view(), name='logs'),
    path('config/', include('core.urls')),

    path('finance/', include('finances.urls')),
    path('todolist/', include('todolist.urls')),
    # path('preferences/', include('userpreferences.urls')),
    path('admin/', admin.site.urls),
]
