from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf import settings
from leave.models import LeaveEmployee


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

    return render(request, 'page/staff_password.html', {
        'page_title': page_title, 
        'project_name': project_name, 
        'project_version': project_version, 
        'db_server': db_server, 'today_date': today_date,
    })