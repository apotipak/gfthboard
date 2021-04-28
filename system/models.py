from django.db import models
from django.contrib.auth.models import User
import datetime
from django.utils.timezone import now


class ComZone(models.Model):
    zone_id = models.DecimalField(primary_key=True, max_digits=4, decimal_places=0)
    zone_th = models.CharField(max_length=30, blank=True, null=True)
    zone_en = models.CharField(max_length=30, blank=True, null=True)
    zone_emp_id = models.DecimalField(max_digits=6, decimal_places=0, blank=True, null=True)
    upd_date = models.DateTimeField(blank=True, null=True)
    upd_by = models.CharField(max_length=10, blank=True, null=True)
    upd_flag = models.CharField(max_length=1, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'COM_ZONE'

    def __str__(self):
    	return self.zone_en


class ContractPolicy(models.Model):
	username = models.ForeignKey(User, db_column='username', to_field='username', on_delete=models.SET_NULL, null=True)	
	zone = models.ForeignKey(ComZone, db_column='zone_id', on_delete=models.CASCADE, blank=True, null=True)	

	class Meta:
		db_table = 'contract_policy'
		verbose_name = u'Contract Policy'
		verbose_name_plural = u'Contract Policy'

	def __str__(self):
		return ('%s - %s' % (self.username, self.zone.zone_en))


class OutlookEmailActiveUserList(models.Model):
    id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    description = models.CharField(max_length=100, blank=True, null=True)
    created_date = models.DateTimeField(null=True, default=datetime.date.today)
    created_by = models.CharField(max_length=50, blank=True, null=True, default='System')    

    class Meta:
        managed = True
        db_table = 'system_outlook_email_active_user_list'
        unique_together = [("email")]

    def __str__(self):
        return '{0}'.format(self.email)

