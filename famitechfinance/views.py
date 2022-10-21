from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from todolist.models import Task
from django.contrib import messages
from django.core.paginator import Paginator
import json
from django.http import JsonResponse,HttpResponse
import datetime
import csv
import xlwt
from weasyprint import HTML, CSS
# from weasyprint.text.fonts import FontConfiguration
from django.template.loader import render_to_string
from django.views.generic import TemplateView

import tempfile
from django.db.models import Sum
# Create your views here.
class Dashboard(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        tasks=Task.objects.filter(is_active=True)
        recent_tasks=tasks.order_by('-created_at')[:3]
        # category_count = get_category_count()
        # most_recent = Post.objects.order_by('-timestamp')[:3]
        context = super().get_context_data(**kwargs)
        tasksContext=[
            {"title":"Today's Tasks","key":"todays-tasks","tasks":tasks.filter(startdate=datetime.date.today())},
            {"title":"Pending Tasks","key":"pending-tasks","tasks":tasks.filter(completed=False)},
            {"title":"Recent Tasks","key":"recent-tasks","tasks":recent_tasks},
        ]
        context['recent_tasks'] = recent_tasks
        context['todays_tasks'] = tasks.filter(startdate=datetime.date.today())
        context['pending_tasks'] = tasks.filter(completed=False)
        context['tasks'] = tasksContext
        context['page_request_var'] = "page"
        # context['category_count'] = category_count
        # context['form'] = self.form
        return context
