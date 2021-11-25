from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns=[
    path('', views.index,name='index'),
    path('addincome', views.addincome,name='addincome'),
    path('editIncome/<int:id>', views.editIncome,name='editIncome'),
    path('deleteIncome/<int:id>', views.deleteincome,name='deleteIncome'),
    path('search-income', csrf_exempt(views.searchIncomes),name='search-income'),
    path('incomesummary',views.incomesummary,name='incomesummary'),
    path('income_stats_view',views.income_stats_view,name='income_stats_view'),
    path('exportcsv',views.exportcsv,name='exportcsv'),
    path('exportexcel',views.exportexcel,name='exportexcel'),
    path('exportpdf',views.exportpdf,name='exportpdf'),
]