from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from .models import Category,Expense
from django.contrib import messages
from django.core.paginator import Paginator
import json
from django.http import JsonResponse,HttpResponse
from userpreferences.models import UserPreferences
import datetime
import csv
import xlwt
from weasyprint import HTML, CSS
# from weasyprint.text.fonts import FontConfiguration
from django.template.loader import render_to_string

import tempfile
from django.db.models import Sum
# Create your views here.

# Create a search function here
def searchExpenses(request):
    if request.method=="POST":

        search_str = json.loads(request.body).get('searchText')

        expenses = Expense.objects.filter(
            amount__istartswith=search_str, owner=request.user
            ) | Expense.objects.filter(
                date__istartswith=search_str, owner=request.user
                ) | Expense.objects.filter(
                description__icontains=search_str, owner=request.user
                ) | Expense.objects.filter(
                category__icontains=search_str, owner=request.user
                )
        data = expenses.values()

        return JsonResponse(list(data),safe=False)

@login_required(login_url='/authentication/login')
def index(request):
    categories = Category.objects.all()
    expenseList = Expense.objects.filter(owner=request.user)
    paginator = Paginator(expenseList,10)
    page_number = request.GET.get('page')
    page_object = Paginator.get_page(paginator,page_number)
    # currency=''
    currency = UserPreferences.objects.get(user=request.user).currency
    # import pdb
    # pdb.set_trace()

    context = {
        'categories':categories,
        'expenseList':expenseList,
        'page_object': page_object,
        'currency':currency,
        }
    return render(request,'expenses/index.html',context)

@login_required(login_url='/authentication/login')
def addexpense(request):
    categories = Category.objects.all()
    context = {
            'categories':categories,
            'fieldValues':request.POST,
            }
    # import pdb
    # pdb.set_trace()
    if request.method=="GET":
        return render(request,'expenses/addexpense.html',context)

    if request.method=="POST":
        amount = request.POST['amount']
        description = request.POST['description']
        category = request.POST['category']
        expensedate = request.POST['expensedate']

        if not amount:
            messages.error(request,'Amount is Required')
            return render(request,'expenses/addexpense.html',context)

        if not description:
            messages.error(request,'Desription is Required')
            return render(request,'expenses/addexpense.html',context)

        createExpense = Expense.objects.create(
            amount=amount,
            category=category,
            date=expensedate,
            description=description,
            owner = request.user,
        )
        createExpense.save()
        messages.success(request, 'Expense Saved Successfully')
        return redirect('index')

@login_required(login_url='/authentication/login')
def editExpense(request,id):
    expense = Expense.objects.get(pk=id)
    categories = Category.objects.all()
    context = {
        'expense' :expense,
        'fieldValues' : expense,
        'categories':categories,
    }
    # import pdb
    # pdb.set_trace()
    if request.method=="GET":
        return render(request,'expenses/editexpense.html',context)
    if request.method=="POST":
        amount = request.POST['amount']
        description = request.POST['description']
        category = request.POST['category']
        expensedate = request.POST['expensedate']

        if not amount:
            messages.error(request,'Amount is Required')
            return render(request,'expenses/editexpense.html',context)
        if not description:
            messages.error(request,'Description is Required')
            return render(request,'expenses/editexpense.html',context)
        expense.amount=amount
        expense.category=category
        expense.date=expensedate
        expense.description=description
        expense.owner = request.user
        expense.save()
        messages.success(request, 'Expense Update Successfully')
        return redirect('index')

@login_required(login_url='/authentication/login')
def deleteExpense(request,id):
    expense = Expense.objects.get(pk=id)
    expense.delete()
    messages.success(request,'Expense Removed')
    return redirect('index')

def expensesummary(request):
    todays_date = datetime.date.today()
    sixmonthsago = todays_date - datetime.timedelta(days=30*6)

    expenses = Expense.objects.filter(owner=request.user,date__gte=sixmonthsago,date__lte=todays_date)

    final_data_rep = {}

    def get_category(expense):
        return expense.category

    category_list = list(set(map(get_category,expenses)))

    def get_expense_category_amount(category):
        amount=0
        filtered_by_category = expenses.filter(category=category)
        for item in filtered_by_category:
            amount+=item.amount
        return amount

    for x in expenses:
        for y in category_list:
            final_data_rep[y]=get_expense_category_amount(y)

    return JsonResponse({'expense_category_data':final_data_rep},safe=False)

def stats_view(request):
    return render(request,'expenses/stats.html')
# Eport a CSV file
def exportcsv(request):
    response = HttpResponse(content_type='text/csv')
    # import pdb
    # pdb.set_trace()
    response['Content-Disposition'] = 'attachment; filename=Expenses'+str(datetime.datetime.now())+'.csv'
    writer = csv.writer(response)
    writer.writerow(['Amount','Category','Description','date'])
    expenses = Expense.objects.filter(owner=request.user)

    for expense in expenses:
        writer.writerow([expense.amount,expense.category,expense.description,expense.date])

    return response

def exportexcel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=Expenses'+str(datetime.datetime.now())+'.xls'
    
    style1 = xlwt.easyxf(num_format_str='D-MMM-YY')

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Expenses')
    row_num =0
    # fontstyle = xlwt.easyxf('font: name Times New Roman, color-index red, bold on',num_format_str='#,##0.00')
    fontstyle = xlwt.XFStyle()
    fontstyle.font.bold = True
    columns = ['Amount','Category','Description','date']

    for col_num in range(len(columns)): 
        ws.write(row_num, col_num, columns[col_num], fontstyle)
    fontstyle = xlwt.XFStyle()

    # set up dynamic rows
    rows = Expense.objects.filter(owner=request.user).values_list(
        'amount','category', 'description', 'date'
    )
    for row in rows:
        row_num+=1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, str(row[col_num]), fontstyle)
    wb.save(response)

    return response

def exportpdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; attachment; filename=Expenses'+str(datetime.datetime.now())+'.pdf'
    
    expenses = Expense.objects.filter(owner=request.user)
    sum= expenses.aggregate(Sum('amount'))
    # import pdb
    # pdb.set_trace()
    response['Content-Transfer-Encoding']='binary'
    html_string = render_to_string('expenses/pdfoutput.html',{'expenses':expenses,'total':sum['amount__sum']})

    html = HTML(string=html_string)

    result = html.write_pdf()
    with tempfile.NamedTemporaryFile(delete=True) as output:
        output.write(result)
        # output.write_pdf(response)
        output.flush
        output.seek(0)
        # output = open(output.name,'rb')
        # HTML(string=html).write_pdf(response)
        response.write(output.read())
    return response
