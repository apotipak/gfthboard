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
from django.utils.translation import ugettext as _
from django.db.models import CharField, Value
from django.utils.timezone import now
from django.core.exceptions import ValidationError
import sys
import json
import django.db as db
import collections



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
    
    ITcontractList = ITcontractDB.objects.all()

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
        'ITcontractList':  ITcontractList,
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

            start_date = None if itcontract.start_date is None else itcontract.start_date.strftime("%d/%m/%Y")
            end_date = None if itcontract.end_date is None else itcontract.end_date.strftime("%d/%m/%Y")

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


@permission_required('ITcontract.add_itcontractdb', login_url='/accounts/login/')
def ajax_add_it_contract_item(request):    
    is_error = True
    message = ""

    dept = request.POST.get("dept")
    vendor = request.POST.get("vendor")
    description = request.POST.get("description")    
    start_date = datetime.strptime(request.POST.get("start_date"), "%d/%m/%Y").date()
    end_date = datetime.strptime(request.POST.get("end_date"), "%d/%m/%Y").date()

    print(dept, vendor, description, start_date, end_date)    

    record = {}
    refresh_it_contract_list = []    

    try:
        item = ITcontractDB(
            dept = dept,
            vendor = vendor,
            description = description,
            start_date = start_date,
            end_date = end_date
            )
        item.save()        

        is_error = False
        message = "ทำรายการสำเร็จ"
    except db.OperationalError as e:
        message = str(e)
    except db.Error as e:
        message = str(e)
    except Exception as e:                
        message = str(e)

    if not is_error:
        refresh_it_contract = ITcontractDB.objects.all()
        for item in refresh_it_contract:
            it_contract_id = item.id
            dept = item.dept
            vendor = item.vendor
            description = item.description
            start_date = item.start_date.strftime("%d/%m/%Y")
            end_date = item.end_date.strftime("%d/%m/%Y")                
            record = {
                "it_contract_id": it_contract_id,
                "dept": dept,
                "vendor": vendor,
                "description": description,
                "start_date": start_date,
                "end_date": end_date,
            }
            refresh_it_contract_list.append(record) 

        is_error = False
        message = "ทำรายการสำเร็จ"

    response = JsonResponse(data={
        "success": True,
        "is_error": is_error,
        "message": message,
        "refresh_it_contract_list": refresh_it_contract_list,
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
    
    start_date = datetime.strptime(request.POST.get("start_date"), "%d/%m/%Y").date()
    end_date = datetime.strptime(request.POST.get("end_date"), "%d/%m/%Y").date()

    print("START_DATE1 : ", start_date)

    record = {}
    refresh_it_contract_list = []    

    if it_contract_id is not None:
        itcontract = ITcontractDB.objects.filter(pk=it_contract_id).get()

        if itcontract is not None:
            
            itcontract.dept = dept
            itcontract.vendor = vendor
            itcontract.description = description            
            itcontract.start_date = start_date
            itcontract.end_date = end_date
                        
            try:
                itcontract.save()
                is_error = False
                message = "ทำรายการสำเร็จ"
            except db.OperationalError as e:
                message = str(e)
            except db.Error as e:
                message = str(e)
            except Exception as e:                
                message = str(e)

            if not is_error:
                refresh_it_contract = ITcontractDB.objects.all()
                for item in refresh_it_contract:
                    it_contract_id = item.id
                    dept = item.dept
                    vendor = item.vendor
                    description = item.description
                    start_date = item.start_date.strftime("%d/%m/%Y")
                    end_date = item.end_date.strftime("%d/%m/%Y")                
                    record = {
                        "it_contract_id": it_contract_id,
                        "dept": dept,
                        "vendor": vendor,
                        "description": description,
                        "start_date": start_date,
                        "end_date": end_date,
                    }
                    refresh_it_contract_list.append(record) 

                is_error = False
                message = "ทำรายการสำเร็จ"
        else:
            message = "Error"
    else:
        message = "Error"

    response = JsonResponse(data={
        "success": True,
        "is_error": is_error,
        "message": message,
        "refresh_it_contract_list": refresh_it_contract_list,
    })

    response.status_code = 200
    return response