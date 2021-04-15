import sys
from django.utils import timezone
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from leave.models import LeavePlan, LeaveHoliday, LeaveEmployee, LeaveType
from .models import EmployeeInstance
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
from .rules import *
from page.rules import *
from .forms import EmployeeForm
from .form_m1817 import EmployeeM1817Form
from .form_m1247 import EmployeeM1247Form
from django.core.files.storage import FileSystemStorage
from django.utils import translation
from django.core import serializers
import collections
from django.utils.timezone import now
from base64 import decodestring
from django.core.files import File
from django.utils.translation import ugettext as _
from django.db.models import CharField, Value
import json
import re, io
import django.db as db
from django.db import connection
from django.http import FileResponse
from base64 import b64encode


# excluded_username = {'900590','580816','900630'}
excluded_username = {}
current_year = datetime.now().year


@login_required(login_url='/accounts/login/')
def m1817_check_leave_request_day(request):
    result = {}
    total_day = 0
    total_hour = 0
    error = ""
    leave_type_id = request.GET['leave_type_id']
    start_date = request.GET['start_date']
    end_date = request.GET['end_date']

    start_date = datetime.strptime(start_date, "%Y-%m-%d %H:%M:00")
    end_date = datetime.strptime(end_date, "%Y-%m-%d %H:%M:00")

    found_m1817_error = checkM1817TotalHours('M1817', start_date, end_date, leave_type_id)
    if found_m1817_error[0]:
        result = {
            'total_day' : 0,
            'total_hour' : 0,
            'error': found_m1817_error[1],
        }
    else:
        count = found_m1817_error[1]
        result = {
            'total_day' : count // 8,
            'total_hour' : count % 8,
            'error': "",
        }        

    return JsonResponse(result)


@login_required(login_url='/accounts/login/')
def m1247_check_leave_request_day(request):
    result = {}
    total_day = 0
    total_hour = 0
    leave_type_id = request.GET['leave_type_id']
    start_date = request.GET['start_date']
    end_date = request.GET['end_date']

    start_date = datetime.strptime(start_date, "%Y-%m-%d %H:%M:00")
    end_date = datetime.strptime(end_date, "%Y-%m-%d %H:%M:00")

    count = checkM1247TotalHours("m1247", start_date, end_date, leave_type_id)
    
    # print("count1 : " + str(count))

    if count != 0:
        if count.is_integer():
            result = {
                'total_day' : count // 8,
                'total_hour' : count % 8,
                'error' : "",
            }
            #return True, _("ช่วงวันลามีเศษครึ่งชั่วโมง")
        else:                
            result = {
                'total_day' : count // 8,
                'total_hour' : count % 8,
                'error' : "ช่วงวันลามีเศษครึ่งชั่วโมง",
            }
    else:
        result = {
            'total_day' : count // 8,
            'total_hour' : count % 8,
            'error' : "เลือกช่วงวันลาไม่ถูกต้อง",
        }

    return JsonResponse(result)


@login_required(login_url='/accounts/login/')
def EmployeeNew(request):
    user_language = getDefaultLanguage(request.user.username)
    translation.activate(user_language)
    
    dattime_format = "%Y-%m-%d %H:%M:%S"

    page_title = settings.PROJECT_NAME
    db_server = settings.DATABASES['default']['HOST']
    project_name = settings.PROJECT_NAME
    project_version = settings.PROJECT_VERSION
    # today_date = settings.TODAY_DATE
    today_date = getDateFormatDisplay(user_language)
    
    # render_template_name = 'leave/employeeinstance_form.html'
    
    if request.method == "POST":
        '''        
        if request.user.groups.filter(name__in=['E-Leave Staff', 'E-Leave Manager', 'E-Leave-M1817-Staff', 'E-Leave-M1817-Manager']).exists():
            form = EmployeeM1817Form(request.POST, request.FILES, user=request.user)
            render_template_name = 'leave/m1817_form.html'
        elif request.user.groups.filter(name__in=['E-Leave-M1247-Staff', 'E-Leave-M1247-Manager']).exists():
            form = EmployeeM1247Form(request.POST, request.FILES, user=request.user)
            render_template_name = 'leave/m1247_form.html'
        else:
            form = EmployeeForm(request.POST, user=request.user)
        '''

        form = EmployeeM1247Form(request.POST, request.FILES, user=request.user)
        render_template_name = 'leave/m1247_form.html'

        if form.is_valid():           
            start_date = form.cleaned_data['start_date']
            start_hour = form.cleaned_data['start_hour']
            start_minute = form.cleaned_data['start_minute']

            end_date = form.cleaned_data['end_date']
            end_hour = form.cleaned_data['end_hour']            
            end_minute = form.cleaned_data['end_minute']

            d1 = str(start_date) + ' ' + str(start_hour) + ':' + str(start_minute) + ':00'
            d2 = str(end_date) + ' ' + str(end_hour) + ':' + str(end_minute) + ':00'
            start_date = datetime.strptime(d1, dattime_format)
            end_date = datetime.strptime(d2, dattime_format)

            leave_type_id = form.data['leave_type']
            leave_type = form.cleaned_data['leave_type']
            leave_reason = form.cleaned_data['leave_reason']
            username = request.user.username
            fullname = request.user.first_name + " " + request.user.last_name
            created_by = request.user.username                        

            employee = form.save(commit=False)

            employee.start_date = start_date
            employee.end_date = end_date
            employee.emp_id = request.user.username
            employee.created_by = request.user.username
            employee.leave_reason = leave_reason

            # employee.document_data = request.FILES['document'].read()

            '''
            if request.user.groups.filter(name__in=['E-Leave Staff','E-Leave Manager', 'E-Leave-M1817-Staff', 'E-Leave-M1817-Manager']).exists():
                grand_total_hours = checkM1817BusinessRules('M1817', start_date, end_date, leave_type_id)
                employee.lve_act = grand_total_hours // 8
                employee.lve_act_hr = grand_total_hours % 8
            elif request.user.groups.filter(name__in=['E-Leave-M1247-Staff', 'E-Leave-M1247-Manager']).exists():
                found_m1247_error = checkM1247BusinessRules('M1247', start_date, end_date, leave_type_id)
                if found_m1247_error[0]:
                    raise forms.ValidationError(found_m1247_error[1])
                else:
                    grand_total_hours = found_m1247_error[1]

                employee.lve_act = grand_total_hours // 8
                employee.lve_act_hr = grand_total_hours % 8
            '''
            
            found_m1247_error = checkM1247BusinessRules('M1247', start_date, end_date, leave_type_id)
            if found_m1247_error[0]:
                raise forms.ValidationError(found_m1247_error[1])
            else:
                grand_total_hours = found_m1247_error[1]

            employee.lve_act = grand_total_hours // 8
            employee.lve_act_hr = grand_total_hours % 8
        
            employee.save()
            ref = employee.id 

            day_hour_display = ""
            if grand_total_hours // 8 > 0:
                day_hour_display += str(grand_total_hours // 8) + ' วัน '
            if grand_total_hours % 8 > 0:
                day_hour_display += str(grand_total_hours % 8) + ' ช.ม.'

            # EMPLOYEE SENDS LEAVE REQUEST EMAIL
            if request.user.username not in excluded_username:

                if settings.TURN_SEND_MAIL_ON:                    
                    employee = LeaveEmployee.objects.get(emp_id=request.user.username)
                    supervisor_id = employee.emp_spid
                    supervisor = User.objects.get(username=supervisor_id)
                    supervisor_email = supervisor.email
                    recipients = [supervisor_email]                
                    employee_full_name = employee.emp_fname_th + ' ' + employee.emp_lname_th
                    supervisor_obj = LeaveEmployee.objects.get(emp_id=supervisor_id)
                    supervisor_fullname = supervisor_obj.emp_fname_th + " " + supervisor_obj.emp_lname_th
                    
                    if settings.TURN_DUMMY_EMAIL_ON:
                        recipients = settings.DUMMY_EMAIL

                    if len(leave_reason) <= 0:
                        leave_reason = _('There is no reason provided.')

                    mail.send(                        
                        recipients, # To
                        settings.DEFAULT_FROM_EMAIL, # From
                        subject = 'E-Leave: ' + employee_full_name + ' - ขออนุมัติวันลา',
                        message = 'E-Leave: ' + employee_full_name + ' - ขออนุมัติวันลา',
                        html_message = 'เรียน คุณ <strong>' + supervisor_fullname + '</strong><br><br>'
                            'พนักงานแจ้งใช้สิทธิ์วันลาตามรายละเอียดด้านล่าง<br><br>'                            
                            'ชื่อพนักงาน: <strong>' + employee_full_name + '</strong><br>'
                            'ประเภทการลา: <strong>' + str(leave_type) + '</strong><br>'
                            'ลาวันที่: <strong>' + str(start_date.strftime("%d-%b-%Y %H:%M")) + '</strong> ถึงวันที่ <strong>' + str(end_date.strftime("%d-%b-%Y %H:%M")) + '</strong><br>'
                            'จำนวน: <strong>' + day_hour_display + '</strong><br>'
                            'เหตุผลการลา: <strong>' + leave_reason + '</strong><br><br>'
                            'กรุณา <a href="http://27.254.207.51:8080">ล็อคอินที่นี่</a> เพื่อดำเนินการพิจารณาต่อไป<br>'
                            '<br><br>--This email was sent from E-Leave System<br>'
                            'ref: ' + str(ref) + '<br>'
                    )

            return HttpResponseRedirect('/leave/leave-history/?submitted=True')
              
    else:
        '''
        if request.user.groups.filter(name__in=['E-Leave Staff', 'E-Leave Manager', 'E-Leave-M1817-Staff', 'E-Leave-M1817-Manager']).exists():
            form = EmployeeM1817Form(user=request.user)            
            render_template_name = 'leave/m1817_form.html'
        elif request.user.groups.filter(name__in=['E-Leave-M1247-Staff', 'E-Leave-M1247-Manager']).exists():
            form = EmployeeM1247Form(user=request.user)
            render_template_name = 'leave/m1247_form.html'
        else:
            form = EmployeeForm(user=request.user)
        '''

        form = EmployeeM1247Form(user=request.user)
        render_template_name = 'leave/m1247_form.html'
        
    # Check number of waiting leave request
    # waiting_for_approval_item = len(EmployeeInstance.objects.raw("select * from leave_employeeinstance as ei inner join leave_employee e on ei.emp_id = e.emp_id where ei.emp_id in (select emp_id from leave_employee where emp_spid=" + request.user.username + ") and ei.status in ('p')"))
    waiting_for_approval_item = len(EmployeeInstance.objects.raw("select * from leave_employeeinstance as ei inner join leave_employee e on ei.emp_id = e.emp_id where ei.emp_id in (select emp_id from leave_employee where emp_spid=" + request.user.username + ") and ei.status in ('p') and year(end_date)='2021'"))     
    
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

    return render(request, render_template_name, {
        'form': form,
        'page_title': settings.PROJECT_NAME,
        'today_date': today_date,
        'project_version': settings.PROJECT_VERSION,
        'db_server': settings.DATABASES['default']['HOST'],
        'project_name': settings.PROJECT_NAME,
        'waiting_for_approval_item': waiting_for_approval_item,
        'able_to_approve_leave_request': able_to_approve_leave_request,
        'user_language': user_language,
        'username_display': username_display,
    })


class EmployeeInstanceListView(PermissionRequiredMixin, generic.ListView):    

    #template_name = 'leave/employeeinstance_list.html'
    permission_required = ('leave.view_employeeinstance')
    page_title = settings.PROJECT_NAME
    db_server = settings.DATABASES['default']['HOST']
    project_name = settings.PROJECT_NAME
    project_version = settings.PROJECT_VERSION
    model = EmployeeInstance
    #paginate_by = 20    

    def get_context_data(self, **kwargs):
        user_language = getDefaultLanguage(self.request.user.username)
        translation.activate(user_language)

        context = super(EmployeeInstanceListView, self).get_context_data(**kwargs)

        # Check number of waiting leave request
        # waiting_for_approval_item = len(EmployeeInstance.objects.raw("select * from leave_employeeinstance as ei inner join leave_employee e on ei.emp_id = e.emp_id where ei.emp_id in (select emp_id from leave_employee where emp_spid=" + self.request.user.username + ") and ei.status in ('p')"))    
        waiting_for_approval_item = len(EmployeeInstance.objects.raw("select * from leave_employeeinstance as ei inner join leave_employee e on ei.emp_id = e.emp_id where ei.emp_id in (select emp_id from leave_employee where emp_spid=" + self.request.user.username + ") and ei.status in ('p') and year(end_date)='2021'"))
        
        
        # Check leave approval right
        if checkLeaveRequestApproval(self.request.user.username):
            able_to_approve_leave_request = True
        else:
            able_to_approve_leave_request = False

        '''
        if user_language == "th":
            username_display = LeaveEmployee.objects.filter(emp_id=self.request.user.username).values_list('emp_fname_th', flat=True).get()
        else:
            username_display = LeaveEmployee.objects.filter(emp_id=self.request.user.username).values_list('emp_fname_en', flat=True).get()
        '''

        if user_language == "th":
            if self.request.user.username == "999999":
                username_display = request.user.first_name
            else:            
                username_display = LeaveEmployee.objects.filter(emp_id=self.request.user.username).values_list('emp_fname_th', flat=True).get()
        else:
            if self.request.user.username == "999999":
                username_display = request.user.first_name
            else:                    
                username_display = LeaveEmployee.objects.filter(emp_id=self.request.user.username).values_list('emp_fname_en', flat=True).get()


        # today_date = settings.TODAY_DATE
        today_date = getDateFormatDisplay(user_language)

        context.update({
            'page_title': settings.PROJECT_NAME,
            'today_date': today_date,
            'project_version': settings.PROJECT_VERSION,
            'db_server': settings.DATABASES['default']['HOST'],
            'project_name': settings.PROJECT_NAME,
            'waiting_for_approval_item': waiting_for_approval_item,
            'able_to_approve_leave_request': able_to_approve_leave_request,
            'user_language': user_language,
            'username_display': username_display,
        })
        return context

    def get_queryset(self):
        # return EmployeeInstance.objects.filter(emp_id__exact=self.request.user.username).exclude(status__exact='d').order_by('-created_date')        
        return EmployeeInstance.objects.filter(emp_id__exact=self.request.user.username).filter(end_date__year='2021').exclude(status__exact='d').order_by('-created_date')
        #return EmployeeInstance.objects.filter(emp_id__exact=self.request.user.username).order_by('-created_date')


class EmployeeInstanceDetailView(generic.DetailView):
    model = EmployeeInstance


class EmployeeInstanceDelete(PermissionRequiredMixin, DeleteView):    
    permission_required = ('leave.view_employeeinstance')
    page_title = settings.PROJECT_NAME
    db_server = settings.DATABASES['default']['HOST']
    project_name = settings.PROJECT_NAME
    project_version = settings.PROJECT_VERSION
    model = EmployeeInstance
    paginate_by = 10
    permission_required = 'leave.view_employeeinstance'
    template_name = "leave/employeeinstance_confirm_delete.html"
    success_url = reverse_lazy('leave_history')
    success_message = "Deleted Successfully"

    def delete(self, *args, **kwargs):
        success_url = self.get_success_url()
        self.object = self.get_object()          
        self.object.status = 'd'
        self.object.updated_by = self.request.user.username
        self.object.updated_date  = timezone.now()                
        self.object.save()
        
        return HttpResponseRedirect(success_url)

    def get_context_data(self, **kwargs):        
        context = super(EmployeeInstanceDelete, self).get_context_data(**kwargs)

        user_language = getDefaultLanguage(self.request.user.username)
        translation.activate(user_language)

        '''
        if user_language == "th":
            username_display = LeaveEmployee.objects.filter(emp_id=self.request.user.username).values_list('emp_fname_th', flat=True).get()
        else:
            username_display = LeaveEmployee.objects.filter(emp_id=self.request.user.username).values_list('emp_fname_en', flat=True).get()
        '''

        if user_language == "th":
            if self.request.user.username == "999999":
                username_display = self.request.user.first_name
            else:            
                username_display = LeaveEmployee.objects.filter(emp_id=self.request.user.username).values_list('emp_fname_th', flat=True).get()
        else:
            if self.request.user.username == "999999":
                username_display = self.request.user.first_name
            else:                    
                username_display = LeaveEmployee.objects.filter(emp_id=self.request.user.username).values_list('emp_fname_en', flat=True).get()


        # today_date = settings.TODAY_DATE
        today_date = getDateFormatDisplay(user_language)

        context.update({
            'page_title': settings.PROJECT_NAME,
            'today_date': today_date,
            'project_version': settings.PROJECT_VERSION,
            'db_server': settings.DATABASES['default']['HOST'],
            'project_name': settings.PROJECT_NAME,
            'username_display': username_display,
        })

        return context

    def get_success_url(self, **kwargs):

        if self.request.user.username not in excluded_username:

            if settings.TURN_SEND_MAIL_ON:
                self.object = self.get_object()

                username = self.request.user.username
                fullname = self.request.user.first_name + " " + self.request.user.last_name
                created_by = self.request.user.username                        

                emp_id = self.request.user.username
                employee = LeaveEmployee.objects.get(emp_id=emp_id)
                supervisor_id = employee.emp_spid
                supervisor = User.objects.get(username=supervisor_id)
                supervisor_email = supervisor.email
                employee_full_name = employee.emp_fname_th + ' ' + employee.emp_lname_th
                supervisor_obj = LeaveEmployee.objects.get(emp_id=supervisor_id)
                supervisor_fullname = supervisor_obj.emp_fname_th + " " + supervisor_obj.emp_lname_th

                recipients = [supervisor_email]
                
                start_date = self.object.start_date
                end_date = self.object.end_date
                leave_type_id = self.object.leave_type_id
                leave_type_name = LeaveType.objects.filter(lve_id__exact=leave_type_id).values_list('lve_th', flat=True).get()
                day = self.object.lve_act
                hour = self.object.lve_act_hr
                ref = self.object.id

                day_hour_display = ""
                if day > 0:
                    day_hour_display += str(day) + ' วัน '

                if hour > 0:
                    day_hour_display += str(hour) + ' ช.ม.'

                if settings.TURN_DUMMY_EMAIL_ON:
                    recipients = settings.DUMMY_EMAIL

                mail.send(                        
                    recipients, # To
                    settings.DEFAULT_FROM_EMAIL, # From
                    subject = 'E-Leave: ' + employee_full_name + ' - แจ้งยกเลิกวันลา',
                    message = 'E-Leave: ' + employee_full_name + ' - แจ้งยกเลิกวันลา',
                    html_message = 'เรียน คุณ <strong>' + supervisor_fullname + '</strong><br><br>'
                        'มีการขอแจ้งยกเลิกวันลาตามรายละเอียดด้านล่าง<br><br>'
                        'ชื่อพนักงาน: <strong>' + employee_full_name + '</strong><br>'
                        'ประเภทการลา: <strong>' + str(leave_type_name) + '</strong><br>'
                        'ลาวันที่: <strong>' + str(start_date.strftime("%d-%b-%Y %H:%M")) + '</strong> ถึงวันที่ <strong>' + str(end_date.strftime("%d-%b-%Y %H:%M")) + '</strong><br>'
                        'จำนวน: <strong>' + day_hour_display + '</strong><br>'
                        '<br><br>--This email was sent from E-Leave System<br>'
                        'ref: ' + str(ref) + '<br>'
                )            

        return reverse_lazy('leave_history')

    def get_queryset(self):
        owner = self.request.user.username
        return self.model.objects.filter(emp_id=owner)


@login_required(login_url='/accounts/login/')
def LeavePolicy(request):
    user_language = getDefaultLanguage(request.user.username)
    translation.activate(user_language)

    page_title = settings.PROJECT_NAME
    db_server = settings.DATABASES['default']['HOST']
    project_name = settings.PROJECT_NAME
    project_version = settings.PROJECT_VERSION
    # today_date = settings.TODAY_DATE
    today_date = getDateFormatDisplay(user_language)
    leave_policy = LeavePlan.EmployeeLeavePolicy(request)

    username = request.user.username

    for policy in leave_policy:

        leave_plan_day = policy.lve_plan
        leave_plan_hour = policy.lve_plan * 8

        # จำนวน วัน/ช.ม. ที่ใช้ใน HRMS
        total_lve_act = policy.lve_act
        total_lve_act_hr = policy.lve_act_hr
        grand_total_lve_act_hr = total_lve_act_hr + (total_lve_act * 8)

        # จำนวน วัน/ช.ม. คงเหลือใน HRMS
        total_lve_miss = policy.lve_miss
        total_lve_miss_hr = policy.lve_miss_hr
        grand_total_lve_miss_hr = total_lve_miss_hr + (total_lve_miss * 8)

        # จำนวน วัน/ช.ม. ที่ใช้ใน HRMS 2
        total_lve_hrms = policy.lve_HRMS
        total_lve_hrms_hr = policy.lve_HRMS_HR
        grand_total_lve_hrms = total_lve_hrms_hr + (total_lve_hrms * 8)


        # จำนวน วัน/ช.ม. ที่รออนุมัติใน E-Leave
        total_pending_lve_act_eleave = EmployeeInstance.objects.filter(emp_id__exact=username).filter(end_date__year='2021').filter(leave_type_id__exact=policy.lve_type_id).filter(status__in=('p')).aggregate(sum=Sum('lve_act'))['sum'] or 0
        total_pending_lve_act_hr_eleave = EmployeeInstance.objects.filter(emp_id__exact=username).filter(end_date__year='2021').filter(leave_type_id__exact=policy.lve_type_id).filter(status__in=('p')).aggregate(sum=Sum('lve_act_hr'))['sum'] or 0        
        grand_total_pending_eleave = total_pending_lve_act_hr_eleave + (total_pending_lve_act_eleave * 8)
        policy.total_pending_lve_act_eleave = grand_total_pending_eleave // 8
        policy.total_pending_lve_act_hr_eleave = grand_total_pending_eleave % 8  

        # จำนวน วัน/ช.ม. ที่อนุมัติแล้ว E-Leave
        # total_approved_lve_act_eleave = EmployeeInstance.objects.filter(emp_id__exact=username).filter(leave_type_id__exact=policy.lve_type_id).filter(status__in=('a','C','F')).aggregate(sum=Sum('lve_act'))['sum'] or 0
        total_approved_lve_act_eleave = EmployeeInstance.objects.filter(emp_id__exact=username).filter(end_date__year='2021').filter(leave_type_id__exact=policy.lve_type_id).filter(status__in=('a','C','F')).aggregate(sum=Sum('lve_act'))['sum'] or 0        

        # total_approved_lve_act_hr_eleave = EmployeeInstance.objects.filter(emp_id__exact=username).filter(leave_type_id__exact=policy.lve_type_id).filter(status__in=('a','C','F')).aggregate(sum=Sum('lve_act_hr'))['sum'] or 0
        total_approved_lve_act_hr_eleave = EmployeeInstance.objects.filter(emp_id__exact=username).filter(end_date__year='2021').filter(leave_type_id__exact=policy.lve_type_id).filter(status__in=('a','C','F')).aggregate(sum=Sum('lve_act_hr'))['sum'] or 0

        grand_total_approved_eleave = total_approved_lve_act_hr_eleave + (total_approved_lve_act_eleave * 8)
        policy.total_approved_lve_act_eleave = grand_total_approved_eleave // 8
        policy.total_approved_lve_act_hr_eleave = grand_total_approved_eleave % 8

        print("total_approved_lve_act_eleave", total_approved_lve_act_eleave)

        # จำนวนวันคงเหลือสุทธิ
        result = leave_plan_hour - (grand_total_lve_hrms + grand_total_approved_eleave + grand_total_pending_eleave)        
        total_day_remaining = result // 8
        total_hour_remaining = result % 8
        policy.total_day_remaining = total_day_remaining
        policy.total_hour_remaining = total_hour_remaining
    
    # Check number of waiting leave request
    # waiting_for_approval_item = len(EmployeeInstance.objects.raw("select * from leave_employeeinstance as ei inner join leave_employee e on ei.emp_id = e.emp_id where ei.emp_id in (select emp_id from leave_employee where emp_spid=" + request.user.username + ") and ei.status in ('p')"))
    waiting_for_approval_item = len(EmployeeInstance.objects.raw("select * from leave_employeeinstance as ei inner join leave_employee e on ei.emp_id = e.emp_id where ei.emp_id in (select emp_id from leave_employee where emp_spid=" + request.user.username + ") and ei.status in ('p') and year(end_date)='2021'"))

    print("waiting_for_approval_item", waiting_for_approval_item)

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


    return render(request, 'leave/leave_policy.html', {
        'page_title': settings.PROJECT_NAME,
        'today_date': today_date,
        'project_version': settings.PROJECT_VERSION,
        'db_server': settings.DATABASES['default']['HOST'],
        'project_name': settings.PROJECT_NAME,        
        'leave_policy': leave_policy,
        'waiting_for_approval_item': waiting_for_approval_item,
        'able_to_approve_leave_request': able_to_approve_leave_request,
        'user_language': user_language,
        'username_display': username_display,
    })


@permission_required('leave.approve_leaveplan', login_url='/accounts/login/')
def LeaveApproval(request):
    user_language = getDefaultLanguage(request.user.username)
    translation.activate(user_language)

    page_title = settings.PROJECT_NAME
    db_server = settings.DATABASES['default']['HOST']
    project_name = settings.PROJECT_NAME
    project_version = settings.PROJECT_VERSION
    # today_date = settings.TODAY_DATE
    today_date = getDateFormatDisplay(user_language)

    return render(request, 'leave/leave_policy.html', {
        'page_title': settings.PROJECT_NAME,
        'today_date': today_date,
        'project_version': settings.PROJECT_VERSION,
        'db_server': settings.DATABASES['default']['HOST'],
        'project_name': settings.PROJECT_NAME,        
        'leave_policy': leave_policy,
    })


class EmployeeCreate(PermissionRequiredMixin, CreateView):
    model = EmployeeInstance
    fields = '__all__'
    permission_required = 'leave.add_employeeinstance'


class LeavePendingApproveListView(PermissionRequiredMixin, generic.ListView):
    page_title = settings.PROJECT_NAME
    db_server = settings.DATABASES['default']['HOST']
    project_name = settings.PROJECT_NAME
    project_version = settings.PROJECT_VERSION
    template_name = 'leave/leave_pending_approve_list.html'
    permission_required = ('leave.approve_leaveplan')
    model = EmployeeInstance
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super(LeavePendingApproveListView, self).get_context_data(**kwargs)

        user_language = getDefaultLanguage(self.request.user.username)
        translation.activate(user_language)
        today_date = getDateFormatDisplay(user_language)
        
        # Check number of waiting leave request
        # waiting_for_approval_item = len(EmployeeInstance.objects.raw("select * from leave_employeeinstance as ei inner join leave_employee e on ei.emp_id = e.emp_id where ei.emp_id in (select emp_id from leave_employee where emp_spid=" + self.request.user.username + ") and ei.status in ('p')"))
        waiting_for_approval_item = len(EmployeeInstance.objects.raw("select * from leave_employeeinstance as ei inner join leave_employee e on ei.emp_id = e.emp_id where ei.emp_id in (select emp_id from leave_employee where emp_spid=" + self.request.user.username + ") and ei.status in ('p') and year(end_date)='2021'"))        
        
        # Check leave approval right
        if checkLeaveRequestApproval(self.request.user.username):
            able_to_approve_leave_request = True
        else:
            able_to_approve_leave_request = False

        '''
        if user_language == "th":
            username_display = LeaveEmployee.objects.filter(emp_id=self.request.user.username).values_list('emp_fname_th', flat=True).get()
        else:
            username_display = LeaveEmployee.objects.filter(emp_id=self.request.user.username).values_list('emp_fname_en', flat=True).get()
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


        context.update({
            'page_title': settings.PROJECT_NAME,
            'today_date': today_date,
            'project_version': settings.PROJECT_VERSION,
            'db_server': settings.DATABASES['default']['HOST'],
            'project_name': settings.PROJECT_NAME,
            'waiting_for_approval_item': waiting_for_approval_item,
            'able_to_approve_leave_request': able_to_approve_leave_request,
            'username_display': username_display,
        })
        return context

    def get_queryset(self):
        # return EmployeeInstance.objects.raw("select ei.id, ei.start_date, ei.end_date, ei.created_date, ei.created_by, ei.status, ei.emp_id, ei.leave_type_id, e.emp_fname_th, e.emp_lname_th from leave_employeeinstance as ei inner join leave_employee e on ei.emp_id = e.emp_id where ei.emp_id in (select emp_id from leave_employee where emp_spid=" + self.request.user.username + ") and ei.status in ('p') order by emp_id, start_date asc")
        # return EmployeeInstance.objects.raw("select ei.id, ei.start_date, ei.end_date, ei.created_date, ei.created_by, ei.status, ei.emp_id, ei.leave_type_id, e.emp_fname_th, e.emp_lname_th from leave_employeeinstance as ei inner join leave_employee e on ei.emp_id = e.emp_id where ei.emp_id in (select emp_id from leave_employee where emp_spid=" + self.request.user.username + ") and ei.status in ('p') order by created_date")
        return EmployeeInstance.objects.raw("select ei.id, ei.start_date, ei.end_date, ei.created_date, ei.created_by, ei.status, ei.emp_id, ei.leave_type_id, e.emp_fname_th, e.emp_lname_th from leave_employeeinstance as ei inner join leave_employee e on ei.emp_id = e.emp_id where ei.emp_id in (select emp_id from leave_employee where emp_spid=" + self.request.user.username + ") and ei.status in ('p') and year(end_date)='2021' order by created_date")
                

class LeaveApprovedListView(PermissionRequiredMixin, generic.ListView):
    page_title = settings.PROJECT_NAME
    db_server = settings.DATABASES['default']['HOST']
    project_name = settings.PROJECT_NAME
    project_version = settings.PROJECT_VERSION
    template_name = 'leave/leave_approved_list.html'
    permission_required = ('leave.approve_leaveplan')
    model = EmployeeInstance
    #paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super(LeaveApprovedListView, self).get_context_data(**kwargs)

        user_language = getDefaultLanguage(self.request.user.username)
        translation.activate(user_language)
        today_date = getDateFormatDisplay(user_language)
        
        # Check number of waiting leave request
        # waiting_for_approval_item = len(EmployeeInstance.objects.raw("select * from leave_employeeinstance as ei inner join leave_employee e on ei.emp_id = e.emp_id where ei.emp_id in (select emp_id from leave_employee where emp_spid=" + self.request.user.username + ") and ei.status in ('p')"))
        waiting_for_approval_item = len(EmployeeInstance.objects.raw("select * from leave_employeeinstance as ei inner join leave_employee e on ei.emp_id = e.emp_id where ei.emp_id in (select emp_id from leave_employee where emp_spid=" + self.request.user.username + ") and ei.status in ('p') and year(end_date)='2021'"))
                
        # Check leave approval right
        if checkLeaveRequestApproval(self.request.user.username):
            able_to_approve_leave_request = True
        else:
            able_to_approve_leave_request = False

        '''
        if user_language == "th":
            username_display = LeaveEmployee.objects.filter(emp_id=self.request.user.username).values_list('emp_fname_th', flat=True).get()
        else:
            username_display = LeaveEmployee.objects.filter(emp_id=self.request.user.username).values_list('emp_fname_en', flat=True).get()
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


        context.update({
            'page_title': settings.PROJECT_NAME,
            'today_date': today_date,
            'project_version': settings.PROJECT_VERSION,
            'db_server': settings.DATABASES['default']['HOST'],
            'project_name': settings.PROJECT_NAME,
            'waiting_for_approval_item': waiting_for_approval_item,
            'able_to_approve_leave_request': able_to_approve_leave_request,
            'username_display': username_display,
        })
        return context

    def get_queryset(self):
        # return EmployeeInstance.objects.raw("select ei.id, ei.start_date, ei.end_date, ei.created_date, ei.created_by, ei.status, ei.emp_id, ei.leave_type_id, e.emp_fname_th, e.emp_lname_th from leave_employeeinstance as ei inner join leave_employee e on ei.emp_id = e.emp_id where ei.emp_id in (select emp_id from leave_employee where emp_spid=" + self.request.user.username + ") and ei.status in ('a','C','F') order by updated_date desc")
        return EmployeeInstance.objects.raw("select ei.id, ei.start_date, ei.end_date, ei.created_date, ei.created_by, ei.status, ei.emp_id, ei.leave_type_id, e.emp_fname_th, e.emp_lname_th from leave_employeeinstance as ei inner join leave_employee e on ei.emp_id = e.emp_id where ei.emp_id in (select emp_id from leave_employee where emp_spid=" + self.request.user.username + ") and ei.status in ('a','C','F') and year(end_date)='2021' order by updated_date desc")
        

class LeaveRejectedListView(PermissionRequiredMixin, generic.ListView):
    page_title = settings.PROJECT_NAME
    db_server = settings.DATABASES['default']['HOST']
    project_name = settings.PROJECT_NAME
    project_version = settings.PROJECT_VERSION
    template_name = 'leave/leave_rejected_list.html'
    permission_required = ('leave.approve_leaveplan')
    model = EmployeeInstance
    #paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super(LeaveRejectedListView, self).get_context_data(**kwargs)

        user_language = getDefaultLanguage(self.request.user.username)
        translation.activate(user_language)
        # today_date = settings.TODAY_DATE
        today_date = getDateFormatDisplay(user_language)
        
        # Check number of waiting leave request
        # waiting_for_approval_item = len(EmployeeInstance.objects.raw("select * from leave_employeeinstance as ei inner join leave_employee e on ei.emp_id = e.emp_id where ei.emp_id in (select emp_id from leave_employee where emp_spid=" + self.request.user.username + ") and ei.status in ('p')"))
        waiting_for_approval_item = len(EmployeeInstance.objects.raw("select * from leave_employeeinstance as ei inner join leave_employee e on ei.emp_id = e.emp_id where ei.emp_id in (select emp_id from leave_employee where emp_spid=" + self.request.user.username + ") and ei.status in ('p') and year(end_date)='2021'"))
        

        # Check leave approval right
        if checkLeaveRequestApproval(self.request.user.username):
            able_to_approve_leave_request = True
        else:
            able_to_approve_leave_request = False

        '''
        if user_language == "th":
            username_display = LeaveEmployee.objects.filter(emp_id=self.request.user.username).values_list('emp_fname_th', flat=True).get()
        else:
            username_display = LeaveEmployee.objects.filter(emp_id=self.request.user.username).values_list('emp_fname_en', flat=True).get()
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


        context.update({
            'page_title': settings.PROJECT_NAME,
            'today_date': today_date,
            'project_version': settings.PROJECT_VERSION,
            'db_server': settings.DATABASES['default']['HOST'],
            'project_name': settings.PROJECT_NAME,
            'waiting_for_approval_item': waiting_for_approval_item,
            'able_to_approve_leave_request': able_to_approve_leave_request,
            'username_display': username_display,
        })
        return context

    def get_queryset(self):
        # return EmployeeInstance.objects.raw("select ei.id, ei.start_date, ei.end_date, ei.created_date, ei.created_by, ei.status, ei.comment, ei.emp_id, ei.leave_type_id, e.emp_fname_th, e.emp_lname_th from leave_employeeinstance as ei inner join leave_employee e on ei.emp_id = e.emp_id where ei.emp_id in (select emp_id from leave_employee where emp_spid=" + self.request.user.username + ") and ei.status in ('r') order by updated_date desc")
        return EmployeeInstance.objects.raw("select ei.id, ei.start_date, ei.end_date, ei.created_date, ei.created_by, ei.status, ei.comment, ei.emp_id, ei.leave_type_id, e.emp_fname_th, e.emp_lname_th from leave_employeeinstance as ei inner join leave_employee e on ei.emp_id = e.emp_id where ei.emp_id in (select emp_id from leave_employee where emp_spid=" + self.request.user.username + ") and ei.status in ('r') and year(end_date)='2021' order by updated_date desc")
        

#@permission_required('leave.approve_leaveplan')
def EmployeeInstanceApprove(request, pk):
    user_language = getDefaultLanguage(request.user.username)
    translation.activate(user_language)

    page_title = settings.PROJECT_NAME
    db_server = settings.DATABASES['default']['HOST']
    project_name = settings.PROJECT_NAME
    project_version = settings.PROJECT_VERSION
    # today_date = settings.TODAY_DATE
    today_date = getDateFormatDisplay(user_language)
    employee_leave_instance = get_object_or_404(EmployeeInstance, pk=pk)

    if request.method == 'POST':
        employee_leave_instance.status = 'a'
        employee_leave_instance.updated_by = request.user.username
        employee_leave_instance.updated_date = datetime.now()
        employee_leave_instance.save()

        # TODO: Send mail funciton
        if request.user.username not in excluded_username:
            if settings.TURN_SEND_MAIL_ON:
                employee = User.objects.get(username=employee_leave_instance.emp_id)

                employeeobj = LeaveEmployee.objects.get(emp_id=employee_leave_instance.emp_id)
                employee_first_name = employeeobj.emp_fname_th
                employee_last_name = employeeobj.emp_lname_th
                employee_full_name = employee_first_name + ' ' + employee_last_name

                recipients = [employee.email]
                start_date = employee_leave_instance.start_date.strftime("%d-%b-%Y %H:%M")
                end_date = employee_leave_instance.end_date.strftime("%d-%b-%Y %H:%M")
                leave_type = employee_leave_instance.leave_type
                day = employee_leave_instance.lve_act
                hour = employee_leave_instance.lve_act_hr
                ref = pk
                day_hour_display = ""
                if day > 0:
                    day_hour_display += str(day) + ' วัน '

                if hour > 0:
                    day_hour_display += str(hour) + ' ช.ม.'

                if settings.TURN_DUMMY_EMAIL_ON:
                    recipients = settings.DUMMY_EMAIL

                mail.send(                        
                    recipients, # To
                    settings.DEFAULT_FROM_EMAIL, # From
                    subject = 'E-Leave: แจ้งอนุมัติวันลา',
                    message = 'E-Leave: แจ้งอนุมัติวันลา',
                    html_message = 'เรียน คุณ <strong>' + employee_full_name + '</strong><br><br>'
                        'ผู้จัดการของท่านแจ้ง <strong>อนุมัติ</strong> การใช้สิทธิ์วันลาตามรายละเอียดด้านล่าง<br><br>'
                        'ประเภทการลา: <strong>' + str(leave_type) + '</strong><br>'
                        'วันที่: <strong>' + start_date + '</strong> ถึง <strong>' + end_date + '</strong><br>'
                        'จำนวน: <strong>' + day_hour_display + '</strong><br>'
                        'สถานะ: <strong>อนุมัติ</strong><br><br>'
                        'สามารถเข้าสู่ระบบเพื่อดูรายละเอียดเพิ่มเติมได้ <a href="http://27.254.207.51:8080">ที่นี่</a><br>'
                        '<br><br>--This email was sent from E-Leave System<br>'
                        'ref: ' + str(ref) + '<br>'
                )

        return HttpResponseRedirect(reverse('leave_approve_pending_list'))
    
    leaveEmployee = LeaveEmployee.objects.get(emp_id=employee_leave_instance.emp_id)
    # waiting_for_approval_item = len(EmployeeInstance.objects.raw("select * from leave_employeeinstance as ei inner join leave_employee e on ei.emp_id = e.emp_id where ei.emp_id in (select emp_id from leave_employee where emp_spid=" + request.user.username + ") and ei.status in ('p')"))    
    waiting_for_approval_item = len(EmployeeInstance.objects.raw("select * from leave_employeeinstance as ei inner join leave_employee e on ei.emp_id = e.emp_id where ei.emp_id in (select emp_id from leave_employee where emp_spid=" + request.user.username + ") and ei.status in ('p') and year(end_date)='2021'"))    

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

    context = {
        'leave_employee': leaveEmployee,
        'employee_leave_instance': employee_leave_instance,
        'page_title': settings.PROJECT_NAME,
        'db_server': settings.DATABASES['default']['HOST'],
        'project_name': settings.PROJECT_NAME,
        'project_version': settings.PROJECT_VERSION,
        'today_date' : today_date,
        'waiting_for_approval_item': waiting_for_approval_item,
        'username_display': username_display,
    }

    return render(request, 'leave/employeeinstance_approve.html', context)


#@permission_required('leave.approve_leaveplan')
def EmployeeInstanceReject(request, pk):
    user_language = getDefaultLanguage(request.user.username)
    translation.activate(user_language)

    page_title = settings.PROJECT_NAME
    db_server = settings.DATABASES['default']['HOST']
    project_name = settings.PROJECT_NAME
    project_version = settings.PROJECT_VERSION
    # today_date = settings.TODAY_DATE
    today_date = getDateFormatDisplay(user_language)
    employee_leave_instance = get_object_or_404(EmployeeInstance, pk=pk)

    if request.method == 'POST':
        employee_leave_instance.status = 'r'
        employee_leave_instance.updated_by = request.user.username
        employee_leave_instance.updated_date = datetime.now()
        comment = request.POST.get('comment')
        employee_leave_instance.comment = comment
        employee_leave_instance.save()

        if len(comment) <= 0:
            comment = "ไม่ได้ระบุเหตุผล"

        if request.user.username not in excluded_username:

            # TODO: Send mail funciton
            if settings.TURN_SEND_MAIL_ON:
                employee = User.objects.get(username=employee_leave_instance.emp_id)
                recipients = [employee.email]

                employee = LeaveEmployee.objects.get(emp_id=employee_leave_instance.emp_id)
                employee_first_name = employee.emp_fname_th
                employee_last_name = employee.emp_lname_th
                employee_full_name = employee_first_name + ' ' + employee_last_name

                start_date = employee_leave_instance.start_date.strftime("%d-%b-%Y %H:%M")
                end_date = employee_leave_instance.end_date.strftime("%d-%b-%Y %H:%M")
                leave_type = employee_leave_instance.leave_type            
                day = employee_leave_instance.lve_act
                hour = employee_leave_instance.lve_act_hr
                ref = pk

                day_hour_display = ""
                if day > 0:
                    day_hour_display += str(day) + ' วัน '
                if hour > 0:
                    day_hour_display += str(hour) + ' ช.ม.'
                                        
                if settings.TURN_DUMMY_EMAIL_ON:
                    recipients = settings.DUMMY_EMAIL

                mail.send(
                    recipients, # To
                    settings.DEFAULT_FROM_EMAIL, # From
                    subject = 'E-Leave: แจ้งไม่อนุมัติวันลา',
                    message = 'E-Leave: แจ้งไม่อนุมัติวันลา',
                    html_message = 'เรียน คุณ <strong>' + employee_full_name + '</strong><br><br>'
                        'ผู้จัดการของท่านแจ้ง <strong>ไม่อนุมัติ</strong> การใช้สิทธิ์วันลาตามรายละเอียดด้านล่าง<br><br>'
                        'ประเภทการลา: <strong>' + str(leave_type) + '</strong><br>'
                        'วันที่: <strong>' + start_date + '</strong> ถึง <strong>' + end_date + '</strong><br>'
                        'จำนวน: <strong>' + day_hour_display + '</strong><br>'
                        'สถานะ: <strong>ไม่อนุมัติ</strong><br>'
                        'เหตุผล: <strong>' + comment +'</strong><br><br>'
                        'สามารถเข้าสู่ระบบเพื่อดูรายละเอียดเพิ่มเติมได้ <a href="http://27.254.207.51:8080">ที่นี่</a><br><br><br>'                        
                        '--This email was sent from E-Leave System<br>'
                        'ref: ' + str(ref) + '<br>'
                )

        return HttpResponseRedirect(reverse('leave_approve_pending_list'))

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


    leaveEmployee = LeaveEmployee.objects.get(emp_id=employee_leave_instance.emp_id)
    # waiting_for_approval_item = len(EmployeeInstance.objects.raw("select * from leave_employeeinstance as ei inner join leave_employee e on ei.emp_id = e.emp_id where ei.emp_id in (select emp_id from leave_employee where emp_spid=" + request.user.username + ") and ei.status in ('p')"))
    waiting_for_approval_item = len(EmployeeInstance.objects.raw("select * from leave_employeeinstance as ei inner join leave_employee e on ei.emp_id = e.emp_id where ei.emp_id in (select emp_id from leave_employee where emp_spid=" + request.user.username + ") and ei.status in ('p') and year(end_date)='2021'"))
    
    context = {
        'leave_employee': leaveEmployee,
        'employee_leave_instance': employee_leave_instance,
        'page_title': settings.PROJECT_NAME,
        'db_server': settings.DATABASES['default']['HOST'],
        'project_name': settings.PROJECT_NAME,
        'project_version': settings.PROJECT_VERSION,
        'today_date' : today_date,
        'waiting_for_approval_item': waiting_for_approval_item,
        'username_display': username_display,
    }

    return render(request, 'leave/employeeinstance_reject.html', context)


@login_required(login_url='/accounts/login/')
def get_leave_reject_comment(request, pk):
    comment = EmployeeInstance.objects.filter(id__exact=pk).values('comment')[0] or None
    return JsonResponse(comment)


@login_required(login_url='/accounts/login/')
def get_leave_reason(request, pk):    
    reason = EmployeeInstance.objects.filter(id__exact=pk).values('leave_reason')[0] or None
    return JsonResponse(reason)


@login_required(login_url='/accounts/login/')
def GetEmployeeEntitlementRemaining(request, check_employee_id):
    leave_policy = LeavePlan.EmployeeLeavePolicy(request)

    username = check_employee_id

    for policy in leave_policy:

        leave_plan_day = policy.lve_plan
        leave_plan_hour = policy.lve_plan * 8

        # จำนวน วัน/ช.ม. ที่ใช้ใน HRMS
        total_lve_act = policy.lve_act
        total_lve_act_hr = policy.lve_act_hr
        grand_total_lve_act_hr = total_lve_act_hr + (total_lve_act * 8)

        # จำนวน วัน/ช.ม. คงเหลือใน HRMS
        total_lve_miss = policy.lve_miss
        total_lve_miss_hr = policy.lve_miss_hr
        grand_total_lve_miss_hr = total_lve_miss_hr + (total_lve_miss * 8)

        # จำนวน วัน/ช.ม. ที่ใช้ใน HRMS 2
        total_lve_hrms = policy.lve_HRMS
        total_lve_hrms_hr = policy.lve_HRMS_HR
        grand_total_lve_hrms = total_lve_hrms_hr + (total_lve_hrms * 8)


        # จำนวน วัน/ช.ม. ที่รออนุมัติใน E-Leave
        total_pending_lve_act_eleave = EmployeeInstance.objects.filter(emp_id__exact=username).filter(end_date__year='2021').filter(leave_type_id__exact=policy.lve_type_id).filter(status__in=('p')).aggregate(sum=Sum('lve_act'))['sum'] or 0
        total_pending_lve_act_hr_eleave = EmployeeInstance.objects.filter(emp_id__exact=username).filter(end_date__year='2021').filter(leave_type_id__exact=policy.lve_type_id).filter(status__in=('p')).aggregate(sum=Sum('lve_act_hr'))['sum'] or 0        
        grand_total_pending_eleave = total_pending_lve_act_hr_eleave + (total_pending_lve_act_eleave * 8)
        policy.total_pending_lve_act_eleave = grand_total_pending_eleave // 8
        policy.total_pending_lve_act_hr_eleave = grand_total_pending_eleave % 8  

        # จำนวน วัน/ช.ม. ที่อนุมัติแล้ว E-Leave
        total_approved_lve_act_eleave = EmployeeInstance.objects.filter(emp_id__exact=username).filter(end_date__year='2021').filter(leave_type_id__exact=policy.lve_type_id).filter(status__in=('a','C','F')).aggregate(sum=Sum('lve_act'))['sum'] or 0        
        total_approved_lve_act_hr_eleave = EmployeeInstance.objects.filter(emp_id__exact=username).filter(end_date__year='2021').filter(leave_type_id__exact=policy.lve_type_id).filter(status__in=('a','C','F')).aggregate(sum=Sum('lve_act_hr'))['sum'] or 0
        grand_total_approved_eleave = total_approved_lve_act_hr_eleave + (total_approved_lve_act_eleave * 8)
        policy.total_approved_lve_act_eleave = grand_total_approved_eleave // 8
        policy.total_approved_lve_act_hr_eleave = grand_total_approved_eleave % 8

        # จำนวนวันคงเหลือสุทธิ
        result = leave_plan_hour - (grand_total_lve_hrms + grand_total_approved_eleave + grand_total_pending_eleave)        
        total_day_remaining = result // 8
        total_hour_remaining = result % 8
        policy.total_day_remaining = total_day_remaining
        policy.total_hour_remaining = total_hour_remaining
    
    return leave_policy
#---------------------------------------------------------------------------------------

@login_required(login_url='/accounts/login/')
def get_employee_leave_history_approved (request, emp_id):
    employee = LeaveEmployee.objects.filter(emp_id=emp_id).get() or None
    now = datetime.now()
    LeaveYear = str(now.year)
    pickup_records = []
    employee_leave_plan = EmployeeInstance.objects.raw(
        "Select ei.id , ei.emp_id, lve_th,lve_id,start_date,end_date,lve_act,lve_act_hr from leave_employeeinstance Ei inner join leave_type lt on ei.leave_type_id=lt.lve_id  where Ei.emp_id = " +emp_id+ "  and  year(start_date) = "+ LeaveYear
        +"and status in ( 'C' )   order by start_date Desc"
        )

    user_language = getDefaultLanguage(request.user.username)
    translation.activate(user_language)
    fullname = employee.emp_fname_th + " " + employee.emp_lname_th


    pickup_dict = {}
    pickup_records = []

    if employee_leave_plan:
        for l in employee_leave_plan:
            record = {
                    "emp_id": l.emp_id,
                    "fullname": fullname,  # ชื่อพนักงาน  lve_en,lve_id,start_date,end_date,lve_act,lve_act_hr
                    "leave_name": l.lve_th,  # ชื่อประเภทวันลา
                    "start_date": l.start_date.strftime("%d-%b-%Y %H:%M"),  # จำนวนวัน
                    "end_date": l.end_date.strftime("%d-%b-%Y %H:%M"),  # จำนวนชั่วโมงที
                    "lve_act": l.lve_act,  # จำนวนวัน
                    "lve_act_hr": l.lve_act_hr,  # จำนวนชั่วโมงที
                    "entitlement_year": LeaveYear,
            }
            pickup_records.append(record)
        response = JsonResponse(data={"success": True, "results": list(pickup_records)})
        response.status_code = 200

        return response
    else:
        response = JsonResponse({"error": "there was an error"})
        response.status_code = 403
        return response

    return JsonResponse(data={"success": False, "results": ""})
#--------------------------------------------------------------------------------------



@login_required(login_url='/accounts/login/')
def get_employee_leave_history(request, emp_id):        

    employee = LeaveEmployee.objects.filter(emp_id=emp_id) or None
    now = datetime.now()
    LeaveYear = str(now.year)
    employee_leave_plan = LeavePlan.objects.raw("select lp.emp_id as id, lp.lve_year, lt.lve_id as lve_type_id, lp.lve_code, lp.lve_plan, lt.lve_th, lt.lve_en, lp.lve_act, lp.lve_act_hr, lp.lve_miss, lp.lve_miss_hr, lp.lve_HRMS, lp.lve_HRMS_HR from leave_plan lp inner join leave_type lt on lp.lve_id=lt.lve_id where lp.emp_id=" + emp_id + " and lp.lve_year=" + LeaveYear)
    
    user_language = getDefaultLanguage(request.user.username)
    translation.activate(user_language)    

    if employee_leave_plan:
        pickup_dict = {}
        pickup_records=[]

        for e in employee:
            if user_language == 'th':
                fullname = e.emp_fname_th + " " + e.emp_lname_th
            else:
                fullname = e.emp_fname_en + " " + e.emp_lname_en

            for l in employee_leave_plan:

                leave_plan_day = l.lve_plan
                leave_plan_hour = l.lve_plan * 8

                # จำนวน วัน/ช.ม. ที่ใช้ใน HRMS 2
                total_lve_hrms = l.lve_HRMS
                total_lve_hrms_hr = l.lve_HRMS_HR
                grand_total_lve_hrms = total_lve_hrms_hr + (total_lve_hrms * 8)

                # จำนวน วัน/ช.ม. ที่อนุมัติแล้ว E-Leave
                total_approved_lve_act_eleave_obj = EmployeeInstance.objects.filter(emp_id__exact=emp_id).filter(end_date__year='2021').filter(leave_type_id__exact=l.lve_type_id).filter(status__in=('a','C','F')).aggregate(sum=Sum('lve_act'))['sum'] or 0        
                total_approved_lve_act_hr_eleave_obj = EmployeeInstance.objects.filter(emp_id__exact=emp_id).filter(end_date__year='2021').filter(leave_type_id__exact=l.lve_type_id).filter(status__in=('a','C','F')).aggregate(sum=Sum('lve_act_hr'))['sum'] or 0
                grand_total_approved_eleave = total_approved_lve_act_hr_eleave_obj + (total_approved_lve_act_eleave_obj * 8)
                total_approved_lve_act_eleave = grand_total_approved_eleave // 8
                total_approved_lve_act_hr_eleave = grand_total_approved_eleave % 8

                # จำนวน วัน/ช.ม. ที่รออนุมัติใน E-Leave
                total_pending_lve_act_eleave_obj = EmployeeInstance.objects.filter(emp_id__exact=emp_id).filter(end_date__year='2021').filter(leave_type_id__exact=l.lve_type_id).filter(status__in=('p')).aggregate(sum=Sum('lve_act'))['sum'] or 0
                total_pending_lve_act_hr_eleave_obj = EmployeeInstance.objects.filter(emp_id__exact=emp_id).filter(end_date__year='2021').filter(leave_type_id__exact=l.lve_type_id).filter(status__in=('p')).aggregate(sum=Sum('lve_act_hr'))['sum'] or 0        
                grand_total_pending_eleave = total_pending_lve_act_hr_eleave_obj + (total_pending_lve_act_eleave_obj * 8)
                total_pending_lve_act_eleave = grand_total_pending_eleave // 8
                total_pending_lve_act_hr_eleave = grand_total_pending_eleave % 8  

                # จำนวนวันคงเหลือสุทธิ
                result = leave_plan_hour - (grand_total_lve_hrms + grand_total_approved_eleave + grand_total_pending_eleave)        
                total_day_remaining = result // 8
                total_hour_remaining = result % 8

                # จำนวนวันที่ใช้สุทธิ (รวมวันจากระบบ HRMS และ E-Leave)
                total_day_used = (grand_total_lve_hrms // 8) + total_approved_lve_act_eleave
                total_hour_used = (grand_total_lve_hrms % 8) + total_approved_lve_act_hr_eleave
                combined_day_hour = (total_day_used * 8) + total_hour_used
                total_day_used = combined_day_hour // 8
                total_hour_used = combined_day_hour % 8

                # Timeline
                # leave_approved_items = EmployeeInstance.objects.annotate(mycolumn=Value('xxx', output_field=CharField())).filter(emp_id__exact=emp_id).filter(status__in=('a','C','F')).only("start_date","end_date","leave_type","lve_act","lve_act_hr").order_by('-start_date') or None
                leave_approved_items = EmployeeInstance.objects.filter(emp_id__exact=emp_id).filter(end_date__year='2021').filter(status__in=('a','C','F')).order_by('-start_date') or None
                leave_type_list = serializers.serialize('json', LeaveType.objects.all())

                if leave_approved_items:
                    timeline = serializers.serialize('json', leave_approved_items)
                else:
                    timeline = serializers.serialize('json', {})

                record = {
                    "emp_id":e.emp_id, 
                    "fullname": fullname, # ชื่อพนักงาน
                    "leave_name": l.lve_th, # ชื่อประเภทวันลา
                    "leave_plan": leave_plan_day, # สิทธิ์วันลา
                    "total_day_remaining": total_day_remaining, # วันลาคงเหลือ
                    "total_hour_remaining": total_hour_remaining, # ชั่วโมงลาคงเหลือ
                    "total_day_used": total_day_used, # จำนวนวันที่ใช้ไป
                    "total_hour_used": total_hour_used, # จำนวนชั่วโมงที่ใช้ไป
                    "total_day_pending": total_pending_lve_act_eleave, # จำนวนวันที่รออนุมัติ
                    "total_hour_pending": total_pending_lve_act_hr_eleave, # จำนวนชั่วโมงที่รออนุมัติ
                    "entitlement_year": LeaveYear,
                    "timeline": timeline,
                    "leave_type_list": leave_type_list,
                }

                pickup_records.append(record)

        response = JsonResponse(data={"success": True, "results": list(pickup_records)})
        response.status_code = 200

        return response
    else:
        response = JsonResponse({"error": "there was an error"})
        response.status_code = 403
        return response

    return JsonResponse(data={"success": False, "results": ""})


@login_required(login_url='/accounts/login/')
def LeaveTimeline(request):
    user_language = getDefaultLanguage(request.user.username)
    translation.activate(user_language)

    page_title = settings.PROJECT_NAME
    db_server = settings.DATABASES['default']['HOST']
    project_name = settings.PROJECT_NAME
    project_version = settings.PROJECT_VERSION
    today_date = settings.TODAY_DATE.strftime("%Y-%m-%d")
    #today_date = getDateFormatDisplay(user_language)
    leave_policy = LeavePlan.EmployeeLeavePolicy(request)

    # Check number of waiting leave request
    # waiting_for_approval_item = len(EmployeeInstance.objects.raw("select * from leave_employeeinstance as ei inner join leave_employee e on ei.emp_id = e.emp_id where ei.emp_id in (select emp_id from leave_employee where emp_spid=" + request.user.username + ") and ei.status in ('p')"))
    waiting_for_approval_item = len(EmployeeInstance.objects.raw("select * from leave_employeeinstance as ei inner join leave_employee e on ei.emp_id = e.emp_id where ei.emp_id in (select emp_id from leave_employee where emp_spid=" + request.user.username + ") and ei.status in ('p') and year(end_date)='2021'"))    

    username = request.user.username

    leave_approved_items = EmployeeInstance.objects.filter(emp_id__exact=username).filter(status__in=('a','C','F')).filter(end_date__year='2021').order_by('-start_date') or None

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

    context = {
        'page_title': settings.PROJECT_NAME,
        'db_server': settings.DATABASES['default']['HOST'],
        'project_name': settings.PROJECT_NAME,
        'project_version': settings.PROJECT_VERSION,
        'today_date' : today_date,
        'leave_approved_items': leave_approved_items,
        'able_to_approve_leave_request': able_to_approve_leave_request,
        'user_language': user_language,
        'username_display': username_display,
        'waiting_for_approval_item': waiting_for_approval_item,
    }

    return render(request, 'leave/leave_timeline.html', context)


@login_required(login_url='/accounts/login/')
def get_pdf_file(request, pk):
    result = {}
    total_day = 0
    total_hour = 0

    print(pk)

    sql = "select document, document_data from leave_employeeinstance where id='%s';" % (pk)

    document_obj = EmployeeInstance.objects.filter(id__exact=pk).get()
    print(document_obj.document)

    write_document_data = open('media/' + str(document_obj.document), 'wb').write(document_obj.document_data)
    document_data = open('media/' + str(document_obj.document), 'rb')    
    

    '''    
    try:
        with connection.cursor() as cursor:     
            cursor.execute(sql)
            document_obj = cursor.fetchone()
        
    finally:
        cursor.close()

    write_document_data = open('media/' + document_obj[0], 'wb').write(document_obj[1])
    document_data = open('media/' + document_obj[0], 'rb')
    '''

    response = FileResponse(document_data)
    return response

