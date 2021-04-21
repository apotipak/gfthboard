from django.shortcuts import render
from django.utils import timezone
from datetime import datetime
from django.conf import settings
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required
from django.utils import translation
from django.utils.translation import ugettext as _
from django.db import connection
from django.db.models import Sum
from page.rules import *
from django.utils import timezone
from leave.models import LeaveEmployee
from django.http import JsonResponse
from django.forms.models import model_to_dict
import django.db as db


@permission_required('employeem1.can_access_employee_m1', login_url='/accounts/login/')
def EmployeeM1Dashboard(request):
    user_language = getDefaultLanguage(request.user.username)
    translation.activate(user_language)
    render_template_name = 'employeem1/dashboard.html'

    dattime_format = "%Y-%m-%d %H:%M:%S"

    page_title = settings.PROJECT_NAME
    db_server = settings.DATABASES['default']['HOST']
    project_name = settings.PROJECT_NAME
    project_version = settings.PROJECT_VERSION
    today_date = getDateFormatDisplay(user_language)

    if user_language == "th":
        if request.user.username == "999999":
            username_display = request.user.first_name
        else:            
            username_display = LeaveEmployee.objects.filter(emp_id=request.user.username).values_list('emp_fname_th', flat=True).get()
    else:
        if request.user.username == "999999":
            username_display = request.user.first_name
        else:                    
            username_display = LeaveEmployee.objects.filter(emp_id=request.user.username).values_list('emp_fname_en', flat=True).get()

    return render(request, render_template_name, {
        'page_title': settings.PROJECT_NAME,
        'today_date': today_date,
        'project_version': settings.PROJECT_VERSION,
        'db_server': settings.DATABASES['default']['HOST'],
        'project_name': settings.PROJECT_NAME,
        'user_language': user_language,
        'username_display': username_display,
    })


@permission_required('employeem1.can_access_employee_m1_pay_slip', login_url='/accounts/login/')
def EmployeeM1PaySlip(request):
    user_language = getDefaultLanguage(request.user.username)
    translation.activate(user_language)
    render_template_name = 'employeem1/pay_slip.html'

    dattime_format = "%Y-%m-%d %H:%M:%S"

    page_title = settings.PROJECT_NAME
    db_server = settings.DATABASES['default']['HOST']
    project_name = settings.PROJECT_NAME
    project_version = settings.PROJECT_VERSION
    today_date = getDateFormatDisplay(user_language)

    if user_language == "th":
        if request.user.username == "999999":
            username_display = request.user.first_name
        else:            
            username_display = LeaveEmployee.objects.filter(emp_id=request.user.username).values_list('emp_fname_th', flat=True).get()
    else:
        if request.user.username == "999999":
            username_display = request.user.first_name
        else:                    
            username_display = LeaveEmployee.objects.filter(emp_id=request.user.username).values_list('emp_fname_en', flat=True).get()

    return render(request, render_template_name, {
        'page_title': settings.PROJECT_NAME,
        'today_date': today_date,
        'project_version': settings.PROJECT_VERSION,
        'db_server': settings.DATABASES['default']['HOST'],
        'project_name': settings.PROJECT_NAME,
        'user_language': user_language,
        'username_display': username_display,
    })
