from re import sub
import sys
from django.template.defaultfilters import last
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

    # get last login
    last_login = getLastLogin(request)

    return render(request,
        'prpo/welcome.html', {
        'page_title': settings.PROJECT_NAME,
        'today_date': today_date,
        'project_version': settings.PROJECT_VERSION,
        'db_server': settings.DATABASES['default']['HOST'],
        'project_name': settings.PROJECT_NAME,
        'user_language': user_language,
        'username_display': username_display,
        'last_login': last_login,
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

    # get last login
    last_login = getLastLogin(request)

    return render(request,
        'prpo/currency.html', {
        'page_title': settings.PROJECT_NAME,
        'today_date': today_date,
        'project_version': settings.PROJECT_VERSION,
        'db_server': settings.DATABASES['default']['HOST'],
        'project_name': settings.PROJECT_NAME,
        'user_language': user_language,
        'username_display': username_display,
        'last_login': last_login,
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

    # get last login
    last_login = getLastLogin(request)

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
        'last_login': last_login,
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

    # get last login
    last_login = getLastLogin(request)

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
            'last_login': last_login,
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
            'last_login': last_login,
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

    # get last login
    last_login = getLastLogin(request)

    return render(request,
        'prpo/department.html', {
        'page_title': settings.PROJECT_NAME,
        'today_date': today_date,
        'project_version': settings.PROJECT_VERSION,
        'db_server': settings.DATABASES['default']['HOST'],
        'project_name': settings.PROJECT_NAME,
        'user_language': user_language,
        'username_display': username_display,
        'last_login': last_login,
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

    # get last login
    last_login = getLastLogin(request)

    return render(request,
        'prpo/category.html', {
        'page_title': settings.PROJECT_NAME,
        'today_date': today_date,
        'project_version': settings.PROJECT_VERSION,
        'db_server': settings.DATABASES['default']['HOST'],
        'project_name': settings.PROJECT_NAME,
        'user_language': user_language,
        'username_display': username_display,
        'last_login': last_login,
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

    # get last login
    last_login = getLastLogin(request)

    return render(request,
        'prpo/item.html', {
        'page_title': settings.PROJECT_NAME,
        'today_date': today_date,
        'project_version': settings.PROJECT_VERSION,
        'db_server': settings.DATABASES['default']['HOST'],
        'project_name': settings.PROJECT_NAME,
        'user_language': user_language,
        'username_display': username_display,
        'last_login': last_login,
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

    # get last login
    last_login = getLastLogin(request)

    return render(request,
        'prpo/vendor.html', {
        'page_title': settings.PROJECT_NAME,
        'today_date': today_date,
        'project_version': settings.PROJECT_VERSION,
        'db_server': settings.DATABASES['default']['HOST'],
        'project_name': settings.PROJECT_NAME,
        'user_language': user_language,
        'username_display': username_display,
        'last_login': last_login,
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

    # get last login
    last_login = getLastLogin(request)

    return render(request,
        'prpo/user.html', {
        'page_title': settings.PROJECT_NAME,
        'today_date': today_date,
        'project_version': settings.PROJECT_VERSION,
        'db_server': settings.DATABASES['default']['HOST'],
        'project_name': settings.PROJECT_NAME,
        'user_language': user_language,
        'username_display': username_display,
        'last_login': last_login,
    })

@login_required(login_url='/accounts/login/')
def pr_entry_inquiry(request):
    user_language = getDefaultLanguage(request.user.username)
    translation.activate(user_language)
    page_title = settings.PROJECT_NAME
    db_server = settings.DATABASES['default']['HOST']
    project_name = settings.PROJECT_NAME
    project_version = settings.PROJECT_VERSION    
    today_date = getDateFormatDisplay(user_language)
    username = request.user.username
    is_manager = False

    if user_language == "th":
        username_display = LeaveEmployee.objects.filter(emp_id=request.user.username).values_list('emp_fname_th', flat=True).get()
    else:
        username_display = LeaveEmployee.objects.filter(emp_id=request.user.username).values_list('emp_fname_en', flat=True).get()        

    user_list = []
    department_list = []
    category_list = []
    pr_status_list = []
    record = {}

    # Get user list
    sql = "select dpid, dpname department_name from prpo_department order by dpname;"
    try:
        with connection.cursor() as cursor:     
            cursor.execute(sql)
            prpo_department_obj = cursor.fetchall()

        if prpo_department_obj is not None:
            for item in prpo_department_obj:
                dpid = item[0]
                dpname = item[1]
                record = {"dpid":dpid, "dpname":dpname}
                department_list.append(record)
    except db.OperationalError as e:
        is_error = True
        error_message = "Error message: " + str(e)
    except db.Error as e:
        is_error = True
        error_message = "Error message: " + str(e)
    finally:
        cursor.close()

            
    # Get department list
    sql = "select dpid, dpname department_name from prpo_department order by dpname;"
    try:
        with connection.cursor() as cursor:     
            cursor.execute(sql)
            prpo_department_obj = cursor.fetchall()

        if prpo_department_obj is not None:
            for item in prpo_department_obj:
                dpid = item[0]
                dpname = item[1]
                record = {"dpid":dpid, "dpname":dpname}
                department_list.append(record)
    except db.OperationalError as e:
        is_error = True
        error_message = "Error message: " + str(e)
    except db.Error as e:
        is_error = True
        error_message = "Error message: " + str(e)
    finally:
        cursor.close()

    # Get Category List
    sql = "select ctid, ctname category_name from PRPO_Category order by ctname;"
    try:
        with connection.cursor() as cursor:     
            cursor.execute(sql)
            prpo_category_obj = cursor.fetchall()
            
        if prpo_category_obj is not None:
            for item in prpo_category_obj:
                ctid = item[0]
                ctname = item[1]
                record = {"ctid":ctid, "ctname":ctname}
                category_list.append(record)
    except db.OperationalError as e:
        is_error = True
        error_message = "Error message: " + str(e)
    except db.Error as e:
        is_error = True
        error_message = "Error message: " + str(e)
    finally:
        cursor.close()

    # Get PR Status List    
    sql = "select stid status_id, stname from prpo_status where stID in (1,2,3,10,11,13) order by stid;"
    try:
        with connection.cursor() as cursor:     
            cursor.execute(sql)
            prpo_status_obj = cursor.fetchall()
            
        if prpo_status_obj is not None:
            for item in prpo_status_obj:
                stid = item[0]
                stname = item[1]
                record = {"stid":stid, "stname":stname}
                pr_status_list.append(record)
    except db.OperationalError as e:
        is_error = True
        error_message = "Error message: " + str(e)
    except db.Error as e:
        is_error = True
        error_message = "Error message: " + str(e)
    finally:
        cursor.close()    


    # Get User List
    sql = "select usid,usname from prpo_user;"
    try:
        with connection.cursor() as cursor:     
            cursor.execute(sql)
            user_obj = cursor.fetchall()

        if user_obj is not None:
            for item in user_obj:
                usid = item[0]
                usname = item[1]
                record = {"usid":usid, "usname":usname}
                user_list.append(record)
            is_error = False
            message = "Able to get user list."

    except db.OperationalError as e: 
        is_error = True
        message = "Error message: " + str(e)
    except db.Error as e:
        is_error = True
        message = "Error message: " + str(e)
    finally:
        cursor.close()


    # get last login
    last_login = getLastLogin(request)


    # check is manager
    sql = "select usID from PRPO_USER WHERE usSupervisor=" + str(username) + ";"
    print("SQL 11: ", sql)
    try:
        with connection.cursor() as cursor:     
            cursor.execute(sql)
            user_obj = cursor.fetchall()

        if len(user_obj) > 0:
            is_manager = True

    except db.OperationalError as e: 
        is_error = True
        message = "Error message: " + str(e)
    except db.Error as e:
        is_error = True
        message = "Error message: " + str(e)
    finally:
        cursor.close()


    return render(request,
        'prpo/pr_entry_inquiry.html', {
        'page_title': settings.PROJECT_NAME,
        'today_date': today_date,
        'project_version': settings.PROJECT_VERSION,
        'db_server': settings.DATABASES['default']['HOST'],
        'project_name': settings.PROJECT_NAME,
        'user_language': user_language,
        'username_display': username_display,
        'department_list': list(department_list),
        'category_list': list(category_list),
        'pr_status_list': list(pr_status_list),
        'user_list': list(user_list),
        'last_login': last_login,
        'is_manager': is_manager,
    })

 
def ajax_get_item_list_by_subcategory_id(request, *args, **kwargs):
    is_error = True
    message = ""
    subcategory_id = kwargs['subcategory_id']
    item_list = []
    record = {}    

    if subcategory_id=="" or subcategory_id is None:
        is_error = True
        message = "There is no Category ID provided."
    else:
        sql = "select itid, itName item_name, itdescription from prpo_item where itsubcategory=" + str(subcategory_id) + " order by itname;"
        try:
            with connection.cursor() as cursor:     
                cursor.execute(sql)
                prpo_item_obj = cursor.fetchall()

            if prpo_item_obj is not None:
                for item in prpo_item_obj:
                    itid = item[0]
                    itname = item[1]
                    itdescription = item[2]
                    item_short_description = itdescription[0:20]                    
                    record = {"itid":itid, "itname":itname, "itdescription":itdescription, "item_short_description":item_short_description}
                    item_list.append(record)
                is_error = False
                message = "Able to get item list."

        except db.OperationalError as e: 
            is_error = True
            message = "Error message: " + str(e)
        except db.Error as e:
            is_error = True
            message = "Error message: " + str(e)
        finally:
            cursor.close()
    
    response = JsonResponse(data={        
        "is_error": is_error,
        "message": message,
        "item_list": list(item_list),
    })
    
    response.status_code = 200
    return response


def ajax_get_subcategory_list(request, *args, **kwargs):
    is_error = True
    message = ""
    category_id = kwargs['category_id']
    subcategory_list = []
    record = {}

    print("category_id : ", category_id)

    if category_id=="" or category_id is None:
        is_error = True
        message = "There is no Category ID provided."
    else:
        sql = "select scid, scname subcategory_name from prpo_subcategory where sccategory=" + str(category_id) + " order by scname;"
        print("SQL get_subcat : ", sql)
        try:
            with connection.cursor() as cursor:     
                cursor.execute(sql)
                prpo_subcategory_obj = cursor.fetchall()

            if prpo_subcategory_obj is not None:
                for item in prpo_subcategory_obj:
                    scid = item[0]
                    scname = item[1]
                    record = {"scid":scid, "scname":scname}
                    subcategory_list.append(record)
                is_error = False
                message = "Able to get subcategory."

        except db.OperationalError as e:
            is_error = True
            message = "Error message: " + str(e)
        except db.Error as e:
            is_error = True
            message = "Error message: " + str(e)
        finally:
            cursor.close()
    
    response = JsonResponse(data={        
        "is_error": is_error,
        "message": message,
        "subcategory_list": list(subcategory_list),
    })
    
    response.status_code = 200
    return response


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

    # get last login
    last_login = getLastLogin(request)

    return render(request,
        'prpo/pr_inbox.html', {
        'page_title': settings.PROJECT_NAME,
        'today_date': today_date,
        'project_version': settings.PROJECT_VERSION,
        'db_server': settings.DATABASES['default']['HOST'],
        'project_name': settings.PROJECT_NAME,
        'user_language': user_language,
        'username_display': username_display,
        'last_login': last_login,
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

    # get last login
    last_login = getLastLogin(request)

    return render(request,
        'prpo/po_inbox.html', {
        'page_title': settings.PROJECT_NAME,
        'today_date': today_date,
        'project_version': settings.PROJECT_VERSION,
        'db_server': settings.DATABASES['default']['HOST'],
        'project_name': settings.PROJECT_NAME,
        'user_language': user_language,
        'username_display': username_display,
        'last_login': last_login,
    })



@login_required(login_url='/accounts/login/')
def ajax_pr_inquiry_list(request):
    print("*********************************")
    print("ajax_pr_inquiry_list() function")
    print("*********************************")

    is_error = True
    message = ""

    pr_number = request.POST.get("pr_number")
    user_id = request.POST.get("username_options")
    department_id = request.POST.get("department_options")
    category_id = request.POST.get("category_options")
    subcategory_id = request.POST.get("subcategory_options")
    item_id = request.POST.get("item_options")
    date_from = datetime.strptime(request.POST.get("date_from"), "%d/%m/%Y").date()
    date_to = datetime.strptime(request.POST.get("date_to"), "%d/%m/%Y").date()
    pr_status_id = request.POST.get("pr_status")
    pr_list_obj = []
    pr_list = []
    record = {}


    if user_id is None:
        user_id = request.user.username
        user_id = 522;

    print("pr_number : ", pr_number)
    print("user_id : ", user_id)
    print("department_id : ", department_id)
    print("category_id : ", category_id)
    print("subcategory_id : ", subcategory_id)
    print("item_id : ", item_id)
    print("date_from : ", date_from)
    print("date_to : ", date_to)
    print("pr_status : ", pr_status_id)

    if pr_number!="":
        sql = "select pr.prID,pr.prReqDate,pr.prCurrency,ex.erCurrency,pr.prTotalAmt,pr.prCplStatus,pr.prRouting,pr.prNextHandler,pr.prurgent,pr.prConsigner,pr.prcpa,"        
        sql += "pr.prcpa,pr.prnextstatus,s.stname,pr.prcategory,c.ctname,pr.prapplicant,uapp.usName applicant_name,pr.prattentionto,uatt.usName attention_to_name,d.dpnumber,d.dpname,uhan.usname next_handler_name,po.ponumber "
        sql += "from prpo_pr pr "
        sql += "join prpo_exchangerate ex on pr.prcurrency=ex.erid "
        sql += "join prpo_status s on pr.prnextstatus=s.stid "
        sql += "join prpo_category c on pr.prcategory=c.ctid "
        sql += "join prpo_user uapp on pr.prapplicant=uapp.usID "
        sql += "join prpo_user uatt on pr.prAttentionTo=uatt.usID "
        sql += "join prpo_user uhan on pr.prnexthandler=uhan.usid "
        sql += "join prpo_department d on uapp.usdepartment=d.dpid "
        sql += "left outer join prpo_po po on pr.prid=po.popr "
        sql += "where pr.prid='" + str(pr_number) + "'"        
    else:
        sql = "select pr.prID,pr.prReqDate,pr.prCurrency,ex.erCurrency,pr.prTotalAmt,pr.prCplStatus,pr.prRouting,pr.prNextHandler,pr.prurgent,pr.prConsigner,pr.prcpa,"
        sql += "pr.prcpa,pr.prnextstatus,s.stname,pr.prcategory,c.ctname,pr.prapplicant,uapp.usName applicant_name,pr.prattentionto,uatt.usName attention_to_name,d.dpnumber,d.dpname,uhan.usname next_handler_name,po.ponumber "
        sql += "from prpo_pr pr "
        sql += "join prpo_exchangerate ex on pr.prcurrency=ex.erid "
        sql += "join prpo_status s on pr.prnextstatus=s.stid "
        sql += "join prpo_category c on pr.prcategory=c.ctid "
        sql += "join prpo_user uapp on pr.prapplicant=uapp.usid "
        sql += "join prpo_user uatt on pr.prAttentionTo=uatt.usid "
        sql += "join prpo_user uhan on pr.prnexthandler=uhan.usid "
        sql += "join prpo_department d on uapp.usdepartment=d.dpid "
        sql += "left outer join prpo_po po on pr.prid=po.popr "
        sql += "where pr.prReqDate between '" + str(date_from) + "' and '" + str(date_to) + " 23:59:00' "
        sql += "and pr.prApplicant=" + str(user_id) + " "

        if category_id != "" and category_id != "0":
            sql += " and pr.prcategory=" + str(category_id) + " "

        if pr_status_id != "" and pr_status_id != "0":
            sql += " and pr.prnextstatus=" + str(pr_status_id) + " "

    sql += "order by pr.prid;"

    # sql += ";"

    print("sql pr list: ", sql)

    try:
        cursor = connection.cursor()
        cursor.execute(sql)
        pr_list_obj = cursor.fetchall()

        if pr_list_obj is not None:
            if len(pr_list_obj) > 0:
                for item in pr_list_obj:
                    prid = item[0].strip()                    
                    # print("prid :" + prid.strip())
                    prreqdate = item[1].strftime("%d/%m/%Y")
                    prcurrency = item[2]
                    ercurrency = item[3]                                        
                    prtotalamt = "{:,.2f}".format(item[4])
                    prcplstatus = "1" if item[5] else "0"
                    prrouting = item[6]
                    prnexthandler = item[7]
                    prurgent = item[8]
                    prconsigner = "" if item[9] is None else item[10]
                    prcpa = item[10]
                    prnextstatus = item[11]
                    stname = item[13]
                    prcategory = item[13]
                    pr_category_name = item[15]
                    prapplicant_name = item[17]
                    prattentionto_name = item[19]                    
                    dpnumber = item[20]
                    dpname = item[21]
                    nexthandler_name = item[22]
                    ponumber = item[23] if item[23] is not None else ""

                    record = {
                        "prid": prid.strip(),
                        "prcurrency": prcurrency,
                        "ercurrency": ercurrency,
                        "prreqdate": prreqdate,
                        "prtotalamt": prtotalamt,
                        "prcplstatus": prcplstatus,
                        "prrouting": prrouting,
                        "prnexthandler": prnexthandler,
                        "prurgent": prurgent,
                        "prconsigner": prconsigner,
                        "prcpa": prcpa,
                        "prnextstatus": prnextstatus,
                        "stname": stname,
                        "prcategory": prcategory,
                        "pr_category_name": pr_category_name,
                        "prapplicant_name": prapplicant_name,
                        "prattentionto_name": prattentionto_name,
                        "nexthandler_name": nexthandler_name,
                        "dpnumber": dpnumber,
                        "dpname": dpname,
                        "ponumber": ponumber,
                    }

                    pr_list.append(record)
                    
        is_error = False
        message = "Success"
    except db.OperationalError as e:
        is_error = True
        message = "<b>Error: please send this error to IT team</b><br>" + str(e)
    except db.Error as e:
        is_error = True
        message = "<b>Error: please send this error to IT team</b><br>" + str(e)
    finally:
        cursor.close()

    print("count : ", len(pr_list))

    response = JsonResponse(data={        
        "is_error": is_error,
        "message": message,
        "pr_list": list(pr_list),
    })
    
    response.status_code = 200
    return response


@login_required(login_url='/accounts/login/')
def pr_entry(request):
    user_language = getDefaultLanguage(request.user.username)
    translation.activate(user_language)
    page_title = settings.PROJECT_NAME
    db_server = settings.DATABASES['default']['HOST']
    project_name = settings.PROJECT_NAME
    project_version = settings.PROJECT_VERSION    
    today_date = getDateFormatDisplay(user_language)
    username = request.user.username
    
    is_error = True
    message = ""
    pr_id = request.POST.get("selected_pr_id")
    company_list = []
    project_list = []
    division_list = []
    currency_list = []
    attention_to_list = []
    pr_detail_list = []
    user_list = []
    record = {}

    prcompany = ""
    prapplicant = ""
    prcpa = ""
    prreqdate = ""
    prcategory = ""
    pritemtype = ""
    prvendortype = ""
    prurgent = ""
    prrecmdvendor = ""
    prrecmdreason = ""
    prdeliveryto = ""
    prremarks = ""
    
    if user_language == "th":
        username_display = LeaveEmployee.objects.filter(emp_id=request.user.username).values_list('emp_fname_th', flat=True).get()
    else:
        username_display = LeaveEmployee.objects.filter(emp_id=request.user.username).values_list('emp_fname_en', flat=True).get()        

    vendor_type_list = [
        {'vendor_type_id': '1', 'vendor_type_name': 'Any Vendor'},
        {'vendor_type_id': '2', 'vendor_type_name': 'Vendor Recommended'},
        {'vendor_type_id': '3', 'vendor_type_name': 'Vendor Nominated'},
    ]

    item_type_list = [
        {'item_type_id': 'New Item', 'item_type_name': 'New Item'},
        {'item_type_id': 'Spare', 'item_type_name': 'Spare'},
        {'item_type_id': 'Replacement', 'item_type_name': 'Replacement'},
    ]
                       
    # Get Company List
    sql = "select cpid,cpname from PRPO_Company;"
    try:
        with connection.cursor() as cursor:     
            cursor.execute(sql)
            company_obj = cursor.fetchall()

        if company_obj is not None:
            for item in company_obj:
                cpid = item[0]
                cpname = item[1]
                record = {"cpid":cpid, "cpname":cpname}
                company_list.append(record)
            is_error = False
            message = "Able to get company list."

    except db.OperationalError as e: 
        is_error = True
        message = "Error message: " + str(e)
    except db.Error as e:
        is_error = True
        message = "Error message: " + str(e)
    finally:
        cursor.close()

    # Get Project List
    sql = "select cpaid,cpanumber name from PRPO_CPA order by cpaNumber;"
    try:
        with connection.cursor() as cursor:     
            cursor.execute(sql)
            project_obj = cursor.fetchall()

        if project_obj is not None:
            for item in project_obj:
                cpaid = item[0]
                cpanumber = item[1]
                record = {"cpaid":cpaid, "cpanumber":cpanumber}
                project_list.append(record)
            is_error = False
            message = "Able to get project list."

    except db.OperationalError as e: 
        is_error = True
        message = "Error message: " + str(e)
    except db.Error as e:
        is_error = True
        message = "Error message: " + str(e)
    finally:
        cursor.close()

    # Get Division List
    sql = "select ctID,ctName name from PRPO_Category where ctcountry=14 order by ctName;"
    try:
        with connection.cursor() as cursor:     
            cursor.execute(sql)
            division_obj = cursor.fetchall()

        if division_obj is not None:
            for item in division_obj:
                ctid = item[0]
                ctname = item[1]
                record = {"ctid":ctid, "ctname":ctname}
                division_list.append(record)
            is_error = False
            message = "Able to get division list."

    except db.OperationalError as e: 
        is_error = True
        message = "Error message: " + str(e)
    except db.Error as e:
        is_error = True
        message = "Error message: " + str(e)
    finally:
        cursor.close()

    # Get Attention To List
    sql = "select * from prpo_user where usstatus=1 order by usname;"
    try:
        with connection.cursor() as cursor:     
            cursor.execute(sql)
            attention_to_obj = cursor.fetchall()

        if attention_to_obj is not None:
            for item in attention_to_obj:
                usid = item[0]
                usname = item[1]

                record = {"usid":usid, "usname":usname}
                attention_to_list.append(record)
            is_error = False
            message = "Able to get Attention To list."

    except db.OperationalError as e: 
        is_error = True
        message = "Error message: " + str(e)
    except db.Error as e:
        is_error = True
        message = "Error message: " + str(e)
    finally:
        cursor.close()


    # Get User List
    sql = "select usid,usname from prpo_user;"
    try:
        with connection.cursor() as cursor:     
            cursor.execute(sql)
            user_obj = cursor.fetchall()

        if user_obj is not None:
            for item in user_obj:
                usid = item[0]
                usname = item[1]
                record = {"usid":usid, "usname":usname}
                user_list.append(record)
            is_error = False
            message = "Able to get user list."

    except db.OperationalError as e: 
        is_error = True
        message = "Error message: " + str(e)
    except db.Error as e:
        is_error = True
        message = "Error message: " + str(e)
    finally:
        cursor.close()


    if request.method == 'POST':
        # Get PR information     
        sql = "select prid,prcompany,prapplicant,prcpa,prreqdate,prcategory,prcurrency,prdeliveryto,pritemtype,prattentionto,"
        sql += "prattstatus,prattlink,prattrcvddate,prvendortype,prrecmdvendor,prrecmdreason,prurgent,prtotalitem,prtotalamt,"
        sql += "prtotalamtusd,prcplstatus,prremarks,prrouting,prnexthandler,prconsigner,prnextstatus,prverifyamount,practualamount,practualamountusd "
        sql += "from prpo_pr where prid='" + str(pr_id) + "';"
        try:
            with connection.cursor() as cursor:     
                cursor.execute(sql)
                pr_obj = cursor.fetchone()

            if pr_obj is not None:
                prid = pr_obj[0]
                prcompany = pr_obj[1]
                prapplicant = pr_obj[2]
                prcpa = pr_obj[3]
                prreqdate = pr_obj[4]
                prcategory = pr_obj[5]
                prdeliveryto = pr_obj[7]
                pritemtype = pr_obj[8]
                prvendortype = pr_obj[13]
                
                prrecmdvendor = pr_obj[14] if pr_obj[14] else ""
                prrecmdreason = pr_obj[15] if pr_obj[15] else ""

                prurgent = pr_obj[16]
                prremarks = pr_obj[21]

            is_error = False
            message = "Able to get pr information."

        except db.OperationalError as e: 
            is_error = True
            message = "Error message: " + str(e)
        except db.Error as e:
            is_error = True
            message = "Error message: " + str(e)
        finally:
            cursor.close()

        # Get PR Detail
        sql = "select rdid,rdpr,rdsubcategory,rditem,rditemdesc,rditemprice,rdtaxflag,rdtaxrate,rditemqty,rditemum,rdamount,"
        sql += "rddlvrydate,rdpodetail,rdactive,rdreleasedate,rdactualprice "
        sql += "from prpo_prdetail "
        sql += "where rdpr='" + str(pr_id) + "';" 

        try:
            with connection.cursor() as cursor:     
                cursor.execute(sql)
                pr_detail_obj = cursor.fetchall()

            if pr_detail_obj is not None:
                for item in pr_detail_obj:
                    rdid = item[0]
                    rdpr = item[1]
                    rdsubcategory = item[2]
                    rditem = item[3]
                    rditemdesc = item[4]
                    rditemprice = item[5]
                    rdtaxflag = "Yes" if item[6] else "No"
                    rdtaxrate = item[7]
                    rditemqty = item[8]
                    rditemum = item[9]
                    rdamount = item[10]
                    rddlvrydate = item[11]
                    rdpodetail = item[12]
                    rdactive = item[13]
                    rdreleasedate = item[14]
                    prreqdate = item[1]
                    rdactualprice = item[15]

                    record = {
                        'rdid': rdid,
                        'rdpr': rdpr,
                        'rdsubcategory': rdsubcategory,
                        'rditem': rditem,
                        'rditemdesc': rditemdesc,
                        'rditemprice': rditemprice,
                        'rdtaxflag': rdtaxflag,
                        'rdtaxrate': rdtaxrate,
                        'rditemqty': rditemqty,
                        'rditemum': rditemum,
                        'rdamount': rdamount,
                        'rddlvrydate': rddlvrydate,
                        'rdpodetail': rdpodetail,
                        'rdactive': rdactive,
                        'rdreleasedate': rdreleasedate,
                        'rdactualprice': rdactualprice,
                    }
                    pr_detail_list.append(record)

            is_error = False
            message = "Able to get pr detail."

        except db.OperationalError as e: 
            is_error = True
            message = "Error message: " + str(e)
        except db.Error as e:
            is_error = True
            message = "Error message: " + str(e)
        finally:
            cursor.close()    

    if pr_id == "" or pr_id is None:
        pr_id_display = "Create new PR"
    else:
        pr_id_display = str(pr_id) + " | edit"

    # get last login
    last_login = getLastLogin(request)

    return render(request,
        'prpo/pr_entry.html', {
        'page_title': settings.PROJECT_NAME,
        'today_date': today_date,
        'project_version': settings.PROJECT_VERSION,
        'db_server': settings.DATABASES['default']['HOST'],
        'project_name': settings.PROJECT_NAME,
        'user_language': user_language,
        'username_display': username_display,                
        'company_list': list(company_list),
        'project_list': list(project_list),
        'division_list': list(division_list),
        'item_type_list': list(item_type_list),
        'vendor_type_list': list(vendor_type_list),
        'attention_to_list': list(attention_to_list),
        'pr_detail_list': list(pr_detail_list),
        'user_list': list(user_list),
        'pr_id': pr_id,
        'pr_id_display': pr_id_display,
        'prcompany': prcompany,
        'prapplicant': prapplicant,
        'prcpa': prcpa,
        'prreqdate': prreqdate,
        'prcategory': prcategory,
        'pritemtype': pritemtype,
        'prvendortype': prvendortype,
        'prurgent': prurgent,
        'prrecmdvendor': prrecmdvendor,
        'prrecmdreason': prrecmdreason,
        'prdeliveryto': prdeliveryto,
        'prremarks': prremarks,
        'last_login': last_login,
    })
