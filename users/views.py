from django.shortcuts import render,get_object_or_404,HttpResponse,reverse,HttpResponseRedirect,redirect
from django.views import View
from django.views.generic import ListView
from .filters import *
from .forms import *

from .models import User
from core.models import *

from core.utils import save_log,last_date_of_month,send_email

from django.db.models import Case, When,Q,Count,F
from django.utils import timezone
from django.contrib.auth import authenticate,login
import calendar
import datetime
from django.contrib.contenttypes.fields import ContentType
from django.urls import reverse
from django.core.paginator import EmptyPage,PageNotAnInteger,Paginator
from django.contrib.auth.mixins import LoginRequiredMixin,PermissionRequiredMixin


class GroupsView(PermissionRequiredMixin,ListView):
    permission_required = ('users.manage_user',)
    template_name="account/user-roles.html"
    paginate_by=40

    def get_template_names(self):
        if self.request.htmx:
            return 'account/partials/user-roles-section.html'
        return "account/user-roles.html"
    
    def get_queryset(self):
        return Group.objects.filter().prefetch_related("permissions")

    def get(self,request):
        page=request.GET.get("page",1)
        search=request.GET.get("search",None)
        groups =Group.objects.filter().order_by('name').prefetch_related("permissions")
        filters=GroupsFilter(request.GET,groups)
        groups=filters.qs
        if search:
            groups=groups.filter(name__icontains=search)
        context={'list':groups}
        display=request.GET.get('display','section')
        if self.request.htmx:
            self.template_name= 'account/partials/user-roles-%s.html'%(display)
        if 'action' in request.GET and request.GET['action']=='get-form':
            context['form']=UserRoleForm()
            self.template_name="account/partials/user-role-form.html"
            return render(request, self.template_name,context)
        return render(request, self.template_name,context)
    
    def post(self, request, *args, **kwargs):
        form=UserRoleForm(request.POST)
        context={'form':form}
        if form.is_valid():
            form.save()
            return HttpResponse(status=204,headers={'HX-Trigger':'userListChanged'})
        else:
            self.template_name="account/partials/user-form.html"
            return render(request, self.template_name,context)


class GroupDetailView(PermissionRequiredMixin,View):
    permission_required = ('users.manage_user',)

    def get(self, request, pk):
        display=request.GET.get('display','page')
        role = get_object_or_404(Group,pk=pk)
        context={
            'role':role,
            'form':UserRoleForm(instance=role)
        }
        self.template_name="account/partials/user-role-form.html"
        if display=='modal':
            self.template_name="account/partials/user-modal.html"
        return render(request, self.template_name,context)
    def post(self, request, pk):
        role = Group.objects.get(pk=pk)
        context={'role':role,}
        form =UserRoleForm(request.POST,request.FILES,instance=role)
        if form.is_valid():
            form.save()
            return HttpResponse(status=204,headers={'HX-Trigger':'userListChanged'})
        else:
            context['form']=form
            self.template_name="account/partials/user-role-form.html"
        return render(request, self.template_name,context)


class UsersView(PermissionRequiredMixin,View):
    permission_required = ('users.manage_user',)
    template_name="account/users.html"
    filter_class=UsersFilter

    def get(self,request):
        context={'page_title':"User"}
        status=self.request.GET.get('is_active', 1)
        perm=self.request.GET.get('permission', None)
        notme=self.request.GET.get('notme', None)
        filter=self.request.GET.get('filter', None)
        model=self.request.GET.get('model', None)
        model_id=self.request.GET.get('model_id', None)
        display=self.request.GET.get('display', 'all')
        if 'action' in request.GET and request.GET['action']=='get-form':
            context['form']=AddUserForm()
            self.template_name="account/partials/user-form.html"
            return render(request, self.template_name,context)
        users=User.objects.filter(is_active=status,is_employee=False).prefetch_related('department')

        if perm is not None:
            # Filter by the user specified permissions
            users=users.filter(Q(is_superuser=True) | Q(user_permissions__codename__in=[perm])|Q(groups__permissions__codename__in=[perm])).distinct()
        if notme is not None:
            # Remove the current logged in user from the list
            users=users.filter(is_active=status).exclude(id__in=[request.user.id])
        users=self.filter_class(request.GET,users).qs
        # users=users.defer('password')
        values_list=['id','first_name','last_name','username','email','is_active','is_superuser','department__name','phone','designation','dob','gender','nin','marital_status']
        if display=='summary':
            values_list=['id','first_name','last_name','email','is_active','is_superuser','department__name','phone']
        context['users']=users
        context['list']=users.values(*values_list)
        if request.htmx:
            self.template_name="account/partials/users-list.html"
        return render(request, self.template_name,context)

    def post(self, request, format=None):
        form=AddUserForm(request.POST,request.FILES)
        context={'form':form,'page_title':"User"}
        if form.is_valid():
            form.save()
            return HttpResponse(status=204,headers={'HX-Trigger':'userListChanged'})
        else:
            self.template_name="account/partials/user-form.html"
            return render(request, self.template_name,context)


class UserDetailView(LoginRequiredMixin,View):
    template_name="account/user.html"
    
    def get(self,request,pk):
        action=request.GET.get('action',None)
        display=request.GET.get('display','page')
        user = get_object_or_404(User,pk=pk)
        context={
            'profile':user,
            'member':user,'page_title':"User"
        }
        if action=='get-form':
            context['form']=AddUserForm(instance=user,initial={'pop-password':True})
            self.template_name="account/partials/user-form.html"
        elif action=='get-password-reset-form':
            if user==request.user or request.user.has_perm('users.manage_user'):
                context['action']='reset-password'
                context['form']=CustomResetPasswordKeyForm()
                save_log("%s requested password reset form for %s"%(request.user,user))
            self.template_name="account/partials/password-reset-form.html"
        elif action=='get-signature-reset-form':
            if user==request.user or request.user.has_perm('users.manage_user'):
                context['action']='reset-signature'
                context['form']=UserSignatureForm(instance=user)
                # save_log("%s requested password reset form for %s"%(request.user,user))
            self.template_name="account/partials/password-reset-form.html"
        if display=='modal':
            payrollTermsList = [
                { "key": "allowances", "icon": "fa fa-arrow-up", "title": "Allowances" },
                { "key": "deductions", "icon": "fa fa-arrow-down", "title": "Deductions" },
                { "key": "taxes", "icon": "fa fa-arrow-down", "title": "Taxes" }
            ]
            context['payrollTermsList']=payrollTermsList
            # next_user=User.get_next_by_username(user)
            # print(next_user)
            self.template_name="account/partials/user-modal.html"
        return render(request, self.template_name,context)

    def post(self, request, pk):
        action=request.GET.get('action',None)
        user = User.objects.get(pk=pk)
        context={
            'profile':user,
            'member':user,
            'page_title':"User"
        }
        if action=='reset-password':
            form =CustomResetPasswordKeyForm(request.POST,instance=user)
            if form.is_valid():
                form.save()
                save_log("%s changed password for %s"%(request.user,user))
                return HttpResponse("<div class='alert alert-success'>Password reset successfully</div>")
            else:
                context['form']=form
                self.template_name="account/partials/password-reset-form.html"
        elif action=='reset-signature':
            form =UserSignatureForm(request.POST,request.FILES,instance=user)
            if form.is_valid():
                form.save()
                return HttpResponse("<div class='alert alert-success'>Signature reset successfully</div>")
            else:
                context['form']=form
                self.template_name="account/partials/password-reset-form.html"
        else:
            form =AddUserForm(request.POST,request.FILES,instance=user,initial={'pop-password':True})
            if form.is_valid():
                form.save()
                print("User saved")
                # save_log("%s changed data for for %s"%(request.user,user))
                return HttpResponse(status=204,headers={'HX-Trigger':'userListChanged'})
            else:
                print(form.errors)
                context['form']=form
                self.template_name="account/partials/user-form.html"
        return render(request, self.template_name,context)
        
    def delete(self, request, pk):
        user =User.objects.get(pk=pk)
        user.is_active=False
        user.save()
        return HttpResponse(status=204,headers={'HX-Trigger':'userListChanged'})


class NotificationList(View):
    template_name="core/partials/notifications.html"
    def get(self,request, *args, **kwargs):
        notifications=[]
        if request.user.is_authenticated:
            notifications = Notification.objects.filter(recipient=self.request.user).order_by('-created_at')
        context={'list':notifications}
        return render(request,self.template_name,context)

    def post(self, request, *args, **kwargs):  # Mark all as read
        Notification.objects.filter(
            recipient=self.request.user, unread=True).update(unread=False)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ClientLogin(View):
    def post(self,request,*args,**kwargs):
        email=request.POST.get("email",None)
        password=request.POST.get("password",None)
        if email and password:
            user=authenticate(username=email,password=password)
            if user and user is not None:
                login(request, user)
                return HttpResponseRedirect(reverse("home"))
        return redirect(reverse('account_login'))

class EmployeeLogin(View):
    def post(self,request,*args,**kwargs):
        employee_number=request.POST.get("employee_number",None)
        if employee_number:
            user=authenticate(username=employee_number)
            if user and user is not None:
                login(request, user)
                return HttpResponseRedirect(reverse("home"))
        return redirect(reverse('account_login'))


class EmployeesView(PermissionRequiredMixin,View):
    permission_required = ('users.view_employee',)
    template_name="hr/employees/index.html"
    filter_class=UsersFilter
    form_class=EmployeeForm

    def get(self,request):
        context={'page_title':"Employee"}
        status=self.request.GET.get('is_active', 1)
        display=self.request.GET.get('display', 'all')
        if 'action' in request.GET and request.GET['action']=='get-form':
            context['form']=self.form_class(initial={'is_employee':True})
            self.template_name="account/partials/employee-form.html"
            return render(request, self.template_name,context)
        users=User.objects.filter(is_active=status,is_employee=True).prefetch_related('department').prefetch_related('groups')

        users=self.filter_class(request.GET,users).qs
        # users=users.defer('password')
        values_list=['id','employee_number','first_name','last_name','email','is_active','phone','designation','dob','gender','date_joined','nin','marital_status','bank__name','branch_location','account_name','account_number','nssf_number','tin','date_terminated']
        if display=='summary':
            values_list=['id','first_name','last_name','email','is_active','phone','date_joined','date_terminated']
        context['users']=users
        context['list']=users.values(*values_list)
        if request.htmx:
            self.template_name="hr/partials/employees-list.html"
        return render(request, self.template_name,context)

    def post(self, request, format=None):
        form=self.form_class(request.POST,request.FILES)
        context={'form':form,'page_title':"Employee"}
        if form.is_valid():
            form.save()
            return HttpResponse(status=204,headers={'HX-Trigger':'userListChanged'})
        else:
            self.template_name="account/partials/employee-form.html"
            return render(request, self.template_name,context)

class EmployeeDetailView(LoginRequiredMixin,View):
    template_name="account/user.html"
    form_class=EmployeeForm
    
    def get(self,request,pk):
        action=request.GET.get('action',None)
        display=request.GET.get('display','page')
        user = get_object_or_404(User,pk=pk)
        context={
            'profile':user,
            'member':user,'page_title':"Employee"
        }
        if action=='get-form':
            context['form']=self.form_class(instance=user,initial={'pop-password':True})
            self.template_name="account/partials/employee-form.html"
        elif action=='get-password-reset-form':
            if user==request.user or request.user.has_perm('users.manage_user'):
                context['action']='reset-password'
                context['form']=CustomResetPasswordKeyForm()
                save_log("%s requested password reset form for %s"%(request.user,user))
            self.template_name="account/partials/password-reset-form.html"
        elif action=='get-signature-reset-form':
            if user==request.user or request.user.has_perm('users.manage_user'):
                context['action']='reset-signature'
                context['form']=UserSignatureForm(instance=user)
            self.template_name="account/partials/password-reset-form.html"
        elif action=='get-termination-form':
            if request.user.has_perm('users.manage_user'):
                context['form']=EmployeeTerminationForm(instance=user,initial={'is_active':False})
                self.template_name="account/partials/termination-form.html"
        if display=='modal':
            payrollTermsList = [
                { "key": "allowances", "icon": "fa fa-arrow-up", "title": "Allowances" },
                { "key": "deductions", "icon": "fa fa-arrow-down", "title": "Deductions" },
                { "key": "taxes", "icon": "fa fa-arrow-down", "title": "Taxes" }
            ]
            context['payrollTermsList']=payrollTermsList
            # next_user=User.get_next_by_username(user)
            # print(next_user)
            self.template_name="account/partials/user-modal.html"
        return render(request, self.template_name,context)

    def post(self, request, pk):
        action=request.GET.get('action',None)
        user = User.objects.get(pk=pk)
        context={
            'profile':user,
            'member':user,
            'page_title':"User"
        }
        if action=='reset-password':
            form =CustomResetPasswordKeyForm(request.POST,instance=user)
            if form.is_valid():
                form.save()
                save_log("%s changed password for %s"%(request.user,user))
                return HttpResponse("<div class='alert alert-success'>Password reset successfully</div>")
            else:
                context['form']=form
                self.template_name="account/partials/password-reset-form.html"
        elif action=='reset-signature':
            form =UserSignatureForm(request.POST,request.FILES,instance=user)
            if form.is_valid():
                form.save()
                return HttpResponse("<div class='alert alert-success'>Signature reset successfully</div>")
            else:
                context['form']=form
                self.template_name="account/partials/password-reset-form.html"
        elif action=="terminate":
            form =EmployeeTerminationForm(request.POST,request.FILES,instance=user)
            if form.is_valid():
                user=form.save()
                user.is_active=False
                user.save()
                return HttpResponse(status=204,headers={'HX-Trigger':'userListChanged'})
            else:
                context['form']=form
                self.template_name="account/partials/termination-form.html"
        else:
            form =self.form_class(request.POST,request.FILES,instance=user,initial={'pop-password':True})
            if form.is_valid():
                form.save()
                # save_log("%s changed data for for %s"%(request.user,user))
                return HttpResponse(status=204,headers={'HX-Trigger':'userListChanged'})
            else:
                context['form']=form
                self.template_name="account/partials/employee-form.html"
        return render(request, self.template_name,context)
        
    def delete(self, request, pk):
        user =User.objects.get(pk=pk)
        user.is_active=False
        user.save()
        return HttpResponse(status=204,headers={'HX-Trigger':'userListChanged'})

