from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import HttpResponseRedirect
from leave.models import LeaveEmployee
from page.models import UserProfile
from django.contrib.auth.models import User
from .forms import UserForm, LanguageForm
from django.http import HttpResponse
from leave.rules import *
from page.rules import *
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.utils import translation
from django.db.models import CharField, Value as V
from django.db.models.functions import Concat


@login_required(login_url='/accounts/login/')
def index(request):    
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
    today_date = settings.TODAY_DATE

    return render(request, 'index.html', {
        'page_title': page_title, 
        'project_name': project_name, 
        'project_version': project_version, 
        'db_server': db_server, 'today_date': today_date,
        'user_language': user_language,
        'username_display' : username_display,
    })

@login_required(login_url='/accounts/login/')
def StaffProfile(request):
    user_language = getDefaultLanguage(request.user.username)
    translation.activate(user_language)

    page_title = settings.PROJECT_NAME
    db_server = settings.DATABASES['default']['HOST']
    project_name = settings.PROJECT_NAME
    project_version = settings.PROJECT_VERSION
    today_date = settings.TODAY_DATE    
    EmployeeInstance = LeaveEmployee.EmployeeInstance(request)
    SuperVisorInstance = LeaveEmployee.SuperVisorInstance(request)
    TeamMemberList = LeaveEmployee.TeamMemberList(request)

    # Check leave approval right
    if checkLeaveRequestApproval(request.user.username):
        able_to_approve_leave_request = True
    else:
        able_to_approve_leave_request = False

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
    })

@login_required(login_url='/accounts/login/')
def StaffPassword(request):
    user_language = getDefaultLanguage(request.user.username)
    translation.activate(user_language)

    page_title = settings.PROJECT_NAME
    db_server = settings.DATABASES['default']['HOST']
    project_name = settings.PROJECT_NAME
    project_version = settings.PROJECT_VERSION
    today_date = settings.TODAY_DATE    

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
    
    return render(request, 'page/staff_password_form.html', {
        'form': form,
        'page_title': page_title, 
        'project_name': project_name, 
        'project_version': project_version, 
        'db_server': db_server, 'today_date': today_date,
    })


@login_required(login_url='/accounts/login/')
def StaffLanguage(request):
    user_language = getDefaultLanguage(request.user.username)
    translation.activate(user_language)

    page_title = settings.PROJECT_NAME
    db_server = settings.DATABASES['default']['HOST']
    project_name = settings.PROJECT_NAME
    project_version = settings.PROJECT_VERSION
    today_date = settings.TODAY_DATE    

    form = LanguageForm(request.POST, user=request.user)

    if request.method == "POST":
        if form.is_valid():
            language_code = form.cleaned_data['language_code']
            username = request.user.username
            userid = request.user.id

            if not UserProfile.objects.filter(username=username).exists():
                print("debug 1")
                UserProfile.objects.create(language=language_code, updated_by_id=userid, username=username)
            else:
                print("debug 2")
                employee = UserProfile.objects.get(username=username)
                employee.language = language_code
                employee.updated_by_id = userid
                employee.username = username
                employee.save()
            
            messages.success(request, _('A new language has been set.'))
            return HttpResponseRedirect('/staff-language')
    else:
        form = LanguageForm(user=request.user)    
    
    return render(request, 'page/staff_language.html', {
        'form': form,
        'page_title': page_title, 
        'project_name': project_name, 
        'project_version': project_version, 
        'db_server': db_server, 'today_date': today_date,
    })


@login_required(login_url='/accounts/login/')
def HelpEleave(request):
    user_language = getDefaultLanguage(request.user.username)
    translation.activate(user_language)

    page_title = settings.PROJECT_NAME
    db_server = settings.DATABASES['default']['HOST']
    project_name = settings.PROJECT_NAME
    project_version = settings.PROJECT_VERSION
    today_date = settings.TODAY_DATE   

    return render(request, 'page/help_eleave.html', {
        'page_title': page_title, 
        'project_name': project_name, 
        'project_version': project_version, 
        'db_server': db_server, 'today_date': today_date,
    })

