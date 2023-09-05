from django.urls import path,re_path
from .views import *


urlpatterns = [
    path('transactions/', TransactionList.as_view(),name="transactions"),
    path('transactions/<int:pk>/', TransactionDetail.as_view(),name='transaction'),
    path('gl-accounts/', ChartOfAccountList.as_view(),name='gl-accounts'),
    path('gl-accounts/<int:pk>/', ChartOfAccountDetail.as_view(),name='gl-account'),

    path('invoices/', InvoicesView.as_view(),name='invoices'),
    path('invoices/<int:pk>/', InvoiceDetailView.as_view(),name="invoice"),

    # Report
    path('income-expense-report',IncomeExpenseReport.as_view(),name='income-expense-report'),
    path("cashflow/", CashFlowView.as_view(), name="cashflow"),
    path("trialbalance/", TrialBalanceView.as_view(), name="trialbalance"),
    path("income-statement/", IncomeStatementReportView.as_view(), name="income-statement"),
    path("balancesheet/", BalanceSheetView.as_view(), name="balancesheet"),
]