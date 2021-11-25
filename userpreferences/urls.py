from django.urls import path,include
from . import views
# from .views import PreferencesProcessingView

urlpatterns=[
    path('', views.index, name='preferences'),
    # path('PreferencesProcessingView', PreferencesProcessingView.as_view(), name='PreferencesProcessingView')
]