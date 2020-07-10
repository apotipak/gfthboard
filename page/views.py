from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import HttpResponseRedirect
from leave.models import LeaveEmployee
from page.models import UserProfile, ComDivision
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
import json


@login_required(login_url='/accounts/login/')
def index(request):    
    user_language = getDefaultLanguage(request.user.username)
    translation.activate(user_language)
    
    TURN_ANNOUNCEMENT_ON = settings.TURN_ANNOUNCEMENT_ON
    ANNOUNCEMENT_MESSAGE = settings.ANNOUNCEMENT_MESSAGE

    if user_language == "th":
        username_display = LeaveEmployee.objects.filter(emp_id=request.user.username).values_list('emp_fname_th', flat=True).get()
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

    if user_language == "th":
        username_display = LeaveEmployee.objects.filter(emp_id=request.user.username).values_list('emp_fname_th', flat=True).get()
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
    
    if user_language == "th":
        username_display = LeaveEmployee.objects.filter(emp_id=request.user.username).values_list('emp_fname_th', flat=True).get()
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

    if user_language == "th":
        username_display = LeaveEmployee.objects.filter(emp_id=request.user.username).values_list('emp_fname_th', flat=True).get()
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
    item_per_page = 12
    user_language = getDefaultLanguage(request.user.username)
    translation.activate(user_language)

    page_title = settings.PROJECT_NAME
    db_server = settings.DATABASES['default']['HOST']
    project_name = settings.PROJECT_NAME
    project_version = settings.PROJECT_VERSION
    today_date = getDateFormatDisplay(user_language)
    EmployeeInstance = LeaveEmployee.EmployeeInstance(request)
    SuperVisorInstance = LeaveEmployee.SuperVisorInstance(request)
    TeamMemberList = LeaveEmployee.TeamMemberList(request)

    # Check leave approval right
    if checkLeaveRequestApproval(request.user.username):
        able_to_approve_leave_request = True
    else:
        able_to_approve_leave_request = False

    if user_language == "th":
        username_display = LeaveEmployee.objects.filter(emp_id=request.user.username).values_list('emp_fname_th', flat=True).get()
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
        }

    return render(request, 'page/staff_profile.html', context)


@login_required(login_url='/accounts/login/')
def viewallstaff(request):
    item_per_page = 20  
    user_language = getDefaultLanguage(request.user.username)
    translation.activate(user_language)
    if user_language == "th":
        username_display = LeaveEmployee.objects.filter(emp_id=request.user.username).values_list('emp_fname_th', flat=True).get()
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

    if user_language == "th":
        username_display = LeaveEmployee.objects.filter(emp_id=request.user.username).values_list('emp_fname_th', flat=True).get()
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

    if user_language == "th":
        username_display = LeaveEmployee.objects.filter(emp_id=request.user.username).values_list('emp_fname_th', flat=True).get()
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

    if user_language == "th":
        username_display = LeaveEmployee.objects.filter(emp_id=request.user.username).values_list('emp_fname_th', flat=True).get()
    else:
        username_display = LeaveEmployee.objects.filter(emp_id=request.user.username).values_list('emp_fname_en', flat=True).get()

    return render(request, 'page/news.html', {
        'page_title': page_title, 
        'project_name': project_name, 
        'project_version': project_version, 
        'db_server': db_server, 'today_date': today_date,
        'username_display' : username_display,
    })
