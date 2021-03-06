from django.db import models
from django.contrib.auth.models import User
import datetime


class UserProfile(models.Model):
   language = models.CharField(max_length=2, blank=True, null=True)
   username = models.CharField(max_length=10, blank=True, null=True)
   updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)


class ComDivision(models.Model):
    div_id = models.DecimalField(primary_key=True, max_digits=3, decimal_places=0)
    com_id = models.DecimalField(max_digits=2, decimal_places=0, blank=True, null=True)
    div_th = models.CharField(max_length=50, blank=True, null=True)
    div_en = models.CharField(max_length=50, blank=True, null=True)
    upd_date = models.DateTimeField(blank=True, null=True)
    upd_by = models.CharField(max_length=10, blank=True, null=True)
    upd_flag = models.CharField(max_length=1, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'COM_DIVISION'        
        permissions = (
            ("can_view_all_employees", "Can view all employees"),
        )

    def __str__(self):
        return '{0}'.format(self.div_en)


class CovidEmployeeVaccineUpdate(models.Model):    
    emp_id = models.DecimalField(max_digits=7, decimal_places=0, blank=True, null=True)
    full_name = models.CharField(max_length=200, blank=True, null=True)
    phone_number = models.TextField(max_length=50,blank=True, null=True)

    get_vaccine_status = models.DecimalField(max_digits=1, decimal_places=0, blank=True, null=True)
    get_vaccine_date = models.DateTimeField(blank=True, null=True)
    get_vaccine_place = upd_by = models.CharField(max_length=100, blank=True, null=True)    
    file_attach = models.FileField(upload_to='documents/covid/', null=True)
    file_attach_data = models.BinaryField(null=True)
    file_attach_type = models.CharField(max_length=10, blank=True, null=True)

    upd_date = models.DateTimeField(blank=True, null=True)
    upd_by = models.CharField(max_length=10, blank=True, null=True)
    upd_flag = models.CharField(max_length=1, blank=True, null=True)
    
    op1 = models.TextField(max_length=10,blank=True, null=True)
    op2 = models.TextField(max_length=10,blank=True, null=True)
    op3 = models.TextField(max_length=10,blank=True, null=True)
    op4 = models.TextField(max_length=10,blank=True, null=True)
    op5 = models.TextField(max_length=10,blank=True, null=True)
    opn1 = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    opn2 = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    opd1 = models.DateTimeField(blank=True, null=True)
    opd2 = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'covid_employee_vaccine_update'

    '''
    def __str__(self):
        return '{0}'.format(self.div_en)
    '''

class UserPasswordLog(models.Model):
    emp_id = models.DecimalField(primary_key=True, max_digits=7, decimal_places=0)
    is_password_changed = models.BooleanField(default=False,blank=True, null=True)
    is_password_expired = models.BooleanField(default=False,blank=True, null=True)
    created_date = models.DateTimeField(blank=True, null=True, default=datetime.date.today)
    created_by = models.CharField(max_length=10, blank=True, null=True, default='system')
    update_date = models.DateTimeField(blank=True, null=True)
    upd_by = models.CharField(max_length=10, blank=True, null=True)
    upd_flag = models.CharField(max_length=1, blank=True, null=True, default='A')

    class Meta:
        managed = True
        db_table = 'auth_user_password_log'


class UserLoginLog(models.Model):
    emp_id = models.DecimalField(max_digits=7, decimal_places=0, blank=True, null=True)
    login_date = models.DateTimeField(blank=True, null=True, default=datetime.date.today)
    ip_address = models.CharField(max_length=20, blank=True, null=True)
    device = models.CharField(max_length=1000, blank=True, null=True)
    created_by = models.CharField(max_length=10, blank=True, null=True, default='system')
    upd_by = models.CharField(max_length=10, blank=True, null=True)
    upd_flag = models.CharField(max_length=1, blank=True, null=True, default='A')

    class Meta:
        managed = True
        db_table = 'auth_user_login_log'

