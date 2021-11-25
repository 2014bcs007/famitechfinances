from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns=[
    path('', views.index,name='expenses'),
    path('addexpense', views.addexpense,name='addexpense'),
    path('editExpense/<int:id>', views.editExpense,name='editExpense'),
    path('deleteExpense/<int:id>', views.deleteExpense,name='deleteExpense'),
    path('search-expenses', csrf_exempt(views.searchExpenses),name='search-expenses'),
    path('expensesummary',views.expensesummary,name='expensesummary'),
    path('stats_view',views.stats_view,name='stats_view'),
    path('exportcsv',views.exportcsv,name='exportcsv'),
    path('exportexcel',views.exportexcel,name='exportexcel'),
    path('exportpdf',views.exportpdf,name='exportpdf'),
]