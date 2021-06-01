from re import sub
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
def pr_entry_inquiry(request):
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


    department_list = []
    category_list = []
    pr_status_list = []
    record = {}

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
    sql = "select stid status_id, stname from prpo_status where stID in (1,2,3,10) order by stid;"
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

    return render(request,
        'prpo/pr_entry_inquiry.html', {
        'page_title': settings.PROJECT_NAME,
        'today_date': today_date,
        'project_version': settings.PROJECT_VERSION,
        'db_server': settings.DATABASES['default']['HOST'],
        'project_name': settings.PROJECT_NAME,
        'user_language': user_language,
        'username_display': username_display,
        "department_list": list(department_list),
        "category_list": list(category_list),
        "pr_status_list": list(pr_status_list),
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
                    record = {"itid":itid, "itname":itname, "itdescription":itdescription}
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

    if category_id=="" or category_id is None:
        is_error = True
        message = "There is no Category ID provided."
    else:
        sql = "select scid, scname subcategory_name from prpo_subcategory where sccategory=" + str(category_id) + " order by scname;"
        print("SQL ", sql)
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


@login_required(login_url='/accounts/login/')
def ajax_pr_inquiry(request):
    is_error = True
    message = ""

    pr_number = request.POST.get("pr_number")
    category_id = request.POST.get("category_option")
    subcategory_id = request.POST.get("subcategory_option")
    item_id = request.POST.get("item_option")
    date_from = datetime.strptime(request.POST.get("date_from"), "%d/%m/%Y").date()
    date_to = datetime.strptime(request.POST.get("date_to"), "%d/%m/%Y").date()
    
    pr_list_obj = []
    pr_list = []
    record = {}

    print("pr_number : ", pr_number)
    print("category_id : ", category_id)
    print("subcategory_id : ", subcategory_id)
    print("item_id : ", item_id)
    print("date_from : ", date_from)
    print("date_to : ", date_to)

    if pr_number!="":
        # sql = "select prID,prReqDate,prCurrency,prTotalAmt,prCplStatus,prRouting,prNextHandler,prurgent,prConsigner from prpo_pr "
        sql = "select pr.prID,pr.prReqDate,pr.prCurrency,ex.erCurrency,pr.prTotalAmt,pr.prCplStatus,pr.prRouting,pr.prNextHandler,pr.prurgent,pr.prConsigner "
        sql += "from prpo_pr pr "
        sql += "join PRPO_ExchangeRate ex on pr.prCurrency=ex.erID "
        sql += "where pr.prid='" + str(pr_number) + "';"
    else:
        # sql = "select prID,prReqDate,prCurrency,prTotalAmt,prCplStatus,prRouting,prNextHandler,prurgent,prConsigner from prpo_pr "
        sql = "select pr.prID,pr.prReqDate,pr.prCurrency,ex.erCurrency,pr.prTotalAmt,pr.prCplStatus,pr.prRouting,pr.prNextHandler,pr.prurgent,pr.prConsigner "
        sql += "from prpo_pr pr "
        sql += "join PRPO_ExchangeRate ex on pr.prCurrency=ex.erID "
        sql += "where pr.prReqDate between '" + str(date_from) + "' and '" + str(date_to) + " 23:59:00'";

    print("sql: ", sql)

    try:
        cursor = connection.cursor()
        cursor.execute(sql)
        pr_list_obj = cursor.fetchall()

        if pr_list_obj is not None:
            if len(pr_list_obj) > 0:
                for item in pr_list_obj:
                    prid = item[0].strip()
                    # print("prid :" + prid.strip())
                    prcurrency = item[2]
                    ercurrency = item[3]
                    prreqdate = item[1].strftime("%d/%m/%Y")
                    prtotalamt = item[4]
                    prcplstatus = "1" if item[5] else "0"
                    prrouting = item[6]
                    prnexthandler = item[7]
                    prurgent = item[8]
                    prconsigner = "" if item[9] is None else item[10]

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
    pr_id = request.POST.get("selected_pr_id")

    if user_language == "th":
        username_display = LeaveEmployee.objects.filter(emp_id=request.user.username).values_list('emp_fname_th', flat=True).get()
    else:
        username_display = LeaveEmployee.objects.filter(emp_id=request.user.username).values_list('emp_fname_en', flat=True).get()        
                       
    print("PR #: ", pr_id)

    return render(request,
        'prpo/pr_entry.html', {
        'page_title': settings.PROJECT_NAME,
        'today_date': today_date,
        'project_version': settings.PROJECT_VERSION,
        'db_server': settings.DATABASES['default']['HOST'],
        'project_name': settings.PROJECT_NAME,
        'user_language': user_language,
        'username_display': username_display,
        'pr_id': pr_id,
    })
