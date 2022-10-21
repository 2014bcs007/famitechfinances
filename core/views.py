from django.shortcuts import render,redirect,reverse,HttpResponse

from users.models import *
from core.models import *

from .filters import LogsFilter
from django.conf import settings
import json
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from django.core.files.storage import FileSystemStorage
from django.contrib.admin.models import LogEntry
from django.db.models import Q,Sum,F,Value,CharField
from django.db.models.functions import Concat
from django.views import View
from .forms import *
from users.forms import CustomResetPasswordKeyForm
from django.contrib.auth.mixins import LoginRequiredMixin,PermissionRequiredMixin
import datetime,calendar
from itertools import chain
from core.utils import save_log
from django.contrib.auth.hashers import make_password
from finances.models import *

# Create your views here.
class HomeView(LoginRequiredMixin,View):
    template_name='index.html'
    def get(self,request):
        context={}
        if request.user.is_authenticated:
            if 'module' in request.GET:
                request.session['module']=request.GET['module']
                return redirect(reverse('home'))
            if 'system_client' in request.GET:
                request.session['system_client']=request.GET['system_client']
                next=request.GET.get('next',reverse('home'))
                return redirect(next)
            
            try:
                shift=EmployeeShift.objects.filter(employee=request.user,checkin__isnull=False,checkout__isnull=True,pk=request.session.get("employee_shift",0)).first()
            except:
                shift=None
            context={
                'shift':shift,
            }
            if request.user.is_employee:
                leaves=EmployeeLeave.objects.filter(employee=request.user,is_active=True,status=1)
                context['leaves']=leaves
        if request.htmx:
            self.template_name=request.GET.get('template',self.template_name)
        return render(request, self.template_name,context)


class StatsView(LoginRequiredMixin,View):
    template_name="core/partials/stats.html"

    def get(self, request):
        stats={}
        graphs={}
        tables={}
        
        YEARS= [r for r in range(1984, datetime.date.today().year+2)]
        year=int(request.GET.get("year",datetime.date.today().year))
        response = {'YEARS':YEARS,'YEAR':year}
        filter=self.request.GET.get('module', [])
        if request.user.is_authenticated:
            employees=User.objects.filter(is_employee=True)
            clients=Client.objects.filter()
            expenses=Transaction.objects.filter(is_active=True,date__year=year,transaction_type='expense')
            income=Transaction.objects.filter(is_active=True,date__year=year,transaction_type='income')
            if not request.user.is_superuser:
                income=income.filter(created_by=request.user)
            stats['Employees']=[
                {'title':'New','total':employees.order_by('-date_joined')[:10].count()},
                {'title':'Terminated','total':employees.filter(is_active=False).count()},
                {'title':'All','total':employees.count()},
            ]
            stats['Other stats']=[
                {'title':'Total Clients','total':clients.count()},
            ]
            incomeGraph=[]
            expensesGraph=[]

            incomeCategoriesGraph=[]
            expenseCategoriesGraph=[]
            ledgerAccounts=ChartOfAccount.objects.filter()
            for cat in ledgerAccounts:
                if cat.account_type=='income':
                    items=income.filter(gl_account=cat).aggregate(total=Sum("amount"))
                    tot= items['total'] if items['total'] else 0
                    incomeCategoriesGraph.append({"name":cat.name,"value":tot})
                if cat.account_type=='expense':
                    items=expenses.filter(gl_account=cat).aggregate(total=Sum("amount"))
                    tot= items['total'] if items['total'] else 0
                    expenseCategoriesGraph.append({"name":cat.name,"value":tot})
            graphs['income_categories_graph']={"title":"Income by category","key":"income_categories_graph","type":"pie","class":"col-md-3",'icon':'fa fa-signal',"labels":{"label":"name","value":"value"},"data":incomeCategoriesGraph}
            graphs['expense_categories_graph']={"title":"Expenses by category","key":"expense_categories_graph","type":"pie","class":"col-md-3",'icon':'fa fa-signal',"labels":{"label":"name","value":"value"},"data":expenseCategoriesGraph}
            
            for i in range(1,13):
                month = "%01d"%(i)
                startdate="%s-%s-01"%(year,month)
                enddate="%s-%s-%s"%(year,month,calendar.monthrange(int(year), int(month))[1])
                month_name=datetime.datetime.strptime(month, "%m").strftime("%b")

                items=income.filter(date__month=month,date__year=year).aggregate(total=Sum("amount"))
                tot= items['total'] if items['total'] else 0
                incomeGraph.append({"month":month_name,"value":tot})
            graphs['employee_taxes_graph']={"title":"Income Generated","key":"income_graph","type":"bar","class":"col-md-6",'icon':'fa fa-signal',"labels":{"label":"month","value":"value"},"data":incomeGraph}
        if request.user.is_superuser:
            users=User.objects.filter(is_employee=False)
            activeUsers=users.filter(is_active=True)
            response['users']=[
                {"key":"all","title":"All",'filter':"","data":activeUsers},
                {"key":"all","title":"Inactive",'filter':"","data":users.filter(is_active=False)},
                {"key":"all","title":"Today's Login",'filter':"","data":activeUsers.filter(last_login__date=datetime.date.today())},
                {"key":"recent","title":"Recent",'filter':"","data":activeUsers.order_by('-date_joined')[:3]},
                
            ]
            tables['recent_logins']={"title":"Last logins","icon":"fa fa-users","class":"col-md-6","data":activeUsers.order_by('-last_login').values("first_name","last_name","email","last_login")[:5]}
        response['stats']=stats
        response['graphs']=graphs
        response['tables']=tables
        return render(request,self.template_name,response)



class ConfigurationsView(PermissionRequiredMixin,View):
    permission_required = ('users.manage_user',)
    template_name="index.html"
    def get(self,request):
        context={
            'tab':request.GET.get("tab",'general'),
            'templates':settings.NOTIFICATION_TEMPLATES,
        }
        confs = Config.objects.filter(is_active=True)
        if not request.user or not self.request.user.is_authenticated:
            confs=confs.exclude(name__icontains='password')
        data = {}
        if confs is not None and len(confs)>0:
            for f in confs:
                data[f.name] = f.value
        if request.user.is_authenticated:
            context['terms']=settings.TERMS_CHOICES
            self.template_name='core/index.html'
        context['settings']=data
        
        return render(request, self.template_name,context)
    def post(self, request, *args, **kwargs):
        for key,val in request.POST.items():
            if key.startswith('settings['):
                key=key.replace("settings[","").replace("]","")
                if key in ['email_smtp_enable','email_smtp_auth']:
                    val='true' if val=='on' else 'false'
                conf=Config.objects.get_or_create(name=key)[0]
                if not conf.value ==val:
                    conf.value=val
                    conf.save()
        if len(request.FILES)!=0:
            fs = FileSystemStorage()
            files=request.FILES
            for key in files:
                name = fs.save(files[key].name.replace(" ","_"), files[key])
                url = fs.url(name)
                conf=Config.objects.get_or_create(name=key)[0]
                conf.value=url
                conf.save()
        return redirect("%s?tab=%s"%(reverse('config'),request.GET.get("tab",'general')))
        return render(request, self.template_name)


class TermsList(View):
    template_name='core/terms.html'
    
    def get(self, request, *args, **kwargs):
        term = self.kwargs['term']
        terms=Term.objects.filter(is_active=True,type=term).order_by('name')
        sItems=settings.AVAILABLE_TERMSLIST
        m = next((item for item in sItems if item['key'] == term), None)
        # print("Here:",settings.AVAILABLE_TERMSLIST,sItems)
        context={
            'items':terms,
            'term_key':term,
            'meta_keys':m.get('meta_keys',[]) if m else [],
        }
        if request.htmx:
            self.template_name='core/partials/terms-section.html'
        if 'action'in request.GET and request.GET['action']=='get-form':
            context['form']=TermForm(initial={'type':term})
            self.template_name='core/partials/term-form.html'
        return render(request, self.template_name,context)

    def post(self, request, *args, **kwargs):
        form =TermForm(request.POST)
        context={}
        if form.is_valid():
            ser=form.save()
            for key,val in request.POST.items():
                if key.startswith('meta['):
                    key=key.replace("meta[","").replace("]","")
                    conf=TermMeta.objects.get_or_create(meta_key=key,term=ser)[0]
                    if val=='on':val="True"
                    conf.meta_value=val
                    conf.save()
            return HttpResponse(status=204,headers={'HX-Trigger':'listChanged'})
            
        else:
            context['form']=form
            self.template_name='core/partials/term-form.html'
        return render(request, self.template_name,context)


class TermDetail(View):
    template_name='core/partials/term-form.html'
    
    def get(self, request, *args, **kwargs):
        pk = kwargs['pk']
        term = get_object_or_404(Term,pk=pk)
        sItems=settings.AVAILABLE_TERMSLIST
        m = next((item for item in sItems if item['key'] == term.type), None)
        keys=m.get('meta_keys',[]) if m else []
        saved_meta=term.get_meta()
        if keys and saved_meta:
            for index in range(len(keys)):
                key=keys[index]
                mValue = saved_meta.get(key['meta_key'],None)
                keys[index]['value']=mValue
        context={'term':term,'term_key':term.type,'id':pk,'meta_keys':keys,}
        if 'action'in request.GET and request.GET['action']=='get-form':
            context['form']=TermForm(instance=term,initial={'type':term.type})
        return render(request, self.template_name,context)
    def post(self, request, pk):
        term = Term.objects.get(pk=pk)
        context={'term_key':term.type,}
        form=TermForm(request.POST,instance=term)
        if form.is_valid():
            term=form.save()
            TermMeta.objects.filter(term=term).delete()
            for key,val in request.POST.items():
                if key.startswith('meta['):
                    key=key.replace("meta[","").replace("]","")
                    conf=TermMeta.objects.get_or_create(meta_key=key,term=term)[0]
                    if val=='on':val=True
                    conf.meta_value=val
                    conf.save()
            return HttpResponse(status=204,headers={'HX-Trigger':'listChanged'})
            
        else:
            context['form']=form
            self.template_name='core/partials/term-form.html'
        return render(request, self.template_name,context)

        

class EventsList(View):
    def get(self,request):
        records = []
        leaves=EmployeeLeave.objects.filter(status=1)
        if request.user.is_client:
            leaves=leaves.filter(employee__client=request.user)
        elif not request.user.is_superuser:
            leaves=leaves.filter(employee=request.user) 
        for leave in leaves:
            records.append({"title":"%s"%(leave.category),'color':'green','type':'leave','description':"%s: %s"%(leave.employee,leave.reason), "id":leave.id,"date":str(leave.startdate),'end':str(leave.enddate)})
        tasks = Task.objects.filter()
        for task in tasks:
            records.append(
                {"title":task.title,'type':'task', "id":task.id,"date":str(task.employee_shift.date),'end':str(task.employee_shift.date),'task':''}
                )
        return HttpResponse(json.dumps(records))
    
    def post(self,request):
        try:
            task=Task.objects.create(
                title=request.POST.get('content',None),
                startdate=request.POST.get('start_time',None),
                enddate=request.POST.get('end_time',None),
                owner_model=ContentType.objects.get(model='user'),
                owner_id=request.user.pk)
        except Exception as ex:
            print(ex)
        return HttpResponse()

class LogsList(PermissionRequiredMixin,View):
    permission_required = ('users.manage_user',)
    filter_class=LogsFilter
    template_name="core/logs.html"
    
    def get(self, request, *args, **kwargs):
        adminLogs=LogEntry.objects.filter().prefetch_related("user").prefetch_related("content_type")
        userLogs=Log.objects.filter().prefetch_related("user").prefetch_related("content_type")
        adminLogs=self.filter_class(request.GET,adminLogs)
        # combine querysets 
        queryset_chain = chain(
            adminLogs.qs,
            self.filter_class(request.GET,userLogs).qs
        )
        qs = sorted(queryset_chain, 
            key=lambda instance: instance.action_time, 
            reverse=True)
        count = len(qs) # since qs is actually a list
        context={'list':qs,'count':len(qs),'tab':request.GET.get('tab','admin'),'filters':self.filter_class(request.GET)}
        return render(request, self.template_name,context)

class TemplatesList(PermissionRequiredMixin,View):
    permission_required = ('users.manage_user',)
    
    def get_queryset(self, *args, **kwargs):
        return Template.objects.filter(is_active=True).order_by('code')

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class TemplateDetail(PermissionRequiredMixin,View):
    permission_required = ('users.manage_user',)
    template_name='core/partials/template-form.html'
    def get(self, request, code):
        m = next((item for item in settings.NOTIFICATION_TEMPLATES if item['code'] == code), None)
        template = Template.objects.get_or_create(code=code)[0]
        form=TemplateForm(instance=template)
        context={'template':template,'form':form,'settings':m}
        return render(request, self.template_name,context)
    def post(self, request, code):
        template = Template.objects.filter(code=code).first()
        m = next((item for item in settings.NOTIFICATION_TEMPLATES if item['code'] == code), None)
        form=TemplateForm(request.POST,instance=template)
        context={'template':template,'form':form,'settings':m}
        if form.is_valid():
            form.save()
            return HttpResponse(status=204)
        else:
            render(request, self.template_name,context)
            



class ClientsView(PermissionRequiredMixin,View):
    permission_required = ('core.view_client',)
    model_class=Client
    form_class=ClientForm
    template_name="core/clients/index.html"
    
    def get(self, request, *args, **kwargs):
        action=request.GET.get("action",None)
        context={}
        if action=="get-form":
            context['form']=self.form_class
            self.template_name="core/partials/client-form.html"
            return render(request, self.template_name,context)
        items=self.model_class.objects.filter()
        context['list']=items
        if request.htmx:
            self.template_name="core/partials/clients-list.html"
        return render(request, self.template_name,context)

    def post(self, request, *args, **kwargs):
        form=self.form_class(request.POST,request.FILES)
        context={'form':form,}
        if form.is_valid():
            form.save()
            return HttpResponse(status=204,headers={'HX-Trigger':'clientsListChanged'})
        else:
            self.template_name="core/partials/client-form.html"
        render(request, self.template_name,context)


class ClientDetailView(LoginRequiredMixin,View):
    # permission_required = ('clients.view_client',)
    template_name='core/clients/client.html'
    model_class=Client
    form_class=ClientForm
    def get(self, request, pk):
        client = self.model_class.objects.get(pk=pk)
        action=request.GET.get("action",None)
        context={'client':client,'password_reset_form':CustomResetPasswordKeyForm()}
        if action=="get-form":
            self.template_name="core/partials/client-form.html"
            context['form']=self.form_class(instance=client,initial={'pop-password':True})
        return render(request, self.template_name,context)
    def post(self, request, pk):
        client = self.model_class.objects.get(pk=pk)
        action=request.GET.get('action',None)
        context={'client':client}
        if action=="update-password":
            form =CustomResetPasswordKeyForm(request.POST)
            if form.is_valid():
                password=form.cleaned_data.get('password1',None)
                client.password=make_password(password)
                client.save()
                save_log("%s changed password for client %s"%(request.user,client))
                return HttpResponse("<div class='alert alert-success'>Password reset successfully</div>")
            else:
                context['password_reset_form']=form
                print(form.errors)
                self.template_name="core/partials/client-password-reset-form.html"
                return render(request, self.template_name,context)
        else:
            form=self.form_class(request.POST,request.FILES,instance=client)
            context={'client':client,'form':form}
            if form.is_valid():
                form.save()
                return HttpResponse(status=204,headers={'HX-Trigger':'clientsListChanged'})
        return render(request, self.template_name,context)