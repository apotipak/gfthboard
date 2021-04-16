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
from gfthboard.settings import MEDIA_ROOT
from docxtpl import DocxTemplate
from docx2pdf import convert
from os import path
import xlwt
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

    it_contract_list = []
    record = {}

    ITcontractList = ITcontractDB.objects.exclude(upd_flag='D').all()

    if ITcontractList is not None:
        for item in ITcontractList:
            it_contract_id = item.id
            department = item.dept
            vendor = item.vendor
            description = item.description
            contact = item.person
            phone = item.tel
            email = item.e_mail
            start_date = item.start_date
            end_date = item.end_date
            price = item.price
            remark = item.remark
            upd_by = item.upd_by

            record = {
                "id": it_contract_id,
                "dept": department,
                "vendor": vendor,
                "description": description,
                "contact": contact,
                "phone": phone,
                "email": email,
                "start_date": start_date,
                "end_date": end_date,
                "price": price,
                "remark": remark,
                "upd_by": upd_by,
            }

            it_contract_list.append(record)

    return render(request,
        'ITcontract/ITcontract_policy.html', {
        'page_title': settings.PROJECT_NAME,
        'today_date': today_date,
        'project_version': settings.PROJECT_VERSION,
        'db_server': settings.DATABASES['default']['HOST'],
        'project_name': settings.PROJECT_NAME,
        'user_language': user_language,
        'username_display': username_display,
        'ITcontractList':  it_contract_list,
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
    person = ""
    tel = ""
    price = 0
    e_mail = ""
    remark = ""
    start_date = ""
    end_date = ""
    is_attacehed = False
    attached_file_name = ""

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
                    attached_file_name = str(itcontract.afile)
            else:
                attacehed_file = False

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
        "person": person,
        "tel": tel,
        "price": price,
        "e_mail": e_mail,
        "remark": remark,
        "start_date": start_date,
        "end_date": end_date,
        "attacehed_file": attacehed_file,
        "attached_file_name": attached_file_name,
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
                print("do nothing")
    
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
        upd_by = item.upd_by

        afile = item.afile
        if(afile != ""):
            is_file_attached = True
        else:
            is_file_attached = False

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
            "is_file_attached": is_file_attached,
            "upd_by": upd_by,
        }
        refresh_it_contract_list.append(record)

    return refresh_it_contract_list


@permission_required('ITcontract.view_itcontractdb', login_url='/accounts/login/')
def view_contract_document(request, it_contract_id):
    result = {}
    total_day = 0
    total_hour = 0
    document_obj = ITcontractDB.objects.filter(id__exact=it_contract_id).get()
    write_document_data = open('media/' + str(document_obj.afile), 'wb').write(document_obj.afile_data)
    document_data = open('media/' + str(document_obj.afile), 'rb')
    response = FileResponse(document_data)
    return response


@permission_required('ITcontract.view_itcontractdb', login_url='/accounts/login/')
def ajax_print_it_contract_report(request):

    base_url = MEDIA_ROOT + '/itcontract/template/'
    template_name = base_url + 'it_contract_list.docx'
    file_name = "IT_Contract_List"

    it_contract_obj = ITcontractDB.objects.exclude(upd_flag='D').all()
    print_datetime = datetime.now().strftime("%d/%m/%Y %H:%M")

    it_contract_list = []
    record = {}

    if it_contract_obj is not None:
        for item in it_contract_obj:
            it_contract_id = item.id
            vendor = item.vendor
            description = item.description
            contact = item.person
            phone = item.tel
            email = item.e_mail
            start_date = item.start_date.strftime("%d/%m/%Y")
            end_date = item.end_date.strftime("%d/%m/%Y")
            price = item.price
            remark = item.remark

            record = {
                "it_contract_id": it_contract_id,
                "vendor": vendor,
                "description": description,
                "contact": contact,
                "phone": phone,
                "email": email,
                "start_date": start_date,
                "end_date": end_date,
                "price": price,
                "remark": remark,
            }

            it_contract_list.append(record)

    context = {'it_contract_list': list(it_contract_list), 'print_datetime': print_datetime}

    tpl = DocxTemplate(template_name)
    tpl.render(context)
    tpl.save(MEDIA_ROOT + '/itcontract/download/' + file_name + ".docx")

    docx_file = path.abspath("media\\itcontract\\download\\" + file_name + ".docx")
    pdf_file = path.abspath("media\\itcontract\\download\\" + file_name + ".pdf")    
    convert(docx_file, pdf_file)

    return FileResponse(open(pdf_file, 'rb'), content_type='application/pdf')


@permission_required('ITcontract.view_itcontractdb', login_url='/accounts/login/')
def export_it_contract_to_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="IT_Contract_List.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('IT_Contract_List')

    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    font_style = xlwt.easyxf('font: bold 1,height 280;')
    ws.write(0, 5, "IT Contract List", font_style)

    # font_style = xlwt.XFStyle()
    font_style = xlwt.easyxf('font: height 180;')        
    ws.col(1).width = int(13*260)
    ws.col(2).width = int(13*260)
    ws.col(3).width = int(13*260)
    ws.col(4).width = int(13*260)
    ws.col(5).width = int(13*260)
    ws.col(6).width = int(13*260)
    ws.col(7).width = int(13*260)
    ws.col(8).width = int(13*260)
    ws.col(9).width = int(20*260)

    columns = ['ID', 'Vendor', 'Description', 'Contact', 'Phone', 'Email', 'Start Date', 'End Date', 'Price', 'Remark']
    for col_num in range(len(columns)):
        ws.write(2, col_num, columns[col_num], font_style)
    
    font_style = xlwt.XFStyle()
    font_style = xlwt.easyxf('font: height 180;')

    row_num = 3
    counter = 1

    it_contract_obj = ITcontractDB.objects.exclude(upd_flag='D').all()
    print(len(it_contract_obj))
    
    if it_contract_obj is not None:        
        for row in it_contract_obj:
            it_contract_id = row.id
            vendor = row.vendor
            description = row.description
            contact = row.person
            phone = row.tel
            email = row.e_mail
            start_date = row.start_date.strftime("%d/%m/%Y")
            end_date = row.end_date.strftime("%d/%m/%Y")
            price = row.price
            remark = row.remark

            for col_num in range(len(columns)):
                if(col_num==0):
                    ws.write(row_num, 0, it_contract_id, font_style)
                elif(col_num==1):
                    ws.write(row_num, 1, vendor, font_style)
                elif(col_num==2):
                    ws.write(row_num, 2, description, font_style)
                elif(col_num==3):
                    ws.write(row_num, 3, contact, font_style)
                elif(col_num==4):
                    ws.write(row_num, 4, phone, font_style)
                elif(col_num==5):
                    ws.write(row_num, 5, email, font_style)
                elif(col_num==6):
                    ws.write(row_num, 6, start_date, font_style)
                elif(col_num==7):
                    ws.write(row_num, 7, end_date, font_style)
                elif(col_num==8):
                    ws.write(row_num, 8, price, font_style)                    
                else:
                    ws.write(row_num, 9, remark, font_style)

            row_num += 1
            counter += 1

    wb.save(response)
    return response
