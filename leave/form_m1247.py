import datetime
import time
import calendar
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from datetime import datetime, timedelta
from django import forms
from .models import EmployeeInstance, LeaveType, LeavePlan, LeaveEmployee, LeaveHoliday
from django.forms.widgets import HiddenInput
from django.contrib.auth.models import User
from decimal import Decimal
from django.db.models import Sum
from .rules import *
from django.utils.dateparse import parse_datetime
from django import forms
from django.template.defaultfilters import filesizeformat


current_year = datetime.now().year
standard_start_working_hour = 0
standard_stop_working_hour = 23

class EmployeeM1247Form(forms.ModelForm):
    start_working_hour = 0
    stop_working_hour = 59
    hour_range = ((0,'00'),(1,'01'),(2,'02'),(3,'03'),(4,'04'),(5,'05'),(6,'06'),(7,'07'),(8,'08'),(9,'09'),(10,'10'),(11,'11'),(12,'12'),(13,'13'),(14,'14'),(15,'15'),(16,'16'),(17,'17'),(18,'18'),(19,'19'),(20,'20'),(21,'21'),(22,'22'),(23,'23'))
    minute_range = ((0,'00'),(30,'30'),(59,'59'))

    leave_type = forms.ModelChoiceField(label='เลือกประเภทการลา', queryset=None, required=True)

    start_date = forms.DateField(label='วันเริ่ม', required=True, error_messages={'required': 'กรุณาป้อนข้อมูลวันที่ลา'})
    start_hour = forms.IntegerField(widget=forms.Select(choices=hour_range))
    start_minute = forms.IntegerField(widget=forms.Select(choices=minute_range))

    end_date = forms.DateField(label='วันสิ้นสุด', required=True, error_messages={'required': 'กรุณาป้อนข้อมูลลาถึงวันที่'})    
    end_hour = forms.IntegerField(widget=forms.Select(choices=hour_range))
    end_minute = forms.IntegerField(widget=forms.Select(choices=minute_range))

    employee_type = forms.CharField(required=False, widget=forms.HiddenInput(), initial="M1247")

    document = forms.FileField(required=False)

    class Meta:
        model = EmployeeInstance
        fields = ['start_date', 'end_date', 'leave_type', 'lve_act', 'lve_act_hr', 'document']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(EmployeeM1247Form, self).__init__(*args, **kwargs)

        default_end_date =  datetime.now()+timedelta(days=1)
        self.fields['leave_type'].widget.attrs={'class': 'form-control'}
        self.fields['leave_type'].queryset=LeaveType.objects.filter(leaveplan__emp_id=self.user.username, leaveplan__lve_year=current_year)        

        self.fields['start_date'].widget.attrs={'class': 'form-control datepicker border-bottom-0 border-left-0 rounded-0'}
        self.initial['start_date'] = datetime.now().strftime("%Y-%m-%d")
        self.fields['start_date'].widget.attrs['placeholder'] = "YYYY-MM-DD"        
        self.fields['start_hour'].widget.attrs={'class': 'form-control border-top-0 border-left-0 rounded-0'}
        self.initial['start_hour'] = 8
        self.fields['start_minute'].widget.attrs={'class': 'form-control border-top-0 rounded-0'}
        self.initial['start_minute'] = 0

        self.fields['end_date'].widget.attrs={'class': 'form-control datepicker border-bottom-0 border-left-0 rounded-0'}
        self.initial['end_date'] = datetime.now().strftime("%Y-%m-%d") #default_end_date.strftime("%Y-%m-%d")
        self.fields['end_date'].widget.attrs['placeholder'] = "YYYY-MM-DD"        
        self.fields['end_hour'].widget.attrs={'class': 'form-control border-top-0 border-left-0 rounded-0'}
        self.initial['end_hour'] = 17
        self.fields['end_minute'].widget.attrs={'class': 'form-control border-top-0 rounded-0'}
        self.initial['end_minute'] = 0

    def clean(self):
        datetime_format = "%Y-%m-%d %H:%M:%S"
        cleaned_data = super(EmployeeM1247Form, self).clean()

        leave_type = self.cleaned_data.get('leave_type')
        leave_type_id = self.data.get('leave_type')

        start_date = self.cleaned_data.get('start_date')
        start_hour = self.cleaned_data.get('start_hour')
        start_minute = self.cleaned_data.get('start_minute')

        end_date = self.cleaned_data.get('end_date')
        end_hour = self.cleaned_data.get('end_hour')
        end_minute = self.cleaned_data.get('end_minute')
        
        document = self.cleaned_data.get('document')
        if document is not None:
            document_type = document.content_type.split('/')[0]
            if document_type in settings.CONTENT_TYPES:
                if document.size > settings.MAX_UPLOAD_SIZE:
                    raise forms.ValidationError(_('ไฟล์แนบมีขนาดเกิน 5 เมกะไบท์'))
            else:
                raise forms.ValidationError(_('แนบไฟล์รูปภาพได้เท่านั้น'))

        username = self.user.username
        employee_type = 'M1'

        d1 = str(start_date) + ' ' + str(start_hour) + ':' + str(start_minute) + ':00'
        d2 = str(end_date) + ' ' + str(end_hour) + ':' + str(end_minute) + ':00'
        start_date = datetime.strptime(d1, datetime_format)
        end_date = datetime.strptime(d2, datetime_format)

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
            # Check Standard Business Rules
            # ------------------------------------------------
            found_standard_error = checkM1247StandardBusinessRules(start_date, end_date, leave_type_id)
            if found_standard_error[0]:
                raise forms.ValidationError(_(found_standard_error[1]))
            
            # ------------------------------------------------ 
            # Check M1247 Business Rules
            # ------------------------------------------------            
            found_m1247_error = checkM1247BusinessRules('M1247', start_date, end_date, leave_type_id)
            if found_m1247_error[0]:
                raise forms.ValidationError(found_m1247_error[1])
            else:
                total_leave_request_hour = found_m1247_error[1]

            
            #raise forms.ValidationError(total_leave_request_hour)
            print(str(total_leave_request_hour) + " : total_leave_request_hour")
            print(str(grand_total_leave_quota_remaining_hour) + " : grand_total_leave_quota_remaining_hour")

            # RULE 1: Check not over leave quota
            if (total_leave_request_hour) > grand_total_leave_quota_remaining_hour:
                #raise forms.ValidationError({'start_date': "เลือกวันลาเกินโควต้าที่กำหนด"})
                raise forms.ValidationError(_("มีการเลือกวันลาเกินจำนวนที่กำหนด"))
            else:
                if grand_total_leave_quota_remaining_hour <= 0:
                    #raise forms.ValidationError({'start_date': "ใช้วัน" + str(leave_type) + "หมดแล้ว" })
                    raise forms.ValidationError(_("ใช้วัน" + str(leave_type) + "หมดแล้ว"))

            # RULE 2: Check duplicate leave
            #select id from leave_employeeinstance where not (start_date > @end_date OR end_date < @start_date)
            queryset = EmployeeInstance.objects.raw("select id from leave_employeeinstance where not (start_date > '" + str(end_date.strftime("%Y-%m-%d %H:00") + "' or end_date < '" + str(start_date.strftime("%Y-%m-%d %H:01")) + "')") + " and emp_id=" + username + " and status in ('a','p','C','F')")            
            if len(queryset) > 0:
                #raise forms.ValidationError({'start_date': "เลือกวันลาซ้ำ"})
                raise forms.ValidationError(_("มีการเลือกวันลาซ้ำ"))

            # RULE 3: Check public holidays
            if checkLeaveTypeIncludePublicHoliday(leave_type_id):
                queryset = LeaveHoliday.objects.filter(hol_date__range=(start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))).values_list('pub_th', flat=True)
                holiday_list = str(list(queryset)).replace("'", '')
                if len(queryset) > 0:
                    #raise forms.ValidationError({'start_date': "เลือกวันลาตรงกับวันหยุด - " + str(holiday_list)})
                    raise forms.ValidationError(_("ช่วงวันลาตรงกับวันหยุดนักขัตฤกษ์ - " + str(holiday_list)))

            # RULE 4: Check not allow over month
            if(checkLeaveRequestOverMonth("M1", start_date, end_date)):
                #raise forms.ValidationError({'start_date': "เลือกวันลาข้ามเดือน"})
                raise forms.ValidationError(_("ไม่สามารถเลือกวันลาข้ามเดือน กรุณาแบ่งทำ 2 รายการแยกเดือนกัน"))
        
        return cleaned_data    
