import sys
from django.utils import timezone
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from leave.models import LeavePlan, LeaveHoliday, LeaveEmployee, LeaveType
from .models import PrpoCompany
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
import django.db as db
from django.db import connection

# excluded_username = {'900590','580816','900630'}
excluded_username = {}
current_year = datetime.now().year


@login_required(login_url='/accounts/login/')
def v_prpo_company(request):

    user_language = getDefaultLanguage(request.user.username)
    translation.activate(user_language)

    page_title = settings.PROJECT_NAME
    db_server = settings.DATABASES['default']['HOST']
    project_name = settings.PROJECT_NAME
    project_version = settings.PROJECT_VERSION
    # today_date = settings.TODAY_DATE
    today_date = getDateFormatDisplay(user_language)
    #leave_policy = LeavePlan.EmployeeLeavePolicy(request)
    #prpocompany = PrpoCompany.prpocompanylist(request)

    username = request.user.username
    sql = "Select cpid ,cpname,cpaltername,cpshortcut from prpo_company order by cpid ";
    employee_expend_obj = None
    record = {}
    try:
        cursor = connection.cursor()
        cursor.execute(sql)
        prpocompanyInstance = cursor.fetchall()
    except db.OperationalError as e:
        is_error = True
        error_message = "<b>Error: please send this error to IT team</b><br>" + str(e)
    except db.Error as e:
        is_error = True
        error_message = "<b>Error: please send this error to IT team</b><br>" + str(e)
    finally:
        cursor.close()

    for item in prpocompanyInstance:
        cpid = item[0]
        cpname = item[1]
        cpaltername = item[2]
        cpshoutcut = item[3]
        #print(prpocompanyInstance)
        print(cpid)
    if user_language == "th":
        username_display = LeaveEmployee.objects.filter(emp_id=request.user.username).values_list('emp_fname_th',
                                                                                                  flat=True).get()
    else:
        username_display = LeaveEmployee.objects.filter(emp_id=request.user.username).values_list('emp_fname_en',
                                                                                                  flat=True).get()

    return render(request,
        'prpo/prpo_company.html', {
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
        'v_prpo_company':  prpocompanyInstance,

    })


