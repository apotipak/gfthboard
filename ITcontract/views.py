import sys
from django.utils import timezone
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from leave.models import LeavePlan, LeaveHoliday, LeaveEmployee, LeaveType
from .models import ITcontractDB_M
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
#from .rules import *
from page.rules import *
#from .forms import EmployeeForm
#from .form_m1817 import EmployeeM1817Form
#from .form_m1247 import EmployeeM1247Form
from django.core.files.storage import FileSystemStorage
from django.utils import translation
from django.core import serializers
import collections
from django.utils.timezone import now
import json
from django.utils.translation import ugettext as _
from django.db.models import CharField, Value


# excluded_username = {'900590','580816','900630'}
excluded_username = {}
current_year = datetime.now().year


@login_required(login_url='/accounts/login/')
def ITcontractPolicy(request):

    user_language = getDefaultLanguage(request.user.username)
    translation.activate(user_language)

    page_title = settings.PROJECT_NAME
    db_server = settings.DATABASES['default']['HOST']
    project_name = settings.PROJECT_NAME
    project_version = settings.PROJECT_VERSION
    # today_date = settings.TODAY_DATE
    today_date = getDateFormatDisplay(user_language)
    #leave_policy = LeavePlan.EmployeeLeavePolicy(request)
    ITcontractPolicy = ITcontractDB_M.ITcontractPolicy(request)

    username = request.user.username

    for item in ITcontractPolicy:
        dept = item.dept
        vendor = item.vendor
        description = item.description
        startdate = item.startdate
        enddate = item.enddate
        print(dept)

    ''' 
    # Check number of waiting leave request
    #waiting_for_approval_item = len(EmployeeInstance.objects.raw(
    #    "select * from leave_employeeinstance as ei inner join leave_employee e on ei.emp_id = e.emp_id where ei.emp_id in (select emp_id from leave_employee where emp_spid=" + request.user.username + ") and ei.status in ('p')"))

    # Check leave approval right
    if checkLeaveRequestApproval(request.user.username):
        able_to_approve_leave_request = True
    else:
        able_to_approve_leave_request = False
    '''
    if user_language == "th":
        username_display = LeaveEmployee.objects.filter(emp_id=request.user.username).values_list('emp_fname_th',
                                                                                                  flat=True).get()
    else:
        username_display = LeaveEmployee.objects.filter(emp_id=request.user.username).values_list('emp_fname_en',
                                                                                                  flat=True).get()

    return render(request,
        'ITcontract/ITcontract_policy.html', {
        'page_title': settings.PROJECT_NAME,
        'today_date': today_date,
        'project_version': settings.PROJECT_VERSION,
        'db_server': settings.DATABASES['default']['HOST'],
        'project_name': settings.PROJECT_NAME,
        '''
        'leave_policy': leave_policy,
        'waiting_for_approval_item': waiting_for_approval_item,
        'able_to_approve_leave_request': able_to_approve_leave_request,
        '''
        'user_language': user_language,
        'username_display': username_display,
        'ITcontractPolicy':  ITcontractPolicy,

    })


