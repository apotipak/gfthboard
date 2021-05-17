import sys
from django.utils import timezone
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required
from django.urls import reverse_lazy
from .models import PrpoCompany
from leave.models import LeaveEmployee
from django.http import HttpResponseRedirect
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
from page.rules import *
from django.core.files.storage import FileSystemStorage
from django.utils import translation
from django.core import serializers
import collections
from django.utils.timezone import now
import json
from django.utils.translation import ugettext as _
from django.db.models import CharField, Value
import django.db as db
from django.db import connection

excluded_username = {}
current_year = datetime.now().year

@login_required(login_url='/accounts/login/')
def welcome(request):
    user_language = getDefaultLanguage(request.user.username)
    translation.activate(user_language)
    page_title = settings.PROJECT_NAME
    db_server = settings.DATABASES['default']['HOST']
    project_name = settings.PROJECT_NAME
    project_version = settings.PROJECT_VERSION    
    today_date = getDateFormatDisplay(user_language)
    username = request.user.username

    if user_language == "th":
        username_display = LeaveEmployee.objects.filter(emp_id=request.user.username).values_list('emp_fname_th', flat=True).get()
    else:
        username_display = LeaveEmployee.objects.filter(emp_id=request.user.username).values_list('emp_fname_en', flat=True).get()        
                       
    return render(request,
        'prpo/welcome.html', {
        'page_title': settings.PROJECT_NAME,
        'today_date': today_date,
        'project_version': settings.PROJECT_VERSION,
        'db_server': settings.DATABASES['default']['HOST'],
        'project_name': settings.PROJECT_NAME,
        'user_language': user_language,
        'username_display': username_display,
    })


@login_required(login_url='/accounts/login/')
def currency(request):
    user_language = getDefaultLanguage(request.user.username)
    translation.activate(user_language)
    page_title = settings.PROJECT_NAME
    db_server = settings.DATABASES['default']['HOST']
    project_name = settings.PROJECT_NAME
    project_version = settings.PROJECT_VERSION    
    today_date = getDateFormatDisplay(user_language)
    username = request.user.username

    if user_language == "th":
        username_display = LeaveEmployee.objects.filter(emp_id=request.user.username).values_list('emp_fname_th', flat=True).get()
    else:
        username_display = LeaveEmployee.objects.filter(emp_id=request.user.username).values_list('emp_fname_en', flat=True).get()        
                       
    return render(request,
        'prpo/currency.html', {
        'page_title': settings.PROJECT_NAME,
        'today_date': today_date,
        'project_version': settings.PROJECT_VERSION,
        'db_server': settings.DATABASES['default']['HOST'],
        'project_name': settings.PROJECT_NAME,
        'user_language': user_language,
        'username_display': username_display,
    })


@login_required(login_url='/accounts/login/')
def company_list(request):
    user_language = getDefaultLanguage(request.user.username)
    translation.activate(user_language)
    page_title = settings.PROJECT_NAME
    db_server = settings.DATABASES['default']['HOST']
    project_name = settings.PROJECT_NAME
    project_version = settings.PROJECT_VERSION
    today_date = getDateFormatDisplay(user_language)
    username = request.user.username

    sql = "select cpid,cpnumber,cpcountry,cpname,cpshortcut,cpaltername,cpaddress,cpalteraddr, ";
    sql += "cptel,cpfax,cpcurrency,cplogo,cpponotes,cpvpflag,cpverifypercent,cpvvflag,cpverifyapprover, ";
    sql += "cpprmaxid,cppomaxid,fldremainnum,fldremainchar1,fldremainchar2,opuser,optime ";
    sql += " from prpo_company order by cpid;";

    try:
        cursor = connection.cursor()
        cursor.execute(sql)
        prpocompany_instance = cursor.fetchall()
    except db.OperationalError as e:
        is_error = True
        error_message = "<b>Error: please send this error to IT team</b><br>" + str(e)
    except db.Error as e:
        is_error = True
        error_message = "<b>Error: please send this error to IT team</b><br>" + str(e)
    finally:
        cursor.close()
        
    if user_language == "th":
        username_display = LeaveEmployee.objects.filter(emp_id=request.user.username).values_list('emp_fname_th', flat=True).get()
    else:
        username_display = LeaveEmployee.objects.filter(emp_id=request.user.username).values_list('emp_fname_en', flat=True).get()

    return render(request,
        'prpo/company_list.html', {
        'page_title': settings.PROJECT_NAME,
        'today_date': today_date,
        'project_version': settings.PROJECT_VERSION,
        'db_server': settings.DATABASES['default']['HOST'],
        'project_name': settings.PROJECT_NAME,
        'user_language': user_language,
        'username_display': username_display,
        'prpo_company_list':  list(prpocompany_instance),
    })

@login_required(login_url='/accounts/login/')
def ajax_save_company(request):
    is_error = True
    error_message = "Error"
    company_title = ""

    updated_by = request.user.username    
    company_id = request.POST.get('company_id')
    company_name_en = request.POST.get('company_name_en')
    company_name_th = request.POST.get('company_name_th')
    company_address = request.POST.get('company_address') 
    company_telephone = request.POST.get('company_telephone')
    company_fax = request.POST.get('company_fax')
    print(updated_by, company_id)

    if company_id is not None:
        try:
            company = PrpoCompany.objects.filter(pk=company_id).get()
            company.cpname = company_name_en
            company.cpaltername = company_name_th
            company.cpaddress = company_address
            company.cptel = company_telephone
            company.cpfax = company_fax
            company.optime = datetime.now()
            company.save()  
            
            company_title = company_name_en
            is_error = False
            error_message = "บันทึกรายการสำเร็จ"
        except db.OperationalError as e:
            is_error = True
            error_message = str(e)
        except db.Error as e:
            is_error = True
            error_message = str(e)        
        except Exception as e:            
            is_error = True
            error_message = str(e)
    else:
        is_error = True
        error_message = "ไม่พบข้อมูลบริษัทที่ต้องการแก้ไข"

    response = JsonResponse(data={
        "success": True,
        "is_error": is_error,
        "error_message": error_message,
        "company_title": company_title,
    })

    response.status_code = 200
    return response


@login_required(login_url='/accounts/login/')
def company_manage(request):
    company_id = request.POST.get('company_id')
    user_language = getDefaultLanguage(request.user.username)
    translation.activate(user_language)
    page_title = settings.PROJECT_NAME
    db_server = settings.DATABASES['default']['HOST']
    project_name = settings.PROJECT_NAME
    project_version = settings.PROJECT_VERSION
    today_date = getDateFormatDisplay(user_language)
    username = request.user.username

    if user_language == "th":
        username_display = LeaveEmployee.objects.filter(emp_id=request.user.username).values_list('emp_fname_th', flat=True).get()
    else:
        username_display = LeaveEmployee.objects.filter(emp_id=request.user.username).values_list('emp_fname_en', flat=True).get()

    if company_id is None:
        return render(request,
            'prpo/company_manage.html', {
            'page_title': settings.PROJECT_NAME,
            'today_date': today_date,
            'project_version': settings.PROJECT_VERSION,
            'db_server': settings.DATABASES['default']['HOST'],
            'project_name': settings.PROJECT_NAME,
            'user_language': user_language,
            'username_display': username_display,
            'prpo_company_list': None,
            'company_id': None,
        })
    else:        
        sql = "select cpid,cpnumber,cpcountry,cpname,cpshortcut,cpaltername,cpaddress,cpalteraddr, ";
        sql += "cptel,cpfax,cpcurrency,cplogo,cpponotes,cpvpflag,cpverifypercent,cpvvflag,cpverifyapprover, ";
        sql += "cpprmaxid,cppomaxid,fldremainnum,fldremainchar1,fldremainchar2,opuser,optime ";
        sql += "from prpo_company "
        sql += "where cpid=" + str(company_id + " ")
        sql += "order by cpid;";

        try:
            cursor = connection.cursor()
            prpocompany_instance = cursor.execute(sql)
            prpocompany_instance = cursor.fetchone()
        except db.OperationalError as e:
            is_error = True
            error_message = "<b>Error: please send this error to IT team</b><br>" + str(e)
        except db.Error as e:
            is_error = True
            error_message = "<b>Error: please send this error to IT team</b><br>" + str(e)
        finally:
            cursor.close()
            
        return render(request,
            'prpo/company_manage.html', {
            'page_title': settings.PROJECT_NAME,
            'today_date': today_date,
            'project_version': settings.PROJECT_VERSION,
            'db_server': settings.DATABASES['default']['HOST'],
            'project_name': settings.PROJECT_NAME,
            'user_language': user_language,
            'username_display': username_display,
            'prpo_company_list':  list(prpocompany_instance),
            'company_id': company_id,
        })


@login_required(login_url='/accounts/login/')
def department(request):
    user_language = getDefaultLanguage(request.user.username)
    translation.activate(user_language)
    page_title = settings.PROJECT_NAME
    db_server = settings.DATABASES['default']['HOST']
    project_name = settings.PROJECT_NAME
    project_version = settings.PROJECT_VERSION    
    today_date = getDateFormatDisplay(user_language)
    username = request.user.username

    if user_language == "th":
        username_display = LeaveEmployee.objects.filter(emp_id=request.user.username).values_list('emp_fname_th', flat=True).get()
    else:
        username_display = LeaveEmployee.objects.filter(emp_id=request.user.username).values_list('emp_fname_en', flat=True).get()        
                       
    return render(request,
        'prpo/department.html', {
        'page_title': settings.PROJECT_NAME,
        'today_date': today_date,
        'project_version': settings.PROJECT_VERSION,
        'db_server': settings.DATABASES['default']['HOST'],
        'project_name': settings.PROJECT_NAME,
        'user_language': user_language,
        'username_display': username_display,
    })


@login_required(login_url='/accounts/login/')
def category(request):
    user_language = getDefaultLanguage(request.user.username)
    translation.activate(user_language)
    page_title = settings.PROJECT_NAME
    db_server = settings.DATABASES['default']['HOST']
    project_name = settings.PROJECT_NAME
    project_version = settings.PROJECT_VERSION    
    today_date = getDateFormatDisplay(user_language)
    username = request.user.username

    if user_language == "th":
        username_display = LeaveEmployee.objects.filter(emp_id=request.user.username).values_list('emp_fname_th', flat=True).get()
    else:
        username_display = LeaveEmployee.objects.filter(emp_id=request.user.username).values_list('emp_fname_en', flat=True).get()        
                       
    return render(request,
        'prpo/category.html', {
        'page_title': settings.PROJECT_NAME,
        'today_date': today_date,
        'project_version': settings.PROJECT_VERSION,
        'db_server': settings.DATABASES['default']['HOST'],
        'project_name': settings.PROJECT_NAME,
        'user_language': user_language,
        'username_display': username_display,
    })


@login_required(login_url='/accounts/login/')
def item(request):
    user_language = getDefaultLanguage(request.user.username)
    translation.activate(user_language)
    page_title = settings.PROJECT_NAME
    db_server = settings.DATABASES['default']['HOST']
    project_name = settings.PROJECT_NAME
    project_version = settings.PROJECT_VERSION    
    today_date = getDateFormatDisplay(user_language)
    username = request.user.username

    if user_language == "th":
        username_display = LeaveEmployee.objects.filter(emp_id=request.user.username).values_list('emp_fname_th', flat=True).get()
    else:
        username_display = LeaveEmployee.objects.filter(emp_id=request.user.username).values_list('emp_fname_en', flat=True).get()        
                       
    return render(request,
        'prpo/item.html', {
        'page_title': settings.PROJECT_NAME,
        'today_date': today_date,
        'project_version': settings.PROJECT_VERSION,
        'db_server': settings.DATABASES['default']['HOST'],
        'project_name': settings.PROJECT_NAME,
        'user_language': user_language,
        'username_display': username_display,
    })


@login_required(login_url='/accounts/login/')
def vendor(request):
    user_language = getDefaultLanguage(request.user.username)
    translation.activate(user_language)
    page_title = settings.PROJECT_NAME
    db_server = settings.DATABASES['default']['HOST']
    project_name = settings.PROJECT_NAME
    project_version = settings.PROJECT_VERSION    
    today_date = getDateFormatDisplay(user_language)
    username = request.user.username

    if user_language == "th":
        username_display = LeaveEmployee.objects.filter(emp_id=request.user.username).values_list('emp_fname_th', flat=True).get()
    else:
        username_display = LeaveEmployee.objects.filter(emp_id=request.user.username).values_list('emp_fname_en', flat=True).get()        
                       
    return render(request,
        'prpo/vendor.html', {
        'page_title': settings.PROJECT_NAME,
        'today_date': today_date,
        'project_version': settings.PROJECT_VERSION,
        'db_server': settings.DATABASES['default']['HOST'],
        'project_name': settings.PROJECT_NAME,
        'user_language': user_language,
        'username_display': username_display,
    })


@login_required(login_url='/accounts/login/')
def user(request):
    user_language = getDefaultLanguage(request.user.username)
    translation.activate(user_language)
    page_title = settings.PROJECT_NAME
    db_server = settings.DATABASES['default']['HOST']
    project_name = settings.PROJECT_NAME
    project_version = settings.PROJECT_VERSION    
    today_date = getDateFormatDisplay(user_language)
    username = request.user.username

    if user_language == "th":
        username_display = LeaveEmployee.objects.filter(emp_id=request.user.username).values_list('emp_fname_th', flat=True).get()
    else:
        username_display = LeaveEmployee.objects.filter(emp_id=request.user.username).values_list('emp_fname_en', flat=True).get()        
                       
    return render(request,
        'prpo/user.html', {
        'page_title': settings.PROJECT_NAME,
        'today_date': today_date,
        'project_version': settings.PROJECT_VERSION,
        'db_server': settings.DATABASES['default']['HOST'],
        'project_name': settings.PROJECT_NAME,
        'user_language': user_language,
        'username_display': username_display,
    })

@login_required(login_url='/accounts/login/')
def entry_inquiry(request):
    user_language = getDefaultLanguage(request.user.username)
    translation.activate(user_language)
    page_title = settings.PROJECT_NAME
    db_server = settings.DATABASES['default']['HOST']
    project_name = settings.PROJECT_NAME
    project_version = settings.PROJECT_VERSION    
    today_date = getDateFormatDisplay(user_language)
    username = request.user.username

    if user_language == "th":
        username_display = LeaveEmployee.objects.filter(emp_id=request.user.username).values_list('emp_fname_th', flat=True).get()
    else:
        username_display = LeaveEmployee.objects.filter(emp_id=request.user.username).values_list('emp_fname_en', flat=True).get()        
                       
    return render(request,
        'prpo/entry_inquiry.html', {
        'page_title': settings.PROJECT_NAME,
        'today_date': today_date,
        'project_version': settings.PROJECT_VERSION,
        'db_server': settings.DATABASES['default']['HOST'],
        'project_name': settings.PROJECT_NAME,
        'user_language': user_language,
        'username_display': username_display,
    })

@login_required(login_url='/accounts/login/')
def pr_inbox(request):
    user_language = getDefaultLanguage(request.user.username)
    translation.activate(user_language)
    page_title = settings.PROJECT_NAME
    db_server = settings.DATABASES['default']['HOST']
    project_name = settings.PROJECT_NAME
    project_version = settings.PROJECT_VERSION    
    today_date = getDateFormatDisplay(user_language)
    username = request.user.username

    if user_language == "th":
        username_display = LeaveEmployee.objects.filter(emp_id=request.user.username).values_list('emp_fname_th', flat=True).get()
    else:
        username_display = LeaveEmployee.objects.filter(emp_id=request.user.username).values_list('emp_fname_en', flat=True).get()        
                       
    return render(request,
        'prpo/pr_inbox.html', {
        'page_title': settings.PROJECT_NAME,
        'today_date': today_date,
        'project_version': settings.PROJECT_VERSION,
        'db_server': settings.DATABASES['default']['HOST'],
        'project_name': settings.PROJECT_NAME,
        'user_language': user_language,
        'username_display': username_display,
    })

@login_required(login_url='/accounts/login/')
def po_inbox(request):
    user_language = getDefaultLanguage(request.user.username)
    translation.activate(user_language)
    page_title = settings.PROJECT_NAME
    db_server = settings.DATABASES['default']['HOST']
    project_name = settings.PROJECT_NAME
    project_version = settings.PROJECT_VERSION    
    today_date = getDateFormatDisplay(user_language)
    username = request.user.username

    if user_language == "th":
        username_display = LeaveEmployee.objects.filter(emp_id=request.user.username).values_list('emp_fname_th', flat=True).get()
    else:
        username_display = LeaveEmployee.objects.filter(emp_id=request.user.username).values_list('emp_fname_en', flat=True).get()        
                       
    return render(request,
        'prpo/po_inbox.html', {
        'page_title': settings.PROJECT_NAME,
        'today_date': today_date,
        'project_version': settings.PROJECT_VERSION,
        'db_server': settings.DATABASES['default']['HOST'],
        'project_name': settings.PROJECT_NAME,
        'user_language': user_language,
        'username_display': username_display,
    })
