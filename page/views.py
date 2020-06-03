from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf import settings
from leave.models import LeaveEmployee
from django.contrib.auth.models import User
from .forms import UserForm

@login_required(login_url='/accounts/login/')
def index(request):
	page_title = settings.PROJECT_NAME
	db_server = settings.DATABASES['default']['HOST']
	project_name = settings.PROJECT_NAME
	project_version = settings.PROJECT_VERSION
	today_date = settings.TODAY_DATE

	return render(request, 'index.html', {
        'page_title': page_title, 
        'project_name': project_name, 
        'project_version': project_version, 
        'db_server': db_server, 'today_date': today_date
    })

@login_required(login_url='/accounts/login/')
def StaffProfile(request):
    page_title = settings.PROJECT_NAME
    db_server = settings.DATABASES['default']['HOST']
    project_name = settings.PROJECT_NAME
    project_version = settings.PROJECT_VERSION
    today_date = settings.TODAY_DATE    
    EmployeeInstance = LeaveEmployee.EmployeeInstance(request)
    SuperVisorInstance = LeaveEmployee.SuperVisorInstance(request)
    TeamMemberList = LeaveEmployee.TeamMemberList(request)

    return render(request, 'page/staff_profile.html', {
        'page_title': page_title, 
        'project_name': project_name, 
        'project_version': project_version, 
        'db_server': db_server, 'today_date': today_date,
        'EmployeeInstance': EmployeeInstance,
        'SuperVisorInstance': SuperVisorInstance,
        'TeamMemberList': TeamMemberList,
    })

@login_required(login_url='/accounts/login/')
def StaffPassword(request):
    page_title = settings.PROJECT_NAME
    db_server = settings.DATABASES['default']['HOST']
    project_name = settings.PROJECT_NAME
    project_version = settings.PROJECT_VERSION
    today_date = settings.TODAY_DATE    

    form = UserForm(request.POST, user=request.user)
 
    if request.method == "POST":
        if form.is_valid():
            password = form.cleaned_data['password']
    else:
        form = UserForm(user=request.user)    
    
    return render(request, 'page/staff_password_form.html', {
        'form': form,
        'page_title': page_title, 
        'project_name': project_name, 
        'project_version': project_version, 
        'db_server': db_server, 'today_date': today_date,
    })
