from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
import datetime
from django.utils.timezone import now
from django import forms
from django.urls import reverse
import uuid


class LeaveHoliday(models.Model):
    hol_date = models.DateTimeField()
    pub_id = models.SmallIntegerField(blank=True, null=True)
    pub_th = models.CharField(db_column='PUB_TH', max_length=50, blank=True, null=True)  # Field name made lowercase.
    pub_en = models.CharField(db_column='PUB_EN', max_length=50, blank=True, null=True)  # Field name made lowercase.
    upd_date = models.DateTimeField()
    upd_by = models.CharField(max_length=6)

    class Meta:
        managed = False
        db_table = 'LEAVE_HOLIDAY'

    def PublicHolidayInstance():
        try: 
            public_holiday_instance = LeaveHoliday.objects.raw("select pub_id as id, pub_th, pub_en, hol_date from LEAVE_HOLIDAY order by hol_date")
        except ObjectDoesNotExist:
            public_holiday_instance = None   
    
        return public_holiday_instance


class LeaveEmployee(models.Model):
    emp_id = models.DecimalField(max_digits=7, decimal_places=0, db_column='emp_id', primary_key=True)
    emp_fname_en = models.CharField(max_length=30, blank=True, null=True)
    emp_lname_en = models.CharField(max_length=40, blank=True, null=True)
    emp_fname_th = models.CharField(max_length=30, blank=True, null=True)
    emp_lname_th = models.CharField(max_length=40, blank=True, null=True)
    pos_th = models.CharField(max_length=50, blank=True, null=True)
    pos_en = models.CharField(max_length=50, blank=True, null=True)
    div_th = models.CharField(max_length=50, blank=True, null=True)
    div_en = models.CharField(max_length=50, blank=True, null=True)
    emp_type = models.CharField(max_length=2, blank=True, null=True)
    emp_join_date = models.DateTimeField(blank=True, null=True)
    emp_term_date = models.DateTimeField(blank=True, null=True)
    upd_date = models.DateTimeField()
    upd_by = models.CharField(max_length=6)
    emp_passcode = models.CharField(db_column='Emp_passcode', max_length=4, blank=True, null=True)  # Field name made lowercase.
    emp_spid = models.CharField(db_column='emp_SpID', max_length=10, blank=True, null=True)  # Field name made lowercase.
    password = models.CharField(max_length=13)
    
    class Meta:
        managed = False
        db_table = 'Leave_employee'
        permissions = (
            ("approve_leaveplan", "Can approve leave employee"),
        )

    def EmployeeInstance(request):
        EmployeeInstance = None
        if request.user.username != 'superadmin':
            employee_id = request.user.username
            try:
                EmployeeInstance = LeaveEmployee.objects.raw("select * from Leave_employee where emp_id='" + employee_id + "'")
            except ObjectDoesNotExist:
                EmployeeInstance = None

        return EmployeeInstance

    def SuperVisorInstance(request):
        SuperVisorInstance = None
        if request.user.username != 'superadmin':
            EmployeeSupervisorID = LeaveEmployee.objects.filter(emp_id__exact=request.user.username).values_list('emp_spid', flat=True).get()
            try:
                SuperVisorInstance = LeaveEmployee.objects.raw("select * from Leave_employee where emp_id='" + str(EmployeeSupervisorID) + "'")
            except ObjectDoesNotExist:
                SuperVisorInstance = None

        return SuperVisorInstance

    def TeamMemberList(request):
        TeamMemberList = None
        EmployeeID = request.user.username
        try:
            TeamMemberList = LeaveEmployee.objects.raw("select * from Leave_employee where emp_spid='" + EmployeeID + "' order by emp_id")
        except ObjectDoesNotExist:
            TeamMemberList = None

        return TeamMemberList


class LeaveType(models.Model):
    lve_id = models.DecimalField(primary_key=True, max_digits=3, decimal_places=0)
    lve_th = models.CharField(max_length=50, blank=True, null=True)
    lve_en = models.CharField(max_length=50, blank=True, null=True)
    lve_code = models.CharField(max_length=3, blank=True, null=True)
    pay_type = models.CharField(max_length=3, blank=True, null=True)
    upd_date = models.DateTimeField(blank=True, null=True)
    upd_by = models.CharField(max_length=10, blank=True, null=True)
    upd_flag = models.CharField(max_length=1, blank=True, null=True)
    lve_type = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'LEAVE_TYPE'

    def __str__(self):
        return '{0}'.format(self.lve_th)

class LeavePlan(models.Model):
    lve_year = models.DecimalField(max_digits=4, decimal_places=0, blank=True, null=True)
    emp_id = models.DecimalField(max_digits=7, decimal_places=0, blank=True, null=True)
    lve_id = models.DecimalField(max_digits=3, decimal_places=0, blank=True, null=True)
    lve_code = models.CharField(max_length=3, blank=True, null=True)
    lve_plan = models.DecimalField(max_digits=3, decimal_places=0, blank=True, null=True)
    lve_plan_hr = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    lve_act = models.DecimalField(max_digits=3, decimal_places=0, blank=True, null=True)
    lve_act_hr = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    lve_miss = models.DecimalField(max_digits=3, decimal_places=0, blank=True, null=True)
    lve_miss_hr = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    upd_date = models.DateTimeField()
    upd_by = models.CharField(max_length=6)
    lve_id = models.ForeignKey(LeaveType, db_column="lve_id", on_delete=models.SET_NULL, null=True)
    lve_HRMS = models.DecimalField(max_digits=3, decimal_places=0, blank=True, null=True)
    lve_HRMS_HR = models.DecimalField(max_digits=3, decimal_places=0, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Leave_Plan'

    def EmployeeLeavePolicy(request):
        UserName = request.user.username
        now = datetime.datetime.now()
        LeaveYear = str(now.year)

        if UserName == 'superadmin':
            EmployeeLeavePolicyInstance = ""
        else:
            EmployeeLeavePolicyInstance = LeavePlan.objects.raw("select lp.emp_id as id, lp.lve_year, lp.lve_act, lp.lve_act_hr, lp.lve_HRMS, lp.lve_HRMS_HR, lp.lve_miss, lp.lve_miss_hr, lt.lve_id as lve_type_id, lp.lve_code, lp.lve_plan, lp.lve_miss, lp.lve_miss_hr, lt.lve_th from leave_plan lp inner join leave_type lt on lp.lve_id=lt.lve_id where lp.emp_id=" + UserName + " and lp.lve_year=" + LeaveYear)
        return EmployeeLeavePolicyInstance


class EmployeeInstance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)   
    emp = models.ForeignKey(LeaveEmployee, on_delete=models.SET_NULL, null=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    created_date = models.DateTimeField(default=now, editable=False)
    created_by = models.DecimalField(max_digits=7, decimal_places=0, null=True)
    leave_type = models.DecimalField(max_digits=3, decimal_places=0)
    leave_type = models.ForeignKey(LeaveType, on_delete=models.SET_NULL, null=True, blank=True)
    
    lve_act = models.IntegerField(blank=True, null=True)
    lve_act_hr = models.IntegerField(blank=True, null=True)

    updated_date = models.DateTimeField(null=True, blank=True)
    updated_by = models.DecimalField(max_digits=7, decimal_places=0, blank=True, null=True)
    
    comment = models.TextField(blank=True, null=True)
    
    LEAVE_STATUS = (
        ('a', 'Approved'),
        ('p', 'Pending'),
        ('r', 'Rejected'),
        ('c', 'Sync complete'),
        ('f', 'Sync fail'),
    )
    status = models.CharField(
        max_length=1,
        choices=LEAVE_STATUS,
        blank=True,
        default='p',
        help_text='Leave Request Status')

    class Meta:
        #ordering = ['-created_date', '-start_date']
        ordering = ['-created_date']

    def get_absolute_url(self):
        return reverse('leave_history_detail', args=[str(self.id)])

    def TeamLeaveRequestCount(request):
        queryset = EmployeeInstance.objects.raw("select id from leave_employeeinstance where emp_id in (select emp_id from leave_employee where emp_spid='" + request.user.username + "') and status='p'")
        return len(queryset)

    def __str__(self):
        return '{0} ({1} {2})'.format(self.id, self.employee.emp_fname_th, self.status)

