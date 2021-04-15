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
from base64 import b64encode
from django.db import connection
from .forms import ITcontractDBForm
from django.http import FileResponse
import django.db as db
import sys
import json
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
    
    ITcontractList = ITcontractDB.objects.exclude(upd_flag='D').all()

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
    # print("it_contract_id : ", it_contract_id)
    record = {}
    itcontract_list = []
    is_error = True
    error_message = ""
    dept = ""
    vendor = ""
    description = ""
    person = ""
    tel = ""
    price = 0
    e_mail = ""
    remark = ""
    start_date = ""
    end_date = ""
    is_attacehed = False

    if it_contract_id is not None:
        itcontract = ITcontractDB.objects.filter(pk=it_contract_id).get()
        if itcontract is not None:
            error_message = ""
            dept = "" if itcontract.dept is None else itcontract.dept
            vendor = "" if itcontract.vendor is None else itcontract.vendor
            description = "" if itcontract.description is None else itcontract.description
            person = "" if itcontract.person is None else itcontract.person
            tel = "" if itcontract.tel is None else itcontract.tel
            price = 0 if itcontract.price is None else itcontract.price
            e_mail = "" if itcontract.e_mail is None else itcontract.e_mail
            remark = "" if itcontract.remark is None else itcontract.remark
            start_date = None if itcontract.start_date is None else itcontract.start_date.strftime("%d/%m/%Y")
            end_date = None if itcontract.end_date is None else itcontract.end_date.strftime("%d/%m/%Y")
            
            if itcontract.afile != "":
                if itcontract.afile_data is not None:
                    attacehed_file = True
            else:
                attacehed_file = False

            is_error = False
            error_message = ""
        else:
            error_message = "Not found"
    else:
        error_message = "Not found"

    # print("vendor : ", vendor)
    # print("attacehed_file : ", 1)

    response = JsonResponse(data={
        "success": True,
        "is_error": is_error,
        "error_message": error_message,
        "it_contract_id": it_contract_id,
        "dept": dept,
        "vendor": vendor,
        "description": description,
        "person": person,
        "tel": tel,
        "price": price,
        "e_mail": e_mail,
        "remark": remark,
        "start_date": start_date,
        "end_date": end_date,
        "attacehed_file": attacehed_file,
    })

    response.status_code = 200
    return response


@permission_required('ITcontract.add_itcontractdb', login_url='/accounts/login/')
def ajax_add_it_contract_item(request):
    is_error = True
    message = ""
    dept = request.POST.get("dept_add")
    vendor = request.POST.get("vendor_add")
    description = request.POST.get("description_add")
    person = request.POST.get("person_add")
    tel = request.POST.get("tel_add")
    price = request.POST.get("price_add")
    e_mail = request.POST.get("e_mail_add")
    remark = request.POST.get("remark_add")
    start_date = datetime.strptime(request.POST.get("start_date_add"), "%d/%m/%Y").date()
    end_date = datetime.strptime(request.POST.get("end_date_add"), "%d/%m/%Y").date()
    
    if request.FILES:
        afile = request.FILES["it_contract_document_add"].name    
        afile_data = request.FILES['it_contract_document_add'].read()
    else:
        afile = ""
        afile_data = None

    record = {}
    refresh_it_contract_list = []    

    try:
        item = ITcontractDB(
            dept = dept,
            vendor = vendor,
            description = description,
            person = person,
            tel = tel,
            price = price,
            e_mail = e_mail,
            remark = remark,
            start_date = start_date,
            end_date = end_date,            
            upd_date = datetime.now(),
            upd_by = request.user.first_name,
            upd_flag = 'A',
            afile = afile,
            afile_data = afile_data,
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
        refresh_it_contract_list = get_refresh_it_contract_list()
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
    
    it_contract_id = request.POST.get("contract_id_edit")
    dept = request.POST.get("dept_edit")
    vendor = request.POST.get("vendor_edit")
    description = request.POST.get("description_edit")
    person = request.POST.get("person_edit")
    tel = request.POST.get("tel_edit")
    price = request.POST.get("price_edit")
    e_mail = request.POST.get("e_mail_edit")
    remark = request.POST.get("remark_edit")
    start_date = datetime.strptime(request.POST.get("start_date_edit"), "%d/%m/%Y").date()
    end_date = datetime.strptime(request.POST.get("end_date_edit"), "%d/%m/%Y").date()

    record = {}
    refresh_it_contract_list = []    
    
    if it_contract_id is not None:
        itcontract = ITcontractDB.objects.filter(pk=it_contract_id).get()

        if itcontract is not None:
            
            itcontract.dept = dept
            itcontract.vendor = vendor
            itcontract.description = description            
            itcontract.person = person
            itcontract.tel = tel
            itcontract.price = price
            itcontract.e_mail = e_mail
            itcontract.remark = remark
            itcontract.start_date = start_date
            itcontract.end_date = end_date            
            itcontract.upd_date = datetime.now()
            itcontract.upd_by = request.user.first_name
            itcontract.upd_flag = 'E'
    
            if request.FILES:
                itcontract.afile = request.FILES["it_contract_document_edit"].name    
                itcontract.afile_data = request.FILES['it_contract_document_edit'].read()
            else:
                itcontract.afile = ""
                itcontract.afile_data = None
    
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
                refresh_it_contract_list = get_refresh_it_contract_list()
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


@permission_required('ITcontract.delete_itcontractdb', login_url='/accounts/login/')
def ajax_delete_it_contract_item(request):
    it_contract_id = request.POST.get("it_contract_id")

    is_error = True
    message = "Erorr"    
    record = {}
    refresh_it_contract_list = []    

    if it_contract_id is not None:
        itcontract = ITcontractDB.objects.filter(pk=it_contract_id).get()
        if itcontract is not None:            
            itcontract.upd_date = datetime.now()
            itcontract.upd_by = request.user.first_name
            itcontract.upd_flag = 'D'

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
                refresh_it_contract_list = get_refresh_it_contract_list()
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


def get_refresh_it_contract_list():
    record = {}
    refresh_it_contract_list = []    

    refresh_it_contract = ITcontractDB.objects.exclude(upd_flag='D').all()

    for item in refresh_it_contract:
        it_contract_id = item.id
        dept = item.dept
        vendor = item.vendor
        description = item.description
        person = item.person
        tel = item.tel
        price = item.price
        e_mail = item.e_mail
        remark = item.remark                    
        start_date = item.start_date.strftime("%d/%m/%Y")
        end_date = item.end_date.strftime("%d/%m/%Y")                
        record = {
            "it_contract_id": it_contract_id,
            "dept": dept,
            "vendor": vendor,
            "description": description,
            "person": person,
            "tel": tel,
            "price": price,
            "e_mail": e_mail,
            "remark": remark,                        
            "start_date": start_date,
            "end_date": end_date,
        }
        refresh_it_contract_list.append(record)

    return refresh_it_contract_list


@permission_required('ITcontract.view_itcontractdb', login_url='/accounts/login/')
def view_contract_document(request, it_contract_id):
    result = {}
    total_day = 0
    total_hour = 0

    # it_contract_id = 9

    # sql = "select afile, afile_data from itcontractdb where id='%s';" % (it_contract_id)
    document_obj = ITcontractDB.objects.filter(id__exact=it_contract_id).get()
    # print(document_obj.document)

    write_document_data = open('media/' + str(document_obj.afile), 'wb').write(document_obj.afile_data)
    document_data = open('media/' + str(document_obj.afile), 'rb')    
    
    response = FileResponse(document_data)
    return response


@permission_required('ITcontract.view_itcontractdb', login_url='/accounts/login/')
def view_contract_document_bk(request):
    result = {}
    total_day = 0
    total_hour = 0

    it_contract_id = request.POST.get("it_contract_id")

    # print(request.POST.get("it_contract_id"))
    # print("TODO")

    # sql = "select afile, afile_data from itcontractdb where id='%s';" % (it_contract_id)
    document_obj = ITcontractDB.objects.filter(id__exact=it_contract_id).get()
    # print(document_obj.document)

    write_document_data = open('media/' + str(document_obj.afile), 'wb').write(document_obj.afile_data)
    document_data = open('media/' + str(document_obj.afile), 'rb')    
    
    # response = HttpResponse(write_document_data, content_type='application/pdf')
    return response


'''
@permission_required('ITcontract.view_itcontractdb', login_url='/accounts/login/')
def ajax_download_file(request):
    it_contract_id = 50
    c = connection.cursor()
    c.execute("select afile from itcontractdb where id=%s", (it_contract_id,))
    file = c.fetchone()[0]
    c.close()

    #response = HttpResponse(file, content_type='application/pdf')
    #response['Content-Disposition'] = 'inline; filename="report.pdf"'

    response = HttpResponse(file, content_type='application/image')
    response['Content-Disposition'] = 'inline; filename="file.png"'

    return response
'''
