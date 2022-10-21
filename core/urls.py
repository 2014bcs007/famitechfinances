from django.urls import path,re_path
from .views import *


urlpatterns = [
    path('', ConfigurationsView.as_view(),name="config"),
    path('templates/', TemplatesList.as_view()),
    path('templates/<str:code>/', TemplateDetail.as_view(),name="template"),


    re_path(r'^terms/(?P<term>[-\w]+)/$', TermsList.as_view(),name="terms"),
    path('terms/single/<int:pk>/', TermDetail.as_view(),name="term"),
    # re_path(r'^(?P<term>[-\w]+)/(?P<pk>[0-9])/$', TermDetail.as_view()),

    path('clients/', ClientsView.as_view(),name='clients'),
    path('clients/<int:pk>/', ClientDetailView.as_view(),name="client"),

]
