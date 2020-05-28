from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from leave.models import LeavePlan, LeaveHoliday, LeaveEmployee
from .models import EmployeeInstance
from .forms import EmployeeForm
from django.urls import reverse_lazy
from django.shortcuts import render_to_response
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
from django.contrib.auth.models import User
from datetime import timedelta, datetime
import sys


class EmployeeInstanceListView(PermissionRequiredMixin, generic.ListView):
    #template_name = 'leave/employeeinstance_list.html'
    permission_required = ('leave.view_employeeinstance')
    page_title = settings.PROJECT_NAME
    db_server = settings.DATABASES['default']['HOST']
    project_name = settings.PROJECT_NAME
    project_version = settings.PROJECT_VERSION
    today_date = settings.TODAY_DATE    
    model = EmployeeInstance
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super(EmployeeInstanceListView, self).get_context_data(**kwargs)
        context.update({
            'page_title': settings.PROJECT_NAME,
            'today_date': settings.TODAY_DATE,
            'project_version': settings.PROJECT_VERSION,
            'db_server': settings.DATABASES['default']['HOST'],
            'project_name': settings.PROJECT_NAME,
        })
        return context

    def get_queryset(self):
        return EmployeeInstance.objects.filter(emp_id__exact=self.request.user.username).exclude(status__exact='c').order_by('start_date')


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
    success_url = reverse_lazy('leave_history')
    permission_required = 'leave.view_employeeinstance'

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

    return render(request, 'leave/leave_policy.html', {
        'page_title': settings.PROJECT_NAME,
        'today_date': settings.TODAY_DATE,
        'project_version': settings.PROJECT_VERSION,
        'db_server': settings.DATABASES['default']['HOST'],
        'project_name': settings.PROJECT_NAME,        
        'leave_policy': leave_policy
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
        'leave_policy': leave_policy
    })


class EmployeeCreate(PermissionRequiredMixin, CreateView):
    model = EmployeeInstance
    fields = '__all__'
    permission_required = 'leave.add_employeeinstance'


def checkLunchTime(start_date_hour, end_date_hour):
    if end_date_hour >= 12:
        return True
    else:
        return False

def EmployeeNew(request):
    page_title = settings.PROJECT_NAME
    db_server = settings.DATABASES['default']['HOST']
    project_name = settings.PROJECT_NAME
    project_version = settings.PROJECT_VERSION
    today_date = settings.TODAY_DATE

    if request.method == "POST":

        form = EmployeeForm(request.POST, user=request.user)

        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']

            leave_type_id = form.cleaned_data['leave_type']
            username = request.user.username
            fullname = request.user.first_name + " " + request.user.last_name
            created_by = request.user.username                        

            employee = form.save(commit=False)

            employee.emp_id = request.user.username
            employee.created_by = request.user.username

            """ START """
            delta = timedelta(days=1)
            number_of_leave_day, number_of_leave_hour = 0, 0       
            number_of_leave_day = (end_date.day - start_date.day)            
            total_leave_day, total_leave_hour = 0, 0

            while start_date <= end_date:                
                if number_of_leave_day <= 0:
                    number_of_leave_hour = end_date.hour - start_date.hour
                    if number_of_leave_hour == 9:
                        total_leave_day += 1
                        total_leave_hour = 0
                    else:
                        total_leave_day = 0
                        total_leave_hour = number_of_leave_hour
                else:
                    number_of_leave_hour = end_date.hour - start_date.hour

                    if number_of_leave_hour == 9:
                        total_leave_day += 1
                        total_leave_hour = 0
                    else:
                        total_leave_day = number_of_leave_day
                        total_leave_hour = number_of_leave_hour

                start_date += delta                
            
            # Rule : Check lunch time
            if checkLunchTime(start_date.hour, end_date.hour):
                total_leave_hour = total_leave_hour - 1

            employee.lve_act = total_leave_day
            employee.lve_act_hr = total_leave_hour
            """ END """

            employee.save()

            """ TODO: Create send mail function"""
            if settings.TURN_SEND_MAIL_ON:
                query = LeaveEmployee.objects.get(emp_id=request.user.username)
                supervisor_id = query.emp_spid
                supervisor = User.objects.get(username=supervisor_id)
                supervisor_email = supervisor.email

                subject = "GFTH Board: Leave Request"
                sender = "amnaj.potipak@guardforce.co.th"
                recipients = [supervisor_email]
                context = {'username': username, 'fullname': fullname, 'start_date': start_date.strftime('%A, %d-%B-%Y'), 'end_date': end_date.strftime('%A, %d-%B-%Y')}

                send_mail(
                    subject,
                    render_to_string('email/leave_request.html', context),
                    sender,
                    recipients,
                    fail_silently=False)                        

            return HttpResponseRedirect('/leave/leave-history/?submitted=True')

    else:
        form = EmployeeForm(user=request.user)

    return render(request, 'leave/employeeinstance_form.html', {
        'form': form,
        'page_title': settings.PROJECT_NAME,
        'today_date': settings.TODAY_DATE,
        'project_version': settings.PROJECT_VERSION,
        'db_server': settings.DATABASES['default']['HOST'],
        'project_name': settings.PROJECT_NAME,        
    })


class LeaveApprovalListView(PermissionRequiredMixin, generic.ListView):
    page_title = settings.PROJECT_NAME
    db_server = settings.DATABASES['default']['HOST']
    project_name = settings.PROJECT_NAME
    project_version = settings.PROJECT_VERSION
    today_date = settings.TODAY_DATE
    template_name = 'leave/leave_approval_list.html'
    permission_required = ('leave.approve_leaveplan')
    model = EmployeeInstance
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super(LeaveApprovalListView, self).get_context_data(**kwargs)
        context.update({
            'page_title': settings.PROJECT_NAME,
            'today_date': settings.TODAY_DATE,
            'project_version': settings.PROJECT_VERSION,
            'db_server': settings.DATABASES['default']['HOST'],
            'project_name': settings.PROJECT_NAME,
        })
        return context

    def get_queryset(self):
        return EmployeeInstance.objects.raw("select ei.id, ei.start_date, ei.end_date, ei.created_date, ei.created_by, ei.status, ei.emp_id, ei.leave_type_id, e.emp_fname_th, e.emp_lname_th from leave_employeeinstance as ei inner join leave_employee e on ei.emp_id = e.emp_id where ei.emp_id in (select emp_id from leave_employee where emp_spid=" + self.request.user.username + ") order by start_date desc")


@permission_required('leave.approve_leaveplan')
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
        if settings.TURN_SEND_MAIL_ON:
            employee = User.objects.get(username=employee_leave_instance.emp_id)

            subject = "GFTH Board: Approved Leave Request"
            sender = settings.EMAIL_SENDER
            recipients = [employee.email]
            employee_id = employee_leave_instance.emp_id
            employee = User.objects.get(username=employee_id)
            employee_fullname = employee.first_name + " " + employee.last_name
            leave_type = employee_leave_instance.leave_type
            start_date = employee_leave_instance.start_date.strftime('%A, %d-%B-%Y')
            end_date = employee_leave_instance.end_date.strftime('%A, %d-%B-%Y')

            context = {'fullname': employee_fullname, 'start_date': start_date, 'end_date': end_date, 'leave_type': leave_type}

            send_mail(
                subject,
                render_to_string('email/leave_request_approved.html', context),
                sender,
                recipients,
                fail_silently=False)

        return HttpResponseRedirect(reverse('leave_approval'))
    
    leaveEmployee = LeaveEmployee.objects.get(emp_id=employee_leave_instance.emp_id)

    context = {
        'leave_employee': leaveEmployee,
        'employee_leave_instance': employee_leave_instance,
        'page_title': settings.PROJECT_NAME,
        'db_server': settings.DATABASES['default']['HOST'],
        'project_name': settings.PROJECT_NAME,
        'project_version': settings.PROJECT_VERSION,
        'today_date' : settings.TODAY_DATE
    }

    return render(request, 'leave/employeeinstance_approve.html', context)


@permission_required('leave.approve_leaveplan')
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
        employee_leave_instance.save()

        # TODO: Send mail funciton
        if settings.TURN_SEND_MAIL_ON:
            employee = User.objects.get(username=employee_leave_instance.emp_id)

            subject = "GFTH Board: Approved Leave Request"
            sender = settings.EMAIL_SENDER
            recipients = [employee.email]
            employee_id = employee_leave_instance.emp_id
            employee = User.objects.get(username=employee_id)
            employee_fullname = employee.first_name + " " + employee.last_name
            leave_type = employee_leave_instance.leave_type
            start_date = employee_leave_instance.start_date.strftime('%A, %d-%B-%Y')
            end_date = employee_leave_instance.end_date.strftime('%A, %d-%B-%Y')

            context = {'fullname': employee_fullname, 'start_date': start_date, 'end_date': end_date, 'leave_type': leave_type}

            send_mail(
                subject,
                render_to_string('email/leave_request_rejected.html', context),
                sender,
                recipients,
                fail_silently=False)

        return HttpResponseRedirect(reverse('leave_approval'))

    leaveEmployee = LeaveEmployee.objects.get(emp_id=employee_leave_instance.emp_id)

    context = {
        'leave_employee': leaveEmployee,
        'employee_leave_instance': employee_leave_instance,
        'page_title': settings.PROJECT_NAME,
        'db_server': settings.DATABASES['default']['HOST'],
        'project_name': settings.PROJECT_NAME,
        'project_version': settings.PROJECT_VERSION,
        'today_date' : settings.TODAY_DATE        
    }

    return render(request, 'leave/employeeinstance_reject.html', context)

