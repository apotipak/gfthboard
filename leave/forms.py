from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
import datetime
import time
from datetime import datetime, timedelta
from django import forms
from .models import EmployeeInstance, LeaveType, LeavePlan, LeaveEmployee, LeaveHoliday
from django.forms.widgets import HiddenInput
from django.contrib.auth.models import User
from decimal import Decimal
import calendar
from django.db.models import Sum
from .rules import *
from django.utils.dateparse import parse_datetime

# Define constant variable
current_year = datetime.now().year
start_working_hour = 8
stop_working_hour = 17

class EmployeeForm(forms.ModelForm):
    #leave_type = forms.ModelChoiceField(label='ประเภทการลา', queryset=None, required=True, initial=0)
    leave_type = forms.ModelChoiceField(label='เลือกประเภทการลา', queryset=None, required=True)    
    start_date = forms.DateField(label='วันเริ่ม', required=True, error_messages={'required': 'กรุณาป้อนข้อมูลวันที่ลา'})
    end_date = forms.DateField(label='วันสิ้นสุด', required=True, error_messages={'required': 'กรุณาป้อนข้อมูลลาถึงวันที่'})
    start_time = forms.IntegerField(widget = forms.Select(choices=[(v, v) for v in range(start_working_hour, stop_working_hour + 1)]))
    end_time = forms.IntegerField(widget = forms.Select(choices=[(v, v) for v in range(start_working_hour, stop_working_hour + 1)]))

    class Meta:
        model = EmployeeInstance
        fields = ['start_date', 'end_date', 'leave_type', 'lve_act', 'lve_act_hr']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(EmployeeForm, self).__init__(*args, **kwargs)
        self.fields['leave_type'].widget.attrs={'class': 'form-control'}
        self.fields['leave_type'].queryset=LeaveType.objects.filter(leaveplan__emp_id=self.user.username, leaveplan__lve_year=current_year)        

        self.fields['start_date'].widget.attrs={'class': 'form-control datepicker'}
        self.initial['start_date'] = datetime.now().strftime("%Y-%m-%d")

        self.fields['start_time'].widget.attrs={'class': 'form-control'}
        self.fields['start_date'].widget.attrs['placeholder'] = "YYYY-MM-DD"
        self.initial['start_time'] = start_working_hour

        self.fields['end_date'].widget.attrs={'class': 'form-control datepicker'}
        self.initial['end_date'] = datetime.now().strftime("%Y-%m-%d")
        self.fields['end_time'].widget.attrs={'class': 'form-control'}
        self.fields['end_date'].widget.attrs['placeholder'] = "YYYY-MM-DD"
        self.initial['end_time'] = stop_working_hour

    def clean(self):
        cleaned_data = super(EmployeeForm, self).clean()
        start_date = self.cleaned_data.get('start_date')
        start_time = self.cleaned_data.get('start_time')
        end_date = self.cleaned_data.get('end_date')
        end_time = self.cleaned_data.get('end_time')
        leave_type = self.cleaned_data.get('leave_type')
        leave_type_id = self.data.get('leave_type')
        username = self.user.username
        employee_type = 'M1'

        #raise forms.ValidationError({'leave_type': "start: " + str(start_date) + " | end: " + str(end_date)})

        d1 = str(start_date) + ' ' + str(start_time) + ':00:00'
        d2 = str(end_date) + ' ' + str(end_time) + ':00:00'
        start_date = datetime.strptime(d1, "%Y-%m-%d %H:%M:%S")
        end_date = datetime.strptime(d2, "%Y-%m-%d %H:%M:%S")

        #raise forms.ValidationError({'leave_type': "start: " + str(start_date) + " | end: " + str(end_date)})
        if(start_time < start_working_hour or start_time > stop_working_hour):
            raise forms.ValidationError(_("เลือกเวลาไม่ถูกต้อง"))

        if(end_time  < start_working_hour or end_time > stop_working_hour):
            raise forms.ValidationError(_("เลือกเวลาไม่ถูกต้อง"))

        if start_date != None:
            # ------------------------------------------------ 
            # Check master remaining hour (Leave_Plan table)
            # ------------------------------------------------             
            total_leave_quota_remaining_day = LeavePlan.objects.filter(emp_id__exact=username).filter(lve_id__exact=leave_type_id).filter(lve_year=current_year).values_list('lve_miss', flat=True).get()
            total_leave_quota_remaining_hour = LeavePlan.objects.filter(emp_id__exact=username).filter(lve_id__exact=leave_type_id).filter(lve_year=current_year).values_list('lve_miss_hr', flat=True).get()                        
            grand_total_leave_quota_remaining_hour = total_leave_quota_remaining_hour + (total_leave_quota_remaining_day * 8)                    

            
            # ------------------------------------------------ 
            # Check transaction remaing hour (leave_employeeinstance table) (filter status = p, a, F)
            # ------------------------------------------------ 
            total_pending_approve_syncfail_status_history_day = EmployeeInstance.objects.filter(emp_id__exact=username).filter(leave_type_id__exact=leave_type_id).filter(status__in=('p','a','F')).aggregate(sum=Sum('lve_act'))['sum'] or 0
            total_pending_approve_syncfail_status_history_hour = EmployeeInstance.objects.filter(emp_id__exact=username).filter(leave_type_id__exact=leave_type_id).filter(status__in=('p','a','F')).aggregate(sum=Sum('lve_act_hr'))['sum'] or 0
            grand_total_pending_approve_syncfail_status_history_hour = total_pending_approve_syncfail_status_history_hour + (total_pending_approve_syncfail_status_history_day * 8)

            grand_total_leave_quota_remaining_hour = grand_total_leave_quota_remaining_hour - grand_total_pending_approve_syncfail_status_history_hour
                    
            # ------------------------------------------------ 
            # Check request hour
            # ------------------------------------------------
            total_leave_request_hour = checkM1LeaveRequestHour('M1', start_date, end_date)
            
            '''
            raise forms.ValidationError({
                'start_date': 
                "leave remaining : " + str(grand_total_leave_quota_remaining_hour) + " | " +                
                "leave trans: " + str(grand_total_pending_approve_syncfail_status_history_hour) + " | " +
                "leave request: " + str(total_leave_request_hour)                
            })
            '''            
            # RULE 1: Check if leave_request_hour is not over leave quota
            if (total_leave_request_hour > grand_total_leave_quota_remaining_hour):
                #raise forms.ValidationError({'start_date': "เลือกวันลาเกินโควต้าที่กำหนด"})
                raise forms.ValidationError(_("เลือกวันลาเกินโควต้าที่กำหนด"))
            else:
                if grand_total_leave_quota_remaining_hour <= 0:
                    #raise forms.ValidationError({'start_date': "ใช้วัน" + str(leave_type) + "หมดแล้ว" })
                    raise forms.ValidationError(_("ใช้วัน" + str(leave_type) + "หมดแล้ว"))

            # RULE 2: Check if select weekend
            if (total_leave_request_hour == 0):
                #raise forms.ValidationError({'start_date': "เลือกวันลาเริ่มต้นตรงกับเสาร์-อาทิตย์"})
                raise forms.ValidationError(_("เลือกวันลาไม่ถูกต้อง"))

            # RULE 3: Check duplicate leave
            #select id from leave_employeeinstance where not (start_date > @end_date OR end_date < @start_date)
            queryset = EmployeeInstance.objects.raw("select id from leave_employeeinstance where not (start_date > '" + str(end_date.strftime("%Y-%m-%d %H:00") + "' or end_date < '" + str(start_date.strftime("%Y-%m-%d %H:01")) + "')") + " and emp_id=" + username + " and status in ('a','p','C','F')")            
            if len(queryset) > 0:
                #raise forms.ValidationError({'start_date': "เลือกวันลาซ้ำ"})
                raise forms.ValidationError(_("เลือกวันลาซ้ำ"))

            # RULE 4: Check public holidays
            queryset = LeaveHoliday.objects.filter(hol_date__range=(start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))).values_list('pub_th', flat=True)
            holiday_list = str(list(queryset)).replace("'", '')
            if len(queryset) > 0:
                #raise forms.ValidationError({'start_date': "เลือกวันลาตรงกับวันหยุด - " + str(holiday_list)})
                raise forms.ValidationError(_("เลือกวันลาตรงกับวันหยุด - " + str(holiday_list)))

            # RULE 5: Check not allow over month
            if(checkM1LeaveRequestOverMonth("M1", start_date, end_date)):
                #raise forms.ValidationError({'start_date': "เลือกวันลาข้ามเดือน"})
                raise forms.ValidationError(_("เลือกวันลาข้ามเดือน"))

            return cleaned_data
        else:
            return cleaned_data