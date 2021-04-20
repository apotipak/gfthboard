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


class ITcontractDB(models.Model):
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
    start_date = models.DateTimeField(null=True)  # models.DateTimeField(db_column='UPD_Date')  Field name made lowercase.
    end_date = models.DateTimeField(null=True)  # Field name made lowercase.
    upd_date = models.DateTimeField(null=True)  # Field name made lowercase.
    upd_by = models.CharField(max_length=50, blank=True, null=True)
    upd_flag = models.CharField(max_length=1, blank=True, null=True)
    opd1 = models.DateTimeField(null=True)
    opd2 = models.DateTimeField(null=True)
    op1 = models.CharField(max_length=100, blank=True, null=True)
    op2 = models.CharField(max_length=100, blank=True, null=True)
    op3 = models.CharField(max_length=200, blank=True, null=True)    
    opn1 = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    opn2 = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    opn3 = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    afile = models.FileField(upload_to='documents/', null=True)
    afile_data = models.BinaryField(null=True)    

    class Meta:
        managed = True
        ordering = ('id',)
        db_table = 'ITcontractDB'

    def ITcontractPolicy(request):
        ITcontractPolicyInstance = ITcontractDB.objects.raw("Select id, dept,vendor,description,start_date,end_date from ITcontractDB order by end_date desc ")
        return ITcontractPolicyInstance


class ScheduleAlertSetting(models.Model):
    alert_id = models.AutoField(primary_key=True)
    app_name = models.CharField(max_length=100, blank=True, null=True)
    description = models.CharField(max_length=100, blank=True, null=True)
    send_to_email = models.CharField(max_length=100, blank=True, null=True)
    send_to_group_email = models.CharField(max_length=100, blank=True, null=True)
    alert_active = models.CharField(max_length=1, blank=True, null=True)
    reach_minimum_day = models.SmallIntegerField(blank=True, null=True)
    created_date = models.DateTimeField(null=True)
    created_by = models.CharField(max_length=50, blank=True, null=True)    
    modified_date = models.DateTimeField(null=True)
    modified_by = models.CharField(max_length=50, blank=True, null=True)
    modified_flag = models.CharField(max_length=1, blank=True, null=True)

    class Meta:
        managed = True
        ordering = ('alert_id',)
        db_table = 'schedule_alert_setting'

    def __str__(self):
        return '{0} ({1} {2})'.format(self.alert_id, self.alert_name, self.alert_email, self.alert_status)

# Send email notification when IT contract is expired.