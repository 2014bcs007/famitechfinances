from django.conf import settings
from django.shortcuts import redirect, reverse
import os
from .models import Config,Client

SidebarData = [
    {
        "title": "Dashboard", "path": reverse('home'), "icon": "fa fa-home"
    },
    {
        "title": "Users",
        "path": "#",
        "icon": "fa fa-users",
        "permissions": "users.view_user",
        "subNav": [
            { "title": "Users Summary", "path": "%s?display=summary"%(reverse('users')) },
            { "title": "Users Report", "path": reverse('users') },
            { "title": "Inactive Users", "path": "%s?is_active=False"%(reverse('users')) }
        ]
    },
    {
        "title": "Client Mgt",
        "path": "#",
        "icon": "fa fa-user",
        "permissions": "users.manage_user",
        "subNav": [
            { "title": "Add Client", "hx_path": "%s?action=get-form"%(reverse("clients")), "icon": "fa fa-pencil","permissions": "users.manage_user", },
            { "title": "Clients List", "path": reverse("clients"), "icon": "fa fa-user","permissions": "users.manage_user", },
        ]
    },
    {
        "title": "Quotes",
        "path": "#",
        "icon": "fa fa-wrench",
        "permissions": "finances.view_invoice",
        "subNav": [
            { "title": "Add Quote",'hx_target':'#modal-dialog-lg', "hx_path": "%s?invoice_type=quote&action=get-form"%(reverse("invoices")), "icon": "fa fa-pencil","permissions": "finances.add_invoice", },
            { "title": "List Quotes", "path": "%s?invoice_type=quote"%(reverse("invoices")), "icon": "fa fa-user","permissions": "finances.view_invoice", },
        ]
    },
    {
        "title": "Income",
        "path": "#",
        "icon": "fa fa-dollar",
        "subNav": [
            { "title": "Add Income", "hx_path": "%s?transaction_type=income&action=get-form"%(reverse("transactions")), "icon": "fa fa-pencil","permissions": "users.manage_user", },
            { "title": "Income List", "path": "%s?transaction_type=income"%(reverse("transactions")), "icon": "fa fa-user","permissions": "users.manage_user", },
        ]
    },
    {
        "title": "Expenses",
        "path": "#",
        "icon": "fa fa-paypal",
        "subNav": [
            { "title": "Add Expense", "hx_path": "%s?transaction_type=expense&action=get-form"%(reverse("transactions")), "icon": "fa fa-pencil","permissions": "users.manage_user", },
            { "title": "Expenses List", "path": "%s?transaction_type=expense"%(reverse("transactions")), "icon": "fa fa-user","permissions": "users.manage_user", },
        ]
    },
    {
        "title": "Audit Logs", "path": reverse('logs'), "icon": "fa fa-bars","permissions": "users.manage_user",
    },
    {
        "title":"Logout",'path':reverse("account_logout"),'icon':'fa fa-power-off'
    }
]

def core_configurations(request):
    BASE_URL="%s://%s"%(request.scheme,request.get_host())
    APP_LOGO='%s/%s'%(settings.MEDIA_URL,'company_logo.jpg')
    confs = Config.objects.filter(is_active=True)
    company_name=confs.filter(name="company_name").first()
    logo=confs.filter(name="company_logo").first()
    favicon=confs.filter(name="company_favicon").first()
    app_name=confs.filter(name="site_name").first()
    company_description=confs.filter(name="company_description").first()
    requisition_total_quotations=confs.filter(name="requisition_total_quotations").first()
    address=confs.filter(name="office_location").first()
    current_module=request.session.get("module","")


    topMenuShortcuts=[
        {'title':'Settings','permissions':'core.add_config','icon':'','subNav':[
            {'title':'General Settings','icon':'fa fa-gear','path':reverse('config')},
            { "title": "Ledger Accounts",'icon':'fa fa-wrench', "path": reverse('gl-accounts'),"permission": "core.manage_configuration", },
            {'title':'System Logs','icon':'fa fa-history','path':reverse('logs')},
            {'title':'User Groups','icon':'fa fa-user','path':reverse('user-roles')}
        ]},
        {'title':'Reports','icon':'','subNav':[
            {'title':'Users List','icon':'fa fa-user','permission':'users.view_user','path':reverse('users')},
            {'title':'Clients','icon':'fa fa-users','permission':'core.view_client','path':reverse('clients')},
            { "title": "Income Vs Expenses",'icon':'fa fa-list', "path": reverse('income-expense-report') },
            { "title": "CashFlow",'icon':'fa fa-list', "path": reverse('cashflow') },
            { "title": "Trial Balance",'icon':'fa fa-list', "path": reverse('trialbalance') },
            { "title": "Income Statement",'icon':'fa fa-list', "path": reverse('income-statement') },
            { "title": "Balance Sheet",'icon':'fa fa-list', "path": reverse('balancesheet') },
        ]}
    ]

    return {
        "BASE_URL":BASE_URL,
        "APP_NAME": app_name.value if app_name else "eFinance",
        "COMPANY_NAME": company_name.value if company_name else '',
        "COMPANY_DESCRIPTION": company_description.value if company_description else '',
        "ADDRESS": address.value if address else '',
        "APP_LOGO":logo.value if logo else APP_LOGO,
        "APP_FAVICON":favicon.value if favicon else APP_LOGO,
        "TOP_MENU_SHORTCUTS":topMenuShortcuts,
        "REQUISITION_TOTAL_QUOTATIONS":int(requisition_total_quotations.value) if requisition_total_quotations and requisition_total_quotations.value else 0,
        "WELCOME_VIDEO_URL":"",
        "MODULE":current_module,
        "SIDEBAR_MENU":SidebarData,
        "FORMULA_KEYS":"'{basic_salary}','{gross}','{taxable_income}'",
        "config":{
            "welcome_video_url":'',
            "welcome_banner":"%s/%s"%(settings.MEDIA_URL,'welcome_banner.jpg'),
            "default_avator":APP_LOGO,
            "welcome_title":"Start with more than a blinking cursor",
            "welcome_note":"",
        },
        'INSTALLED_APPS':settings.INSTALLED_APPS
    }
