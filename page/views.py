from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import HttpResponseRedirect
from leave.models import LeaveEmployee
from page.models import UserProfile, ComDivision
from system.models import OutlookEmailActiveUserList
from django.contrib.auth.models import User
from .forms import UserForm, LanguageForm, ViewAllStaffForm
from django.http import HttpResponse
from leave.rules import *
from page.rules import *
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.utils import translation
from django.db.models import CharField, Value as V
from django.db.models.functions import Concat
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.forms.models import model_to_dict
from django.core import serializers
import django.db as db
from django.db import connection
import json
import os
from .models import CovidEmployeeVaccineUpdate, UserPasswordLog
from datetime import datetime
from django.core.files.storage import FileSystemStorage
import re
from django.contrib.auth.hashers import make_password


@login_required(login_url='/accounts/login/')
def index(request):    
    
    if not isPasswordChanged(request):
        template_name = 'page/force_change_password.html'
        return render(request, template_name, {})

    user_language = getDefaultLanguage(request.user.username)
    translation.activate(user_language)
    
    TURN_ANNOUNCEMENT_ON = settings.TURN_ANNOUNCEMENT_ON
    ANNOUNCEMENT_MESSAGE = settings.ANNOUNCEMENT_MESSAGE

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

    page_title = settings.PROJECT_NAME    
    db_server = settings.DATABASES['default']['HOST']
    project_name = settings.PROJECT_NAME
    project_version = settings.PROJECT_VERSION

    # today_date = settings.TODAY_DATE
    today_date = getDateFormatDisplay(user_language)

    return render(request, 'index.html', {
        'page_title': page_title, 
        'project_name': project_name, 
        'project_version': project_version, 
        'db_server': db_server, 'today_date': today_date,
        'user_language': user_language,
        'username_display' : username_display,
        'turn_announcement_on': TURN_ANNOUNCEMENT_ON,
        'announcement_message': ANNOUNCEMENT_MESSAGE,
    })

@login_required(login_url='/accounts/login/')
def StaffProfile11(request):
    if not isPasswordChanged(request):
        template_name = 'page/force_change_password.html'
        return render(request, template_name, {})

    user_language = getDefaultLanguage(request.user.username)
    translation.activate(user_language)

    page_title = settings.PROJECT_NAME
    db_server = settings.DATABASES['default']['HOST']
    project_name = settings.PROJECT_NAME
    project_version = settings.PROJECT_VERSION
    # today_date = settings.TODAY_DATE    
    today_date = getDateFormatDisplay(user_language)
    EmployeeInstance = LeaveEmployee.EmployeeInstance(request)
    SuperVisorInstance = LeaveEmployee.SuperVisorInstance(request)
    TeamMemberList = LeaveEmployee.TeamMemberList(request)

    # Check leave approval right
    if checkLeaveRequestApproval(request.user.username):
        able_to_approve_leave_request = True
    else:
        able_to_approve_leave_request = False

    '''
    if user_language == "th":
        username_display = LeaveEmployee.objects.filter(emp_id=request.user.username).values_list('emp_fname_th', flat=True).get()
    else:
        username_display = LeaveEmployee.objects.filter(emp_id=request.user.username).values_list('emp_fname_en', flat=True).get()
    '''

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


    return render(request, 'page/staff_profile.html', {
        'page_title': page_title, 
        'project_name': project_name, 
        'project_version': project_version, 
        'db_server': db_server, 'today_date': today_date,
        'EmployeeInstance': EmployeeInstance,
        'SuperVisorInstance': SuperVisorInstance,
        'TeamMemberList': TeamMemberList,
        'able_to_approve_leave_request': able_to_approve_leave_request,
        'user_language': user_language,
        'username_display': username_display,
    })


@login_required(login_url='/accounts/login/')
def StaffPassword(request):
    user_language = getDefaultLanguage(request.user.username)
    translation.activate(user_language)

    page_title = settings.PROJECT_NAME
    db_server = settings.DATABASES['default']['HOST']
    project_name = settings.PROJECT_NAME
    project_version = settings.PROJECT_VERSION
    # today_date = settings.TODAY_DATE
    today_date = getDateFormatDisplay(user_language)  

    form = UserForm(request.POST, user=request.user)
 
    if request.method == "POST":
        if form.is_valid():            
            new_password = form.cleaned_data['new_password']
            u = User.objects.get(username__exact=request.user)
            u.set_password(new_password)
            u.save()            
            return HttpResponseRedirect('/staff-profile')
    else:
        form = UserForm(user=request.user)    

    '''    
    if user_language == "th":
        username_display = LeaveEmployee.objects.filter(emp_id=request.user.username).values_list('emp_fname_th', flat=True).get()
    else:
        username_display = LeaveEmployee.objects.filter(emp_id=request.user.username).values_list('emp_fname_en', flat=True).get()
    '''

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


    return render(request, 'page/staff_password_form.html', {
        'form': form,
        'page_title': page_title, 
        'project_name': project_name, 
        'project_version': project_version, 
        'db_server': db_server, 'today_date': today_date,
        'username_display': username_display,
    })


@login_required(login_url='/accounts/login/')
def StaffLanguage(request):
    user_language = getDefaultLanguage(request.user.username)
    translation.activate(user_language)

    page_title = settings.PROJECT_NAME
    db_server = settings.DATABASES['default']['HOST']
    project_name = settings.PROJECT_NAME
    project_version = settings.PROJECT_VERSION
    # today_date = settings.TODAY_DATE
    today_date = getDateFormatDisplay(user_language)   

    form = LanguageForm(request.POST, user=request.user)

    if request.method == "POST":
        if form.is_valid():
            language_code = form.cleaned_data['language_code']
            username = request.user.username
            userid = request.user.id

            if not UserProfile.objects.filter(username=username).exists():
                UserProfile.objects.create(language=language_code, updated_by_id=userid, username=username)
            else:
                employee = UserProfile.objects.get(username=username)
                employee.language = language_code
                employee.updated_by_id = userid
                employee.username = username
                employee.save()
            
            messages.success(request, _('ตั้งค่าใหม่สำเร็จ'))
            return HttpResponseRedirect('/staff-language')
    else:
        form = LanguageForm(user=request.user)    

    '''
    if user_language == "th":
        username_display = LeaveEmployee.objects.filter(emp_id=request.user.username).values_list('emp_fname_th', flat=True).get()
    else:
        username_display = LeaveEmployee.objects.filter(emp_id=request.user.username).values_list('emp_fname_en', flat=True).get()
    '''

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
    return render(request, 'page/staff_language.html', {
        'form': form,
        'page_title': page_title, 
        'project_name': project_name, 
        'project_version': project_version, 
        'db_server': db_server, 'today_date': today_date,
        'username_display': username_display,
    })


@login_required(login_url='/accounts/login/')
def StaffProfile(request):
    if not isPasswordChanged(request):
        template_name = 'page/force_change_password.html'
        return render(request, template_name, {})
        
    item_per_page = 12
    user_language = getDefaultLanguage(request.user.username)
    translation.activate(user_language)

    page_title = settings.PROJECT_NAME
    db_server = settings.DATABASES['default']['HOST']
    project_name = settings.PROJECT_NAME
    project_version = settings.PROJECT_VERSION
    today_date = getDateFormatDisplay(user_language)
    EmployeeInstance = LeaveEmployee.EmployeeInstance(request)

    if request.user.username == "999999":
        SuperVisorInstance = None
    else:
        SuperVisorInstance = LeaveEmployee.SuperVisorInstance(request)

    TeamMemberList = LeaveEmployee.TeamMemberList(request)

    # Get email
    email = ""
    email_object = None
    try:

        emp_id = request.user.username
        first_name = request.user.first_name
        last_name = request.user.last_name
        email = request.user.email
        # print("--- a --- : ", email)
        # email_object = OutlookEmailActiveUserList.objects.filter(first_name=first_name).filter(last_name=last_name).first()
        email_object = OutlookEmailActiveUserList.objects.filter(email=email).first()

    except db.OperationalError as e:
        message = str(e)
    except db.Error as e:
        message = str(e)
    except Exception as e:                
        message = str(e)
    if email_object is not None:
        # print("a")
        email = email_object.email
    else:
        email = ""
        # print("b")
    
    # print("--- b --- : ", email)

    # Check leave approval right
    if checkLeaveRequestApproval(request.user.username):
        able_to_approve_leave_request = True
    else:
        able_to_approve_leave_request = False

    '''
    if user_language == "th":
        username_display = LeaveEmployee.objects.filter(emp_id=request.user.username).values_list('emp_fname_th', flat=True).get()
    else:
        username_display = LeaveEmployee.objects.filter(emp_id=request.user.username).values_list('emp_fname_en', flat=True).get()
    '''

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

    if request.method == "POST":
        form = ViewAllStaffForm(request.POST, user=request.user)
        department_id = request.POST.get('department_list')
        first_name = request.POST.get('first_name')
        request.session['search_department'] = department_id
        request.session['search_first_name'] = first_name

        department_name_en = _("All Departments")

        if not department_id and not first_name:
            employee = LeaveEmployee.objects.all()            
        elif department_id and not first_name:
            department_name_en = ComDivision.objects.filter(div_id=department_id).values_list('div_en', flat=True).get()
            employee = LeaveEmployee.objects.filter(div_en=department_name_en).order_by('emp_id')
        elif first_name and not department_id:            
            if len(first_name) >= 2:
                if user_language == "th":
                    employee = LeaveEmployee.objects.filter(emp_fname_th__startswith=first_name)
                else:
                    employee = LeaveEmployee.objects.filter(emp_fname_en__startswith=first_name)
            else:
                employee = LeaveEmployee.objects.filter(emp_fname_th__startswith="None")
        else:
            department_name_en = ComDivision.objects.filter(div_id=department_id).values_list('div_en', flat=True).get()
            employee = LeaveEmployee.objects.filter(div_en=department_name_en, emp_fname_th__startswith=first_name)

        paginator = Paginator(employee, item_per_page)

        is_paginated = True if paginator.num_pages > 1 else False
        page = 1

        try:
            current_page = paginator.page(page)
        except InvalidPage as e:
            raise Http404(str(e))

        context = {
            'current_page': current_page,
            'is_paginated': is_paginated,
            'page_title': page_title, 
            'project_name': project_name, 
            'project_version': project_version, 
            'db_server': db_server, 'today_date': today_date,
            'EmployeeInstance': EmployeeInstance,
            'SuperVisorInstance': SuperVisorInstance,
            'TeamMemberList': TeamMemberList,
            'able_to_approve_leave_request': able_to_approve_leave_request,
            'user_language': user_language,            
            'username_display': username_display,
            'form': form,
            'dept': department_name_en,
            'emp_name': first_name,
            'email': email,
        }        
    else:
        form = ViewAllStaffForm(user=request.user)
        
        if 'search_department' in request.session:
            if request.session['search_department'] != "":
                department_id = request.session['search_department']
                department_name_en = ComDivision.objects.filter(div_id=department_id).values_list('div_en', flat=True).get()
            else:
                department_id = ""
                department_name_en = _("All Departments")
        else:
            department_id = ""
            department_name_en = _("All Departments")

        if 'search_first_name' in request.session:
            if request.session['search_first_name'] != "":
                first_name = request.session['search_first_name']
            else:
                first_name = ""
        else:
            first_name = ""

        if department_id == "" and first_name == "":
            employee = LeaveEmployee.objects.all().order_by('emp_id')
        elif department_id != "" and first_name == "":
            employee = LeaveEmployee.objects.filter(div_en=department_name_en).order_by('emp_id')
        elif first_name != "" and department_id == "":
            if user_language == "th":
                employee = LeaveEmployee.objects.filter(emp_fname_th__startswith=first_name)
            else:
                employee = LeaveEmployee.objects.filter(emp_fname_en__startswith=first_name)
        else:
            if user_language == "th":
                employee = LeaveEmployee.objects.filter(emp_fname_th__startswith=first_name)
            else:
                employee = LeaveEmployee.objects.filter(emp_fname_en__startswith=first_name)

        paginator = Paginator(employee, item_per_page)

        is_paginated = True if paginator.num_pages > 1 else False
        page = request.GET.get('page') or 1

        try:
            current_page = paginator.get_page(page)
        except InvalidPage as e:
            raise Http404(str(e))

        context = {
            'current_page': current_page,
            'is_paginated': is_paginated,
            'page_title': page_title, 
            'project_name': project_name, 
            'project_version': project_version, 
            'db_server': db_server, 'today_date': today_date,
            'EmployeeInstance': EmployeeInstance,
            'SuperVisorInstance': SuperVisorInstance,
            'TeamMemberList': TeamMemberList,
            'able_to_approve_leave_request': able_to_approve_leave_request,
            'user_language': user_language,            
            'username_display': username_display,
            'form': form,
            'dept': department_name_en,
            'emp_name': first_name,
            'email': email,
        }

    return render(request, 'page/staff_profile.html', context)


@login_required(login_url='/accounts/login/')
def viewallstaff(request):
    item_per_page = 20  
    user_language = getDefaultLanguage(request.user.username)
    translation.activate(user_language)

    '''
    if user_language == "th":
        username_display = LeaveEmployee.objects.filter(emp_id=request.user.username).values_list('emp_fname_th', flat=True).get()
    else:
        username_display = LeaveEmployee.objects.filter(emp_id=request.user.username).values_list('emp_fname_en', flat=True).get()
    '''

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


    page_title = settings.PROJECT_NAME
    db_server = settings.DATABASES['default']['HOST']
    project_name = settings.PROJECT_NAME
    project_version = settings.PROJECT_VERSION
    today_date = getDateFormatDisplay(user_language)

    if request.method == "POST":
        form = ViewAllStaffForm(request.POST, user=request.user)
        
        # department_id = form.data['department_list']
        department_id = request.POST.get('department_list')
        first_name = request.POST.get('first_name')

        request.session['search_department'] = department_id

        if len(department_id) == 0:
            employee = LeaveEmployee.objects.all()
            department_name_en = _("All Departments")
        else:
            department_name_en = ComDivision.objects.filter(div_id=department_id).values_list('div_en', flat=True).get()
            employee = LeaveEmployee.objects.filter(div_en=department_name_en).order_by('emp_id')
        
        paginator = Paginator(employee, item_per_page)

        is_paginated = True if paginator.num_pages > 1 else False
        # page = request.GET.get('page') or 1
        page = 1

        try:
            current_page = paginator.page(page)
        except InvalidPage as e:
            raise Http404(str(e))

        context = {
            'current_page': current_page,
            'is_paginated': is_paginated,        
            'page_title': page_title, 
            'project_name': project_name, 
            'project_version': project_version, 
            'db_server': db_server, 'today_date': today_date,
            'username_display': username_display,
            'form': form,
            'dept': department_name_en,
        }

    else:
        form = ViewAllStaffForm(user=request.user)

        # print("debug: " + request.session['search'])
        # department_id = request.session['search']
        department_id = request.POST.get('department_list')
        department_name_en = _("All Departments")

        if 'search_department' in request.session:
            if len(request.session['search_department']) <= 0:
                employee = LeaveEmployee.objects.all().order_by('emp_id')           
            else:
                department_name_en = ComDivision.objects.filter(div_id=request.session['search_department']).values_list('div_en', flat=True).get()
                employee = LeaveEmployee.objects.filter(div_en=department_name_en).order_by('emp_id')
        else:
            employee = LeaveEmployee.objects.all().order_by('emp_id')
        
        paginator = Paginator(employee, item_per_page)

        is_paginated = True if paginator.num_pages > 1 else False
        page = request.GET.get('page') or 1

        try:
            # current_page = paginator.page(page)
            current_page = paginator.get_page(page)

        except InvalidPage as e:
            raise Http404(str(e))

        context = {
            'current_page': current_page,
            'is_paginated': is_paginated,
            'page_title': page_title, 
            'project_name': project_name, 
            'project_version': project_version, 
            'db_server': db_server, 'today_date': today_date,
            'username_display': username_display,
            'form': form,
            'dept': department_name_en,
        }

    return render(request, 'page/view_all_staff.html', context)


    '''
    if user_language == "th":
        username_display = LeaveEmployee.objects.filter(emp_id=request.user.username).values_list('emp_fname_th', flat=True).get()
    else:
        username_display = LeaveEmployee.objects.filter(emp_id=request.user.username).values_list('emp_fname_en', flat=True).get()

    form = ViewAllStaffForm(request.POST, user=request.user)

    if request.method == "POST":
        if form.is_valid():
            username = request.user.username
            userid = request.user.id
            first_name = form.cleaned_data['first_name']
            
            if len(first_name) > 0:
                employee_list = LeaveEmployee.objects.filter(pos_en='Inspector').all()
            else:
                employee_list = None

            if employee_list:  
                paginator = Paginator(employee_list, 5)
                is_paginated = True if paginator.num_pages > 1 else False
                page = request.GET.get('page') or 1

                try:
                    current_page = paginator.page(page)
                except InvalidPage as e:
                    raise Http404(str(e))

                context = {
                    'current_page': current_page,
                    'is_paginated': is_paginated
                }

                return render(request, 'page/view_all_staff.html', {
                    'form': form,
                    'page_title': page_title, 
                    'project_name': project_name, 
                    'project_version': project_version, 
                    'db_server': db_server, 'today_date': today_date,
                    'username_display': username_display,                    
                    'employee_list': employee_list,
                    'context': context
                })


            else:
                messages.warning(request, _(first_name + ' is not found'))
                return HttpResponseRedirect('/view-all-staff')                
    else:
        form = ViewAllStaffForm(user=request.user)    

    return render(request, 'page/view_all_staff.html', {
        'form': form,
        'page_title': page_title, 
        'project_name': project_name, 
        'project_version': project_version, 
        'db_server': db_server, 'today_date': today_date,
        'username_display': username_display,
    })
    '''

@login_required(login_url='/accounts/login/')
def ajaxviewallstaff(request):
    start = request.GET['iDisplayStart']

    # employee_list = LeaveEmployee.objects.filter(pos_en='Supervisor').values_list('emp_id','emp_fname_en','emp_lname_en','pos_en')
    # employee_list = LeaveEmployee.objects.filter(pos_en='Inspector').all()    
    # json = serializers.serialize('json', employee_list)    
    # json_objects=json.loads(serialized_objects)
    # return HttpResponse(json, content_type='application/json')

    '''
    employee_list = LeaveEmployee.objects.all().values('emp_id','emp_fname_en','emp_lname_en','pos_en')
    employee_list = json.dumps(list(employee_list), cls=DjangoJSONEncoder)
    context = {'employee_list': employee_list}
    return HttpResponse(employee_list, content_type='application/json')
    '''

    employee_list = LeaveEmployee.objects.filter(pos_en='Inspector').all()
    page = request.GET.get('page', 1)
    paginator = Paginator(employee_list, 10)
    try:
        employee = paginator.page(page)
    except PageNotAnInteger:
        employee = paginator.page(1)
    except EmptyPage:
        employee = paginator.page(paginator.num_pages)

    return render(request, 'page/view_all_staff.html', { 'employee': employee })


@login_required(login_url='/accounts/login/')
def HelpEleave(request):
    user_language = getDefaultLanguage(request.user.username)
    translation.activate(user_language)

    page_title = settings.PROJECT_NAME
    db_server = settings.DATABASES['default']['HOST']
    project_name = settings.PROJECT_NAME
    project_version = settings.PROJECT_VERSION
    today_date = getDateFormatDisplay(user_language) 

    '''
    if user_language == "th":
        username_display = LeaveEmployee.objects.filter(emp_id=request.user.username).values_list('emp_fname_th', flat=True).get()
    else:
        username_display = LeaveEmployee.objects.filter(emp_id=request.user.username).values_list('emp_fname_en', flat=True).get()
    '''

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


    return render(request, 'page/help_eleave.html', {
        'page_title': page_title, 
        'project_name': project_name, 
        'project_version': project_version, 
        'db_server': db_server, 'today_date': today_date,
        'username_display' : username_display,
    })


@login_required(login_url='/accounts/login/')
def faq(request):
    user_language = getDefaultLanguage(request.user.username)
    translation.activate(user_language)

    page_title = settings.PROJECT_NAME
    db_server = settings.DATABASES['default']['HOST']
    project_name = settings.PROJECT_NAME
    project_version = settings.PROJECT_VERSION
    today_date = getDateFormatDisplay(user_language) 

    '''
    if user_language == "th":
        username_display = LeaveEmployee.objects.filter(emp_id=request.user.username).values_list('emp_fname_th', flat=True).get()
    else:
        username_display = LeaveEmployee.objects.filter(emp_id=request.user.username).values_list('emp_fname_en', flat=True).get()
    '''

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


    return render(request, 'page/faq.html', {
        'page_title': page_title, 
        'project_name': project_name, 
        'project_version': project_version, 
        'db_server': db_server, 'today_date': today_date,
        'username_display' : username_display,
    })


@login_required(login_url='/accounts/login/')
def news(request):
    user_language = getDefaultLanguage(request.user.username)
    translation.activate(user_language)

    page_title = settings.PROJECT_NAME
    db_server = settings.DATABASES['default']['HOST']
    project_name = settings.PROJECT_NAME
    project_version = settings.PROJECT_VERSION
    today_date = getDateFormatDisplay(user_language) 

    '''
    if user_language == "th":
        username_display = LeaveEmployee.objects.filter(emp_id=request.user.username).values_list('emp_fname_th', flat=True).get()
    else:
        username_display = LeaveEmployee.objects.filter(emp_id=request.user.username).values_list('emp_fname_en', flat=True).get()
    '''
    
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


    return render(request, 'page/news.html', {
        'page_title': page_title, 
        'project_name': project_name, 
        'project_version': project_version, 
        'db_server': db_server, 'today_date': today_date,
        'username_display' : username_display,
    })


# For Testing
# START
def openCarFormPage(request):    
    return render(request, 'page/open_car_form_page.html') 

def openCarForm(request):
    os.startfile("C:\CARFORM\Carform.exe")
    return render(request, 'page/open_car_form_page.html') 
# END



def CovidVaccineUpdate(request):
    user_language = getDefaultLanguage(request.user.username)
    translation.activate(user_language)

    page_title = settings.PROJECT_NAME
    db_server = settings.DATABASES['default']['HOST']
    project_name = settings.PROJECT_NAME
    project_version = settings.PROJECT_VERSION
    today_date = getDateFormatDisplay(user_language) 

    print("test")

    return render(request, 'page/covid_vaccine_update.html', {
        'page_title': page_title, 
        'project_name': project_name, 
        'project_version': project_version, 
        'db_server': db_server, 'today_date': today_date,        
    })


def AjaxCovidVaccineUpdateSearchEmployee(request):
    is_error = True
    message = "Error"    
    emp_id = request.POST.get('emp_id')

    employee_instance = None
    name_th = ""

    # print("emp_id : ", emp_id)

    if emp_id is None or emp_id=="":
        response = JsonResponse(data={
            "success": True,
            "is_error": True,
            "message": "ไม่พบข้อมูล",
            "emp_id": emp_id,
            "name_th": name_th,
        })
    else:
        sql = "select * from covid_employee where emp_id=" + str(emp_id) + ";";
        try:
            cursor = connection.cursor()
            cursor.execute(sql)
            employee_instance = cursor.fetchone()
            if employee_instance is not None:            
                name_th = employee_instance[2]
            
            print("name_th : ", name_th)

        except db.OperationalError as e:
            is_error = True
            message = "<b>Error: please send this error to IT team</b><br>" + str(e)
        except db.Error as e:
            is_error = True
            message = "<b>Error: please send this error to IT team</b><br>" + str(e)
        finally:
            cursor.close()
        
        print("message : ", message)

        response = JsonResponse(data={
            "success": True,
            "is_error": False,
            "message": "Success",
            "emp_id": emp_id,
            "name_th": name_th,
        })

    response.status_code = 200
    return response


def AjaxCovidVaccineUpdateSaveEmployee(request):
    is_error = True
    message = "Error"    
    
    selected_emp_id = request.POST.get('selected_emp_id')
    selected_emp_name_th = request.POST.get('selected_emp_name_th')
    phone_number = request.POST.get('phone_number')
    get_vaccine_status = request.POST.get('get_vaccine_status')
    get_vaccine_day = request.POST.get('get_vaccine_day')
    get_vaccine_month = request.POST.get('get_vaccine_month')
    get_vaccine_year = request.POST.get('get_vaccine_year')
    get_vaccine_time = request.POST.get('get_vaccine_time')
    get_vaccine_place = request.POST.get('get_vaccine_place')

    get_vaccine_year = int(get_vaccine_year) - 543
    date_time_str = get_vaccine_day + "/" + get_vaccine_month + "/" + str(get_vaccine_year) +  " " + get_vaccine_time + ":00:00"
    get_vaccine_date = datetime.strptime(date_time_str, '%d/%m/%Y %H:%M:%S')

    '''
    myfile = request.FILES['document']
    fs = FileSystemStorage()
    filename = fs.save(myfile.name, myfile)
    uploaded_file_url = fs.url(filename)
    '''

    '''
    files = request.FILES.getlist('document')
    fs = FileSystemStorage(location="/data/upload/")
    for fl in files:
        fs.save(fl.name, fl)
    '''

    if request.FILES:
        file_attach = request.FILES["file_attach"].name            
        file_attach_data = request.FILES['file_attach'].read()
        file_attach_type = file_attach.split(".")[-1]
    else:
        file_attach = ""
        file_attach_data = None
        file_attach_type = ""

    print("DEBUG")
    print("selected_emp_id : ", selected_emp_id)
    print("selected_emp_name_th : ", selected_emp_name_th)
    print("phone_number : ", phone_number)
    print("get_vaccine_status : ", get_vaccine_status)
    print("get_vaccine_day : ", get_vaccine_day)
    print("get_vaccine_month : ", get_vaccine_month)
    print("get_vaccine_year : ", get_vaccine_year)
    print("get_vaccine_time : ", get_vaccine_time)
    print("get_vaccine_place : ", get_vaccine_place)
    print("get_vaccine_date : ", get_vaccine_date)

    covid_obj = CovidEmployeeVaccineUpdate(
        emp_id = selected_emp_id,         
        full_name = selected_emp_name_th,
        get_vaccine_status = get_vaccine_status,
        get_vaccine_date = get_vaccine_date,
        get_vaccine_place = get_vaccine_place,
        phone_number = phone_number,
        upd_date = datetime.now(),
        upd_by = "system",
        file_attach = file_attach,
        file_attach_data = file_attach_data,
        file_attach_type = file_attach_type,
    )
    covid_obj.save()    

    
    response = JsonResponse(data={
        "success": True,
        "is_error": False,
        "message": "Success",
    })

    response.status_code = 200
    return response



@login_required(login_url='/accounts/login/')
def ForceChangePassword(request):
    emp_id = request.user.username
    is_password_changed = False
    is_password_expired = False
    page_title = settings.PROJECT_NAME
    db_server = settings.DATABASES['default']['HOST']
    project_name = settings.PROJECT_NAME
    project_version = settings.PROJECT_VERSION
    today_date = settings.TODAY_DATE	

    template_name = 'page/force_change_password.html'

    try:
        employee_info = UserPasswordLog.objects.get(emp_id=emp_id)
    except UserPasswordLog.DoesNotExist:
        employee_info = None

    if employee_info is not None:
        is_password_changed = employee_info.is_password_changed
        is_password_expired = employee_info.is_password_expired

        if is_password_changed:
            print("change password")
            return redirect("/")
        else:
            return render(request, template_name, {
                'page_title': page_title,
                'project_name': project_name,
                'project_version': project_version,
                'db_server': db_server,
                'today_date': today_date,
                'database': settings.DATABASES['default']['NAME'],
                'host': settings.DATABASES['default']['HOST'],
            })
    else:
        return redirect("/")


@login_required(login_url='/accounts/login/')
def AjaxForceChangePassword(request):
    is_password_changed = False
    is_password_expired = False

    emp_id = request.user.username
    new_password1 = request.POST.get("new_password1")
    new_password2 = request.POST.get("new_password2")
    print("emp_id : ", emp_id)
    print("new_password1 : ", new_password1)
    print("new_password2 : ", new_password2)

    excluded_password = {'123@gfth'}

    # Passwore Rules!
    if(new_password1!=new_password2):
        response = JsonResponse(data={
            "success": True,
            "is_error": True,
            "message": "รหัสผ่านไม่ตรงกัน กรุณาตรวจสอบอีกครั้ง",
        })
        response.status_code = 200
        return response        
    elif(len(new_password1)<8):
        message = """    
        <div class='text-left'>
        <b>รหัสผ่านใหม่สั้นเกินไป ควรตั้งตามกฏเบื้องต้นดังนี้</b><br>
        1. ควรมีความยาว <span class='text-success'>อย่างน้อย 8 ตัวอักษร</span><br>
        2. ควรประกอบด้วยภาษาอังกฤษ <span class='text-success'>ตัวเล็กปนตัวใหญ่</span><br>
        3. ควรประกอบด้วย <span class='text-success'>สัญลักษณ์พิเศษ เช่น @ ! # %</span>
        </div>
        """
        response = JsonResponse(data={
            "success": True,
            "is_error": True,
            "message": message,
        })
        response.status_code = 200
        return response
    elif(re.search('[A-Z]+', new_password1) is None):
        response = JsonResponse(data={
            "success": True,
            "is_error": True,
            "message": "รหัสผ่านควรประกอบด้วยอักษรภาษาอังกฤษตัวใหญ่",
        })
        response.status_code = 200
        return response 
    elif(re.search('[a-z]+', new_password1) is None):
        response = JsonResponse(data={
            "success": True,
            "is_error": True,
            "message": "รหัสผ่านควรประกอบด้วยอักษรภาษาอังกฤษตัวเล็ก",
        })
        response.status_code = 200
        return response
    elif(re.search('[^A-Za-z0-9]+', new_password1) is None):
        response = JsonResponse(data={
            "success": True,
            "is_error": True,
            "message": "รหัสผ่านควรประกอบด้วยอักษรพิเศษ",
        })
        response.status_code = 200
        return response
    elif(new_password1 in excluded_password):
        response = JsonResponse(data={
            "success": True,
            "is_error": True,
            "message": "ไม่ควรใช้รหัสผ่านตั้งต้น",
        })
        response.status_code = 200
        return response

    employee_info = UserPasswordLog.objects.filter(emp_id=emp_id).get()    
    if employee_info is not None:
        # Update password log
        employee_info.is_password_changed = True
        employee_info.save()

        # Update password
        # print "Hashed password is:", make_password("plain_text")        
        try:            
            user_info = User.objects.filter(username=emp_id).get()
        except User.DoesNotExist:
            user_info = None
        if user_info is not None:
            user_info.password = make_password(new_password1)
            user_info.save()

        is_error = False
        message = "ตั้งรหัสผ่านใหม่สำเร็จ กรุณาเข้าระบบใหม่อีกครั้ง"
    else:
        is_error = True
        message = "No record found."
    
    response = JsonResponse(data={
        "success": True,
        "is_error": is_error,
        "message": message,
    })

    response.status_code = 200
    return response
