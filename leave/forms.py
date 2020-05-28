from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
import datetime
from datetime import datetime
from django import forms
from .models import EmployeeInstance, LeaveType, LeavePlan, LeaveEmployee, LeaveHoliday
from django.forms.widgets import HiddenInput
from django.contrib.auth.models import User
from decimal import Decimal
import calendar
from datetime import timedelta
from django.db.models import Sum


class EmployeeForm(forms.ModelForm):
    #leave_type = forms.ModelChoiceField(label='ประเภทการลา', queryset=None, required=True, initial=0)
    leave_type = forms.ModelChoiceField(label='ประเภทการลา', queryset=None, required=True)
    start_date = forms.DateTimeField(label='วันเริ่ม', widget=HiddenInput(), required=True, error_messages={'required': 'กรุณาระบุวันลา'})
    end_date = forms.DateTimeField(label='วันสิ้นสุด', widget=HiddenInput(), required=True, error_messages={'required': 'กรุณาระบุวันลา'}) 
    number_of_leave_day = forms.DecimalField(widget=HiddenInput(), required=False)
    number_of_leave_hour = forms.DecimalField(widget=HiddenInput(), required=False)

    class Meta:
        model = EmployeeInstance
        fields = ['start_date', 'end_date', 'leave_type', 'lve_act', 'lve_act_hr']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(EmployeeForm, self).__init__(*args, **kwargs)
        self.fields['leave_type'].widget.attrs={'class': 'form-control'}
        self.fields['leave_type'].queryset=LeaveType.objects.filter(leaveplan__emp_id=self.user.username)

    def checkLunchTime(start_date, end_date):
        return True

    def clean(self):
        cleaned_data = super(EmployeeForm, self).clean()
        start_date = self.cleaned_data.get('start_date')
        end_date = self.cleaned_data.get('end_date')
        leave_type = self.cleaned_data.get('leave_type')
        leave_type_id = self.data.get('leave_type')
        username = self.user.username
        employee_type = 'M1'

        if start_date != None:

            """ RULE: Check duplicate leave """
            #queryset = EmployeeInstance.objects.raw("select id from leave_employeeinstance where '" + str(start_date.strftime("%Y-%m-%d %H:01")) + "' between start_date and end_date and emp_id=" + username + " and status in ('a','p','C','F')")
            queryset = EmployeeInstance.objects.raw("select id from leave_employeeinstance where not (start_date > '" + str(end_date.strftime("%Y-%m-%d %H:00") + "' or end_date < '" + str(start_date.strftime("%Y-%m-%d %H:01")) + "')") + " and emp_id=" + username + " and status in ('a','p','C','F')")
            
            #raise forms.ValidationError({'start_date': start_date})
            #raise forms.ValidationError({'start_date': end_date})
            #raise forms.ValidationError({'start_date': queryset})

            if len(queryset) > 0:
                raise forms.ValidationError({'start_date': "เคยใช้วันลาไปแล้ว"})
                return cleaned_data

            if len(queryset) == 0:
                """ Validate End Date """
                count = EmployeeInstance.objects.filter(end_date__exact=end_date).filter(emp_id__exact=username).filter(status__in=('p','a','C','F')).count()
                if count == 0:

                    """ Check total number of Pending and Approved status in hour """
                    total_leave_request_in_day = EmployeeInstance.objects.filter(emp_id__exact=username).filter(leave_type_id__exact=leave_type_id).filter(status__in=('p','a')).aggregate(sum=Sum('lve_act'))['sum'] or 0
                    total_leave_request_in_hour = EmployeeInstance.objects.filter(emp_id__exact=username).filter(leave_type_id__exact=leave_type_id).filter(status__in=('p','a')).aggregate(sum=Sum('lve_act_hr'))['sum'] or 0
                    total_number_of_pending_approved_leave_request_in_hour = total_leave_request_in_hour + (total_leave_request_in_day * 8)

                    """ Check total number of leave reqeust in hour """
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

                            # Rule: Check lunch time


                        start_date += delta

                    total_number_of_current_leave_request_in_hour = (total_leave_day * 8) + (total_leave_hour)
                                            
                    """ Check total number of leave type remaining in hour """
                    total_leave_remaining_in_day = LeavePlan.objects.filter(emp_id__exact=username).filter(lve_id__exact=leave_type_id).values_list('lve_miss', flat=True).get()
                    total_leave_remaining_in_hour = LeavePlan.objects.filter(emp_id__exact=username).filter(lve_id__exact=leave_type_id).values_list('lve_miss_hr', flat=True).get()                        
                    total_number_of_leave_remaing_in_hour = total_leave_remaining_in_hour + (total_leave_remaining_in_day * 8)                    

                    #raise forms.ValidationError({'start_date': str(total_number_of_current_leave_request_in_hour)})
                    #return cleaned_data

                    """ TODO: Employee Type Validation """   
                    employee_type = LeaveEmployee.objects.filter(emp_id__exact=username).values_list('emp_type', flat=True).get()
                    if employee_type == 'M1':
                        start_date_day, start_date_time = start_date.day, start_date.hour
                        end_date_day, end_date_time = end_date.day, end_date.hour

                        """ RULE: Not allows to submit 0 hour """
                        if total_number_of_current_leave_request_in_hour == 0:
                            raise forms.ValidationError({'start_date': "เลือกจำนวนชั่วโมงไม่ถูกต้อง"})
                            return cleaned_data

                        """ RULE: Not allows to submit lunch time """
                        if start_date_time == 12 and end_date_time == 13:
                            raise forms.ValidationError({'start_date': "เลือกเวลาพักกลางวัน"})
                        
                        """ RULE: Not allows to submit less than 8:00 AM or greater than 17:00 PM """
                        if start_date_time < 8:
                            raise forms.ValidationError({'start_date': "เลือกเวลานอกทำการ"})
                        elif end_date_time > 17:
                            raise forms.ValidationError({'start_date': "เลือกเวลานอกทำการ"})
                            return cleaned_data

                        """ RULE: Not allows to sumbit over no. of remaining day """
                        if (total_number_of_pending_approved_leave_request_in_hour + total_number_of_current_leave_request_in_hour) > total_number_of_leave_remaing_in_hour:                            
                            raise forms.ValidationError({'start_date': "วันหยุดคงเหลือไม่พอ"})
                            return cleaned_data
                        else:
                            return cleaned_data                    

                        """ RULE: Not allows to submit for public holidays """
                        queryset = LeaveHoliday.objects.filter(hol_date__range=(start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))).values_list('pub_th', flat=True)
                        holiday_list = str(list(queryset)).replace("'", '')
                        if len(queryset) > 0:
                            raise forms.ValidationError({'start_date': "เลือกวันลาตรงกับวันหยุด - " + str(holiday_list)})

                        """ RULE: Not allows to submit for weekend """
                        week_day_number = start_date.weekday()
                        week_day_name = calendar.day_name[start_date.weekday()]
                        for x in range(total_leave_request_in_day):
                            if start_date.weekday() == 5 or start_date.weekday() == 6:
                                raise forms.ValidationError({'start_date': "วันลาที่เลือกตรงกับวันหยุดเสาร์-อาทิตย์"})
                            else:
                                start_date = start_date + timedelta(days=1)

                        #raise forms.ValidationError({'start_date': str(total_leave_request_in_day)})
                        return cleaned_data
                    else:
                        #raise forms.ValidationError({'start_date': "ระบบวันลาสำหรับพนักงานรายวันอยู่ระหว่างการพัฒนา"})          
                        raise forms.ValidationError({'start_date': "ทำรายการซ้ำ 1"})

                    return cleaned_data
                else:
                    raise forms.ValidationError({'start_date': "ทำรายการซ้ำ 2"})
            else:
                raise forms.ValidationError({'start_date': "วันที่ " + str(start_date.strftime("%d-%b %H:%M")) + " ถึง " + str(end_date.strftime("%d-%b %H:%M")) + " ถูกใช้ทำรายการไปแล้ว"})
            
            return data
        else:
            return cleaned_data