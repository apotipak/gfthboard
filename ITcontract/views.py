import sys
from django.utils import timezone
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from leave.models import LeavePlan, LeaveHoliday, LeaveEmployee, LeaveType
from .models import ITcontractDB
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.timezone import localtime
from datetime import datetime
from django.conf import settings
from django.http import HttpResponse
from django.views import generic
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.contrib.auth.models import User, Group
from datetime import timedelta, datetime
from django.db.models import Sum
from django.utils.dateparse import parse_datetime
from django.http import JsonResponse
from post_office import mail
from page.rules import *
from django.core.files.storage import FileSystemStorage
from django.utils import translation
from django.core import serializers
import collections
from django.utils.timezone import now
import json
from django.utils.translation import ugettext as _
from django.db.models import CharField, Value


current_year = datetime.now().year

@login_required(login_url='/accounts/login/')
def ITcontractPolicy(request):
    username = request.user.username
    user_language = getDefaultLanguage(request.user.username)
    translation.activate(user_language)
    page_title = settings.PROJECT_NAME
    db_server = settings.DATABASES['default']['HOST']
    project_name = settings.PROJECT_NAME
    project_version = settings.PROJECT_VERSION    
    today_date = getDateFormatDisplay(user_language)
    
    ITcontractPolicy = ITcontractDB.ITcontractPolicy(request)        
    if user_language == "th":
        username_display = LeaveEmployee.objects.filter(emp_id=request.user.username).values_list('emp_fname_th', flat=True).get()
    else:
        username_display = LeaveEmployee.objects.filter(emp_id=request.user.username).values_list('emp_fname_en', flat=True).get()

    return render(request,
        'ITcontract/ITcontract_policy.html', {
        'page_title': settings.PROJECT_NAME,
        'today_date': today_date,
        'project_version': settings.PROJECT_VERSION,
        'db_server': settings.DATABASES['default']['HOST'],
        'project_name': settings.PROJECT_NAME,
        'user_language': user_language,
        'username_display': username_display,
        'ITcontractPolicy':  ITcontractPolicy,
    })


@permission_required('ITcontract.view_itcontractdb', login_url='/accounts/login/')
def ajax_get_it_contract_item(request):
    it_contract_id = request.POST.get("id")   
    record = {}
    itcontract_list = []
    is_error = True
    error_message = ""
    dept = ""
    vendor = ""
    description = ""
    start_date = ""
    end_date = ""

    if it_contract_id is not None:
        itcontract = ITcontractDB.objects.filter(pk=it_contract_id).get()
        if itcontract is not None:
            error_message = ""
            dept = itcontract.dept
            vendor = itcontract.vendor
            description = itcontract.description
            start_date = itcontract.start_date.strftime("%d/%m/%Y")
            end_date = itcontract.end_date.strftime("%d/%m/%Y")
            is_error = False
            error_message = ""
        else:
            error_message = "Not found"
    else:
        error_message = "Not found"

    response = JsonResponse(data={
        "success": True,
        "is_error": is_error,
        "error_message": error_message,
        "it_contract_id": it_contract_id,
        "dept": dept,
        "vendor": vendor,
        "description": description,
        "start_date": start_date,
        "end_date": end_date,        
    })

    response.status_code = 200
    return response



@permission_required('ITcontract.change_itcontractdb', login_url='/accounts/login/')
def ajax_save_it_contract_item(request):
    
    is_error = True
    message = ""

    it_contract_id = request.POST.get("it_contract_id")
    dept = request.POST.get("dept")
    vendor = request.POST.get("vendor")
    description = request.POST.get("description")
    start_date = request.POST.get("start_date")
    end_date = request.POST.get("end_date")

    print(it_contract_id, dept, vendor, description, start_date, end_date)

    if it_contract_id is not None:
        itcontract = ITcontractDB.objects.filter(pk=it_contract_id).get()
        if itcontract is not None:
            
            print("update")            
            itcontract.dept = dept
            itcontract.save()

            is_error = False;
            message = "ทำรายการสำเร็จ"
        else:
            message = "Error"
    else:
        message = "Error"

    response = JsonResponse(data={
        "success": True,
        "is_error": is_error,
        "message": message,
    })

    response.status_code = 200
    return response