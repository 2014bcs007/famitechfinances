from django.contrib import admin
from .models import *

# Register your models here.
class ChartOfAccountAdmin(admin.ModelAdmin):
    list_display=['title','code','account_type','status','parent']
    # list_display=[field.name for field in ChartOfAccount._meta.get_fields()]

admin.site.register(ChartOfAccount,ChartOfAccountAdmin)