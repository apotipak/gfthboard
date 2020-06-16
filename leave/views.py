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
from .forms import EmployeeForm
from .form_m1817 import EmployeeM1817Form
from .form_m1247 import EmployeeM1247Form


excluded_username = {'900590','580816','900630'}
current_year = datetime.now().year


@login_required(login_url='/accounts/login/')
def EmployeeNew(request):
    dattime_format = "%Y-%m-%d %H:%M:%S"

    page_title = settings.PROJECT_NAME
    db_server = settings.DATABASES['default']['HOST']
    project_name = settings.PROJECT_NAME
    project_version = settings.PROJECT_VERSION
    today_date = settings.TODAY_DATE
    
    render_template_name = 'leave/employeeinstance_form.html'
    
    if request.method == "POST":
        if request.user.groups.filter(name__in=['E-Leave Staff', 'E-Leave Manager', 'E-Leave-M1817-Staff', 'E-Leave-M1817-Manager']).exists():
            form = EmployeeM1817Form(request.POST, user=request.user)
            render_template_name = 'leave/m1817_form.html'
        elif request.user.groups.filter(name__in=['E-Leave-M1247-Staff', 'E-Leave-M1247-Manager']).exists():
            form = EmployeeM1247Form(request.POST, user=request.user)
            render_template_name = 'leave/m1247_form.html'
        else:
            form = EmployeeForm(request.POST, user=request.user)

        if form.is_valid():      
            start_date = form.cleaned_data['start_date']
            start_hour = form.cleaned_data['start_hour']
            start_minute = form.cleaned_data['end_minute']

            end_date = form.cleaned_data['end_date']
            end_hour = form.cleaned_data['end_hour']            
            end_minute = form.cleaned_data['end_minute']

            d1 = str(start_date) + ' ' + str(start_hour) + ':' + str(start_minute) + ':00'
            d2 = str(end_date) + ' ' + str(end_hour) + ':' + str(end_minute) + ':00'
            start_date = datetime.strptime(d1, dattime_format)
            end_date = datetime.strptime(d2, dattime_format)

            leave_type_id = form.cleaned_data['leave_type']
            username = request.user.username
            fullname = request.user.first_name + " " + request.user.last_name
            created_by = request.user.username                        

            employee = form.save(commit=False)

            employee.start_date = start_date
            employee.end_date = end_date
            employee.emp_id = request.user.username
            employee.created_by = request.user.username


            if request.user.groups.filter(name__in=['E-Leave Staff','E-Leave Manager', 'E-Leave-M1817-Staff', 'E-Leave-M1817-Manager']).exists():
                grand_total_hours = checkM1817BusinessRules('M1247', start_date, end_date)
                employee.lve_act = grand_total_hours // 8
                employee.lve_act_hr = grand_total_hours % 8
            elif request.user.groups.filter(name__in=['E-Leave-M1247-Staff', 'E-Leave-M1247-Manager']).exists():
                found_m1247_error = checkM1247BusinessRules('M1247', start_date, end_date)
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
                    
                    if settings.TURN_DUMMY_EMAIL_ON:
                        recipients = settings.DUMMY_EMAIL

                    mail.send(                        
                        recipients, # To
                        settings.DEFAULT_FROM_EMAIL, # From
                        subject = 'E-Leave: ' + employee_full_name + ' - ขออนุมัติวันลา',
                        message = 'E-Leave: ' + employee_full_name + ' - ขออนุมัติวันลา',
                        html_message = 'เรียน <strong>ผู้จัดการแผนก</strong><br><br>'
                            'พนักงานแจ้งใช้สิทธิ์วันลาตามรายละเอียดด้านล่าง<br><br>'                            
                            'ชื่อพนักงาน: <strong>' + employee_full_name + '</strong><br>'
                            'ประเภทการลา: <strong>' + str(leave_type_id) + '</strong><br>'
                            'ลาวันที่: <strong>' + str(start_date.strftime("%d-%b-%Y %H:%M")) + '</strong> ถึงวันที่ <strong>' + str(end_date.strftime("%d-%b-%Y %H:%M")) + '</strong><br>'
                            'จำนวน: <strong>' + day_hour_display + '</strong><br><br>'
                            'กรุณา <a href="http://27.254.207.51:8080">ล็อคอินที่นี่</a> เพื่อดำเนินการพิจารณาต่อไป<br>'
                            '<br><br>--This email was sent from E-Leave System<br>'
                            'ref: ' + str(ref) + '<br>'
                    )

            return HttpResponseRedirect('/leave/leave-history/?submitted=True')
              
    else:

        if request.user.groups.filter(name__in=['E-Leave Staff', 'E-Leave Manager', 'E-Leave-M1817-Staff', 'E-Leave-M1817-Manager']).exists():
            form = EmployeeM1817Form(user=request.user)            
            render_template_name = 'leave/m1817_form.html'
        elif request.user.groups.filter(name__in=['E-Leave-M1247-Staff', 'E-Leave-M1247-Manager']).exists():
            form = EmployeeM1247Form(user=request.user)
            render_template_name = 'leave/m1247_form.html'
        else:
            form = EmployeeForm(user=request.user)
    
    # Check number of waiting leave request
    waiting_for_approval_item = len(EmployeeInstance.objects.raw("select * from leave_employeeinstance as ei inner join leave_employee e on ei.emp_id = e.emp_id where ei.emp_id in (select emp_id from leave_employee where emp_spid=" + request.user.username + ") and ei.status in ('p')"))    
    
    # Check leave approval right
    if checkLeaveRequestApproval(request.user.username):
        able_to_approve_leave_request = True
    else:
        able_to_approve_leave_request = False


    return render(request, render_template_name, {
        'form': form,
        'page_title': settings.PROJECT_NAME,
        'today_date': settings.TODAY_DATE,
        'project_version': settings.PROJECT_VERSION,
        'db_server': settings.DATABASES['default']['HOST'],
        'project_name': settings.PROJECT_NAME,
        'waiting_for_approval_item': waiting_for_approval_item,
        'able_to_approve_leave_request': able_to_approve_leave_request,
    })


class EmployeeInstanceListView(PermissionRequiredMixin, generic.ListView):    
    #template_name = 'leave/employeeinstance_list.html'
    permission_required = ('leave.view_employeeinstance')
    page_title = settings.PROJECT_NAME
    db_server = settings.DATABASES['default']['HOST']
    project_name = settings.PROJECT_NAME
    project_version = settings.PROJECT_VERSION
    today_date = settings.TODAY_DATE    
    model = EmployeeInstance
    #paginate_by = 20    

    def get_context_data(self, **kwargs):
        context = super(EmployeeInstanceListView, self).get_context_data(**kwargs)

        # Check number of waiting leave request
        waiting_for_approval_item = len(EmployeeInstance.objects.raw("select * from leave_employeeinstance as ei inner join leave_employee e on ei.emp_id = e.emp_id where ei.emp_id in (select emp_id from leave_employee where emp_spid=" + self.request.user.username + ") and ei.status in ('p')"))    
        
        # Check leave approval right
        if checkLeaveRequestApproval(self.request.user.username):
            able_to_approve_leave_request = True
        else:
            able_to_approve_leave_request = False

        context.update({
            'page_title': settings.PROJECT_NAME,
            'today_date': settings.TODAY_DATE,
            'project_version': settings.PROJECT_VERSION,
            'db_server': settings.DATABASES['default']['HOST'],
            'project_name': settings.PROJECT_NAME,
            'waiting_for_approval_item': waiting_for_approval_item,
            'able_to_approve_leave_request': able_to_approve_leave_request,
        })
        return context

    def get_queryset(self):
        #return EmployeeInstance.objects.filter(emp_id__exact=self.request.user.username).exclude(status__exact='d').order_by('-created_date')
        return EmployeeInstance.objects.filter(emp_id__exact=self.request.user.username).order_by('-created_date')


class EmployeeInstanceDetailView(generic.DetailView):
    model = EmployeeInstance


class EmployeeInstanceDelete(PermissionRequiredMixin, DeleteView):
    permission_required = ('leave.view_employeeinstance')
    page_title = settings.PROJECT_NAME
    db_server = settings.DATABASES['default']['HOST']
    project_name = settings.PROJECT_NAME
    project_version = settings.PROJECT_VERSION
    today_date = settings.TODAY_DATE    
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
        context.update({
            'page_title': settings.PROJECT_NAME,
            'today_date': settings.TODAY_DATE,
            'project_version': settings.PROJECT_VERSION,
            'db_server': settings.DATABASES['default']['HOST'],
            'project_name': settings.PROJECT_NAME,
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
                    html_message = 'เรียน <strong>ผู้จัดการแผนก</strong><br><br>'
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
    page_title = settings.PROJECT_NAME
    db_server = settings.DATABASES['default']['HOST']
    project_name = settings.PROJECT_NAME
    project_version = settings.PROJECT_VERSION
    today_date = settings.TODAY_DATE    
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
        total_pending_lve_act_eleave = EmployeeInstance.objects.filter(emp_id__exact=username).filter(leave_type_id__exact=policy.lve_type_id).filter(status__in=('p')).aggregate(sum=Sum('lve_act'))['sum'] or 0
        total_pending_lve_act_hr_eleave = EmployeeInstance.objects.filter(emp_id__exact=username).filter(leave_type_id__exact=policy.lve_type_id).filter(status__in=('p')).aggregate(sum=Sum('lve_act_hr'))['sum'] or 0        
        grand_total_pending_eleave = total_pending_lve_act_hr_eleave + (total_pending_lve_act_eleave * 8)
        policy.total_pending_lve_act_eleave = grand_total_pending_eleave // 8
        policy.total_pending_lve_act_hr_eleave = grand_total_pending_eleave % 8  

        # จำนวน วัน/ช.ม. ที่อนุมัติแล้ว E-Leave
        total_approved_lve_act_eleave = EmployeeInstance.objects.filter(emp_id__exact=username).filter(leave_type_id__exact=policy.lve_type_id).filter(status__in=('a','C','F')).aggregate(sum=Sum('lve_act'))['sum'] or 0        
        total_approved_lve_act_hr_eleave = EmployeeInstance.objects.filter(emp_id__exact=username).filter(leave_type_id__exact=policy.lve_type_id).filter(status__in=('a','C','F')).aggregate(sum=Sum('lve_act_hr'))['sum'] or 0
        grand_total_approved_eleave = total_approved_lve_act_hr_eleave + (total_approved_lve_act_eleave * 8)
        policy.total_approved_lve_act_eleave = grand_total_approved_eleave // 8
        policy.total_approved_lve_act_hr_eleave = grand_total_approved_eleave % 8

        # จำนวนวันคงเหลือสุทธิ
        result = leave_plan_hour - (grand_total_lve_hrms + grand_total_approved_eleave + grand_total_pending_eleave)        
        total_day_remaining = result // 8
        total_hour_remaining = result % 8
        policy.total_day_remaining = total_day_remaining
        policy.total_hour_remaining = total_hour_remaining
    
    # Check number of waiting leave request
    waiting_for_approval_item = len(EmployeeInstance.objects.raw("select * from leave_employeeinstance as ei inner join leave_employee e on ei.emp_id = e.emp_id where ei.emp_id in (select emp_id from leave_employee where emp_spid=" + request.user.username + ") and ei.status in ('p')"))

    # Check leave approval right    
    if checkLeaveRequestApproval(request.user.username):
        able_to_approve_leave_request = True
    else:
        able_to_approve_leave_request = False

    return render(request, 'leave/leave_policy.html', {
        'page_title': settings.PROJECT_NAME,
        'today_date': settings.TODAY_DATE,
        'project_version': settings.PROJECT_VERSION,
        'db_server': settings.DATABASES['default']['HOST'],
        'project_name': settings.PROJECT_NAME,        
        'leave_policy': leave_policy,
        'waiting_for_approval_item': waiting_for_approval_item,
        'able_to_approve_leave_request': able_to_approve_leave_request,
    })


@permission_required('leave.approve_leaveplan', login_url='/accounts/login/')
def LeaveApproval(request):
    page_title = settings.PROJECT_NAME
    db_server = settings.DATABASES['default']['HOST']
    project_name = settings.PROJECT_NAME
    project_version = settings.PROJECT_VERSION
    today_date = settings.TODAY_DATE

    return render(request, 'leave/leave_policy.html', {
        'page_title': settings.PROJECT_NAME,
        'today_date': settings.TODAY_DATE,
        'project_version': settings.PROJECT_VERSION,
        'db_server': settings.DATABASES['default']['HOST'],
        'project_name': settings.PROJECT_NAME,        
        'leave_policy': leave_policy,
    })


class EmployeeCreate(PermissionRequiredMixin, CreateView):
    model = EmployeeInstance
    fields = '__all__'
    permission_required = 'leave.add_employeeinstance'


#class LeaveApprovalListView(PermissionRequiredMixin, generic.ListView):
class LeaveApprovalListView(generic.ListView):
    page_title = settings.PROJECT_NAME
    db_server = settings.DATABASES['default']['HOST']
    project_name = settings.PROJECT_NAME
    project_version = settings.PROJECT_VERSION
    today_date = settings.TODAY_DATE
    template_name = 'leave/leave_approval_list.html'
    #permission_required = ('leave.approve_leaveplan')
    model = EmployeeInstance
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super(LeaveApprovalListView, self).get_context_data(**kwargs)
        
        # Check number of waiting leave request
        waiting_for_approval_item = len(EmployeeInstance.objects.raw("select * from leave_employeeinstance as ei inner join leave_employee e on ei.emp_id = e.emp_id where ei.emp_id in (select emp_id from leave_employee where emp_spid=" + self.request.user.username + ") and ei.status in ('p')"))
        
        # Check leave approval right
        if checkLeaveRequestApproval(self.request.user.username):
            able_to_approve_leave_request = True
        else:
            able_to_approve_leave_request = False

        context.update({
            'page_title': settings.PROJECT_NAME,
            'today_date': settings.TODAY_DATE,
            'project_version': settings.PROJECT_VERSION,
            'db_server': settings.DATABASES['default']['HOST'],
            'project_name': settings.PROJECT_NAME,
            'waiting_for_approval_item': waiting_for_approval_item,
            'able_to_approve_leave_request': able_to_approve_leave_request
        })
        return context

    def get_queryset(self):
        return EmployeeInstance.objects.raw("select ei.id, ei.start_date, ei.end_date, ei.created_date, ei.created_by, ei.status, ei.emp_id, ei.leave_type_id, e.emp_fname_th, e.emp_lname_th from leave_employeeinstance as ei inner join leave_employee e on ei.emp_id = e.emp_id where ei.emp_id in (select emp_id from leave_employee where emp_spid=" + self.request.user.username + ") and ei.status in ('p') order by emp_id, start_date asc")


#@permission_required('leave.approve_leaveplan')
def EmployeeInstanceApprove(request, pk):
    page_title = settings.PROJECT_NAME
    db_server = settings.DATABASES['default']['HOST']
    project_name = settings.PROJECT_NAME
    project_version = settings.PROJECT_VERSION
    today_date = settings.TODAY_DATE    
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

        return HttpResponseRedirect(reverse('leave_approval'))
    
    leaveEmployee = LeaveEmployee.objects.get(emp_id=employee_leave_instance.emp_id)
    waiting_for_approval_item = len(EmployeeInstance.objects.raw("select * from leave_employeeinstance as ei inner join leave_employee e on ei.emp_id = e.emp_id where ei.emp_id in (select emp_id from leave_employee where emp_spid=" + request.user.username + ") and ei.status in ('p')"))    
    context = {
        'leave_employee': leaveEmployee,
        'employee_leave_instance': employee_leave_instance,
        'page_title': settings.PROJECT_NAME,
        'db_server': settings.DATABASES['default']['HOST'],
        'project_name': settings.PROJECT_NAME,
        'project_version': settings.PROJECT_VERSION,
        'today_date' : settings.TODAY_DATE,
        'waiting_for_approval_item': waiting_for_approval_item,
    }

    return render(request, 'leave/employeeinstance_approve.html', context)


#@permission_required('leave.approve_leaveplan')
def EmployeeInstanceReject(request, pk):
    page_title = settings.PROJECT_NAME
    db_server = settings.DATABASES['default']['HOST']
    project_name = settings.PROJECT_NAME
    project_version = settings.PROJECT_VERSION
    today_date = settings.TODAY_DATE   
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

        return HttpResponseRedirect(reverse('leave_approval'))

    leaveEmployee = LeaveEmployee.objects.get(emp_id=employee_leave_instance.emp_id)
    waiting_for_approval_item = len(EmployeeInstance.objects.raw("select * from leave_employeeinstance as ei inner join leave_employee e on ei.emp_id = e.emp_id where ei.emp_id in (select emp_id from leave_employee where emp_spid=" + request.user.username + ") and ei.status in ('p')"))
    context = {
        'leave_employee': leaveEmployee,
        'employee_leave_instance': employee_leave_instance,
        'page_title': settings.PROJECT_NAME,
        'db_server': settings.DATABASES['default']['HOST'],
        'project_name': settings.PROJECT_NAME,
        'project_version': settings.PROJECT_VERSION,
        'today_date' : settings.TODAY_DATE,
        'waiting_for_approval_item': waiting_for_approval_item
    }

    return render(request, 'leave/employeeinstance_reject.html', context)

@login_required(login_url='/accounts/login/')
def get_leave_reject_comment(request, pk):
    comment = EmployeeInstance.objects.filter(id__exact=pk).values('comment')[0] or None
    return JsonResponse(comment)
