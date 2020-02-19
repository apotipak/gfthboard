from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf import settings
from leave.models import LeaveEmployee


@login_required(login_url='/accounts/login/')
def index(request):
    return render(request, 'index.html', {})

@login_required(login_url='/accounts/login/')
def StaffProfile(request):
    EmployeeInstance = LeaveEmployee.EmployeeInstance(request)
    SuperVisorInstance = LeaveEmployee.SuperVisorInstance(request)
    TeamMemberList = LeaveEmployee.TeamMemberList(request)

    return render(request, 'page/staff_profile.html', {
        'EmployeeInstance': EmployeeInstance,
        'SuperVisorInstance': SuperVisorInstance,
        'TeamMemberList': TeamMemberList,
        })
