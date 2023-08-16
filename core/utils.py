from django.shortcuts import reverse
from django.core.mail import send_mail,EmailMessage
import threading
import smtplib
from django.utils import timezone    
from io import BytesIO,StringIO
from core.models import Config,TermMeta,Log
import datetime
import xlsxwriter
from django.conf import settings
from django.contrib.admin.models import LogEntry

from django.contrib.contenttypes.models import ContentType

from .models import Config
def get_email_settings():
    try:
        dbConfig=Config.objects.filter(name__in=['email_smtp_host','email_from_address','email_smtp_port','email_smtp_username','email_smtp_password'])
        if dbConfig is not None:
            for configuration in dbConfig:
                if configuration.name=="email_smtp_host":
                    settings.EMAIL_HOST=configuration.value
                elif configuration.name=="email_smtp_username":
                    settings.EMAIL_HOST_USER=configuration.value
                elif configuration.name=="email_from_address":
                    settings.DEFAULT_FROM_EMAIL=configuration.value
                elif configuration.name=="email_smtp_password":
                    settings.EMAIL_HOST_PASSWORD=configuration.value
                elif configuration.name=="email_smtp_port":
                    settings.EMAIL_PORT=configuration.value
    except:
        pass

get_email_settings()        #Try hooking the settings on settings save
def send_email(subject='',body='',mail_from='', mail_to=[],cc=[],bcc=[],attachments=None):
    get_email_settings()        #Hook and pull the new settings at point of sending emails
    mail=EmailMessage(
        subject,         #Subject
        body, #Message
        mail_from,     #From
        mail_to,     #To
        headers={'Message-ID':'Random'},
        cc=cc,
        bcc=bcc
    )
    mail.content_subtype='html'
    if attachments:
        for f in attachments:
            mail.attach(f['name'], f['file'], f['content_type'])
    
    EmailThread(mail).start()


class EmailThread(threading.Thread):
    def __init__(self,email):
        self.email=email
        threading.Thread.__init__(self)

    def run(self):
        output=self.email.send(fail_silently=False)

# Function to save custom logs
def save_log(message="",instance=None,action_flag=1,):
    from django.db import transaction
    try:
        with transaction.atomic():
            from django_currentuser.middleware import (get_current_authenticated_user)
            user=get_current_authenticated_user()
            content_type = ContentType.objects.get_for_model(instance.__class__) if instance else None
            Log.objects.create(user=user,content_type=content_type,change_message=message,object_repr=instance,action_flag=action_flag)
    except:
        pass

def payrollExcel(employeePayroll):
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
 
    # Here we will adding the code to add data
    worksheet = workbook.add_worksheet("Payroll Payslips")

    for idx, data in enumerate(employeePayroll):
        row = 5 + idx
        worksheet.write_number(row, 0, idx + 1)
        worksheet.write_string(row, 1, data.employee.name)
        worksheet.write(row, 2, data.payroll.startdate.strftime('%d/%m/%Y'))

        my_list = [1, 2, 3, 4, 5]

        worksheet.write_row(row, 3, my_list)              #Adds row with data
        # worksheet.write_column(1, 0, my_list)         #Adds column with data
 
    output.seek(0)
    xlsx_data = output.getvalue()
    workbook.close()
    # xlsx_data contains the Excel file
    return xlsx_data


import datetime

def last_date_of_month(any_day):
    # The day 28 exists in every month. 4 days later, it's always next month
    next_month = any_day.replace(day=28) + datetime.timedelta(days=4)
    # subtracting the number of the current day brings us back one month
    return next_month - datetime.timedelta(days=next_month.day)

def calculate_paye(employee,gross,taxable_income):
    # Only use taxable_income instead of gross
    gross=taxable_income
    paye_tax=0
    if (gross >= 10000000):
        paye_tax = ((gross - 410000) * 0.3) + 25000 + ((0.1 * (gross - 10000000)))
    elif (gross < 10000000 and gross >= 410000):
        paye_tax = ((gross - 410000) * 0.3) + 25000
    elif (gross < 410000 and gross >= 335000):
        paye_tax = ((gross - 335000) * 0.2) + 10000
    elif (gross < 335000 and gross >= 235000):
        paye_tax = (gross - 235000) * 0.1
    return paye_tax





def calculateCashAtHand(startdate=None,enddate=None,report=None):
    from finances.models import Transaction
    transactions=Transaction.objects.filter(is_active=True)
    if startdate:
        transactions=transactions.filter(date__gte=startdate)
    if enddate:
        transactions=transactions.filter(date__lte=enddate)
    
    if report=='trial-balance':transactions=transactions.filter(gl_account__appear_on_trial_balance=True)
    try:
        credits=transactions.filter(gl_account__account_type__in=["Revenue", "Current liabilities", "Long term liabilities", "Owners equity"])
        debits=transactions.filter(gl_account__account_type__in=["Current assets","Fixed assets", "Operating expenses","Capital expenses","Purchases"])
        total_debits,total_credits=debits.aggregate(Sum("amount")).get('amount__sum',0) if debits else 0,credits.aggregate(Sum("amount")).get('amount__sum',0) if credits else 0
        bal=(total_credits-total_debits)
        return bal
    except:
        pass
    return 0

def calculateNetProfit(startdate=None,enddate=None):
    from finances.models import Transaction
    transactions=Transaction.objects.filter(is_active=True)
    if startdate:
        transactions=transactions.filter(date__gte=startdate)
    if enddate:
        transactions=transactions.filter(date__lte=enddate)
    try:
        income_list=transactions.filter(gl_account__account_type__in=["Revenue"]).values("gl_account__title").annotate(amount=Sum("amount") )
        expense_list=transactions.filter(gl_account__account_type__in=["Operating expenses","Capital Expenses"]).values("gl_account__title").annotate(amount=Sum("amount") )
        purchases_list=(transactions.filter(gl_account__account_type__in=["Purchases"]).values("gl_account__title").annotate(assets=(Sum("amount") )))
        total_income=income_list.aggregate(Sum("amount")).get('amount__sum',0) if income_list else 0
            
        # To be considered as the closing from the previous period calculations reports
        opening_stock=transactions.filter(gl_account__is_opening_stock=True)
        opening_stock=opening_stock.aggregate(Sum("amount")).get('amount__sum',0) if opening_stock else 0
        total_purchases=purchases_list.aggregate(Sum('amount')).get('amount__sum',0) if purchases_list else 0

        # Need to be grabbed from the Trial Balance (as cash at hand at end of period). In case the value is negative then it means it is credit (therefore need to use Zero)
        # closing_stock=calculateCashAtHand(startdate,enddate)
        closing_stock=transactions.filter(gl_account__is_closing_stock=True)
        closing_stock=closing_stock.aggregate(Sum("amount")).get('amount__sum',0) if closing_stock else 0
        goods_available_for_sale=(opening_stock+total_purchases)-closing_stock
        total_expenses=expense_list.aggregate(Sum("amount")).get('amount__sum',0) if expense_list else 0
        gross_profit=total_income-goods_available_for_sale
        net_profit=gross_profit-(total_expenses)
        return net_profit
    except Exception as ex:
        print(ex)
    return 0