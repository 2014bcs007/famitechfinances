from django.conf import settings
from django.shortcuts import redirect, reverse
import os
from .utils import SidebarData
from .models import Config,Client


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
