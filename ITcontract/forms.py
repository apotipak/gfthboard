import datetime
import time
import calendar
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from datetime import datetime, timedelta
from django import forms
from .models import ITcontractDB
from django.forms.widgets import HiddenInput
from django.contrib.auth.models import User
from decimal import Decimal
from django.db.models import Sum
from django.utils.dateparse import parse_datetime
from django import forms
from django.template.defaultfilters import filesizeformat
from django.forms import Textarea


class ITcontractDBForm(forms.ModelForm):
    dept = forms.CharField(max_length=128, error_messages={'required': 'กรุณาป้อนรหัสผ่านใหม่'}, widget=forms.TextInput(attrs={'autocomplete':'off'}))
    it_contract_id_edit = forms.CharField(required=False, widget=forms.HiddenInput(), initial="")
    afile = forms.FileField(required=False)

    def clean(self):
        return cleaned_data


    '''
    id = models.AutoField(primary_key=True)
    dept = models.CharField(max_length=100, blank=True, null=True)
    vendor = models.CharField(max_length=100, blank=True, null=True)
    description = models.CharField(max_length=100, blank=True, null=True)
    description1 = models.CharField(max_length=100, blank=True, null=True)
    person = models.CharField(max_length=100, blank=True, null=True)
    tel = models.CharField(max_length=100, blank=True, null=True)
    price = models.DecimalField(db_column='price', max_digits=15, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    e_mail = models.CharField(max_length=100, blank=True, null=True)
    remark = models.CharField(max_length=100, blank=True, null=True)
    ae_mail = models.CharField(max_length=100, blank=True, null=True)
    ae_mail1 = models.CharField(max_length=100, blank=True, null=True)

    start_date = models.DateTimeField()  # models.DateTimeField(db_column='UPD_Date')  Field name made lowercase.
    end_date = models.DateTimeField()  # Field name made lowercase.
    upd_date = models.DateTimeField()  # Field name made lowercase.
    upd_by = models.CharField(max_length=50, blank=True, null=True)
    upd_flag = models.CharField(max_length=1, blank=True, null=True)
    opd1 = models.DateTimeField()
    opd2 = models.DateTimeField()
    op1 = models.CharField(max_length=100, blank=True, null=True)
    op2 = models.CharField(max_length=100, blank=True, null=True)
    op3 = models.CharField(max_length=200, blank=True, null=True)

    opn1 = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    opn2 = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    opn3 = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    afile = models.BinaryField(max_length=200, blank=True, null=True)
    '''

    '''
    class Meta:
        model = EmployeeInstance
        fields = ['start_date', 'end_date', 'leave_type', 'lve_act', 'lve_act_hr', 'document', 'leave_reason']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(EmployeeM1247Form, self).__init__(*args, **kwargs)

        default_end_date =  datetime.now()+timedelta(days=1)
        self.fields['leave_type'].widget.attrs={'class': 'form-control'}
        self.fields['leave_type'].queryset=LeaveType.objects.filter(leaveplan__emp_id=self.user.username, leaveplan__lve_year=current_year)        

        self.fields['start_date'].widget.attrs={'class': 'form-control datepicker border-bottom-1 border-left-0 rounded-0 bg-white'}
        self.initial['start_date'] = datetime.now().strftime("%Y-%m-%d")
        self.fields['start_date'].widget.attrs['placeholder'] = "YYYY-MM-DD"        
        self.fields['start_hour'].widget.attrs={'class': 'form-control border-top-0 border-left-1 rounded-0 bg-white'}
        self.initial['start_hour'] = 8
        self.fields['start_minute'].widget.attrs={'class': 'form-control border-top-0 rounded-0 bg-white'}
        self.initial['start_minute'] = 0

        self.fields['end_date'].widget.attrs={'class': 'form-control datepicker border-bottom-1 border-left-0 rounded-0 bg-white'}
        self.initial['end_date'] = datetime.now().strftime("%Y-%m-%d") #default_end_date.strftime("%Y-%m-%d")
        self.fields['end_date'].widget.attrs['placeholder'] = "YYYY-MM-DD"        
        self.fields['end_hour'].widget.attrs={'class': 'form-control border-top-0 border-left-1 rounded-0 bg-white'}
        self.initial['end_hour'] = 17
        self.fields['end_minute'].widget.attrs={'class': 'form-control border-top-0 rounded-0 bg-white'}
        self.initial['end_minute'] = 0

        self.fields['leave_reason'].widget.attrs={'class': 'form-control rounded-0'}

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
            document_type = document.content_type.split('/')[1]
            print("type:",  document_type)
            if document_type in settings.CONTENT_TYPES:
                if document.size > settings.MAX_UPLOAD_SIZE:
                    raise forms.ValidationError(_('ไฟล์แนบมีขนาดเกิน 5 เมกะไบท์'))
            else:
                raise forms.ValidationError(_('ระบบสามารถแนบไฟล์ (png, jpg, jpeg, pdf) ได้เท่านั้น'))

        # raise forms.ValidationError(_('Test'))

        username = self.user.username
        employee_type = 'M1'

        d1 = str(start_date) + ' ' + str(start_hour) + ':' + str(start_minute) + ':00'
        d2 = str(end_date) + ' ' + str(end_hour) + ':' + str(end_minute) + ':00'
        start_date = datetime.strptime(d1, datetime_format)
        end_date = datetime.strptime(d2, datetime_format)
        '''        
