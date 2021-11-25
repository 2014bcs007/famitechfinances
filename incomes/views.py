from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from .models import Source,Incomes
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
def searchIncomes(request):
    if request.method=="POST":

        search_str = json.loads(request.body).get('searchText')

        incomes = Incomes.objects.filter(
            amount__istartswith=search_str, owner=request.user
            ) | Incomes.objects.filter(
                date__istartswith=search_str, owner=request.user
                ) | Incomes.objects.filter(
                description__icontains=search_str, owner=request.user
                ) | Incomes.objects.filter(
                source__icontains=search_str, owner=request.user
                )
        data = incomes.values()

        return JsonResponse(list(data),safe=False)

@login_required(login_url='/authentication/login')
def index(request):
    source = Source.objects.all()
    incomeList = Incomes.objects.filter(owner=request.user)
    paginator = Paginator(incomeList,10)
    page_number = request.GET.get('page')
    page_object = Paginator.get_page(paginator,page_number)
    # currency=''
    currency = UserPreferences.objects.get(user=request.user).currency
    # import pdb
    # pdb.set_trace()

    context = {
        'source':source,
        'incomeList':incomeList,
        'page_object': page_object,
        'currency':currency,
        }
    return render(request,'incomes/index.html',context)

@login_required(login_url='/authentication/login')
def addincome(request):
    source = Source.objects.all()
    context = {
            'source':source,
            'fieldValues':request.POST,
            }
    # import pdb
    # pdb.set_trace()
    if request.method=="GET":
        return render(request,'incomes/addincomes.html',context)

    if request.method=="POST":
        amount = request.POST['amount']
        description = request.POST['description']
        source = request.POST['source']
        incomedate = request.POST['incomedate']

        if not amount:
            messages.error(request,'Amount is Required')
            return render(request,'incomes/addincomes.html',context)

        if not description:
            messages.error(request,'Desription is Required')
            return render(request,'incomes/addincomes.html',context)

        createincome = Incomes.objects.create(
            amount=amount,
            source=source,
            date=incomedate,
            description=description,
            owner = request.user,
        )
        createincome.save()
        messages.success(request, 'Income Saved Successfully')
        return redirect('index')

@login_required(login_url='/authentication/login')
def editIncome(request,id):
    incomes = Incomes.objects.get(pk=id)
    source = Source.objects.all()
    context = {
        'incomes' :incomes,
        'fieldValues' : incomes,
        'source':source,
    }
    # import pdb
    # pdb.set_trace()
    if request.method=="GET":
        return render(request,'incomes/editincomes.html',context)
    if request.method=="POST":
        amount = request.POST['amount']
        description = request.POST['description']
        source = request.POST['source']
        incomedate = request.POST['incomedate']
        # import pdb
        # pdb.set_trace()
        if not amount:
            messages.error(request,'Amount is Required')
            return render(request,'incomes/editincomes.html',context)
        if not description:
            messages.error(request,'Description is Required')
            return render(request,'incomes/editincomes.html',context)
        incomes.amount=amount
        incomes.source=source
        incomes.date=incomedate
        incomes.description=description
        incomes.owner = request.user
        incomes.save()
        messages.success(request, 'Income Update Successfully')
        return redirect('index')

@login_required(login_url='/authentication/login')
def deleteincome(request,id):
    incomes = Incomes.objects.get(pk=id)
    incomes.delete()
    messages.success(request,'Incomes Removed')
    return redirect('index')

def incomesummary(request):
    todays_date = datetime.date.today()
    sixmonthsago = todays_date - datetime.timedelta(days=30*6)

    incomes = Incomes.objects.filter(owner=request.user,date__gte=sixmonthsago,date__lte=todays_date)

    final_data_rep = {}

    def get_source(income):
        # import pdb
        # pdb.set_trace()
        return income.source

    source_list = list(set(map(get_source,incomes)))

    def get_income_source_amount(source):
        amount=0
        filtered_by_source = incomes.filter(source=source)
        for item in filtered_by_source:
            amount+=item.amount
        return amount

    for x in incomes:
        for y in source_list:
            final_data_rep[y]=get_income_source_amount(y)

    return JsonResponse({'income_source_data':final_data_rep},safe=False)

def income_stats_view(request):
    return render(request,'incomes/incomestat.html')

# Eport a CSV file
def exportcsv(request):
    response = HttpResponse(content_type='text/csv')
    # import pdb
    # pdb.set_trace()
    response['Content-Disposition'] = 'attachment; filename=Incomes '+str(datetime.datetime.now())+'.csv'
    writer = csv.writer(response)
    writer.writerow(['Amount','Source','Description','date'])
    incomes = Incomes.objects.filter(owner=request.user)

    for income in incomes:
        writer.writerow([income.amount,income.source,income.description,income.date])

    return response

def exportexcel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=Incomes'+str(datetime.datetime.now())+'.xls'
    
    style1 = xlwt.easyxf(num_format_str='D-MMM-YY')

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Incomes')
    row_num =0
    # fontstyle = xlwt.easyxf('font: name Times New Roman, color-index red, bold on',num_format_str='#,##0.00')
    fontstyle = xlwt.XFStyle()
    fontstyle.font.bold = True
    columns = ['Amount','Source','Description','date']

    for col_num in range(len(columns)): 
        ws.write(row_num, col_num, columns[col_num], fontstyle)
    fontstyle = xlwt.XFStyle()

    # set up dynamic rows
    rows = Incomes.objects.filter(owner=request.user).values_list(
        'amount','source', 'description', 'date'
    )
    for row in rows:
        row_num+=1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, str(row[col_num]), fontstyle)
    wb.save(response)

    return response

def exportpdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; attachment; filename=Incomes'+str(datetime.datetime.now())+'.pdf'
    
    incomes = Incomes.objects.filter(owner=request.user)
    sum= incomes.aggregate(Sum('amount'))
    # import pdb
    # pdb.set_trace()
    response['Content-Transfer-Encoding']='binary'
    html_string = render_to_string('incomes/pdfoutput.html',{'incomes':incomes,'total':sum['amount__sum']})

    html = HTML(string=html_string)

    result = html.write_pdf()
    with tempfile.NamedTemporaryFile(delete=True) as output:
        output.write(result)
        output.flush
        output.seek(0)
        response.write(output.read())
    return response
