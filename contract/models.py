from django.db import models


class TclContractQty(models.Model):
    cnt_id = models.CharField(primary_key=True, max_length=13)
    cus_name_th = models.CharField(max_length=120, blank=True, null=True)
    zone_en = models.CharField(max_length=30, blank=True, null=True)
    cnt_sign_frm = models.CharField(max_length=30, blank=True, null=True)
    cnt_sign_to = models.CharField(max_length=30, blank=True, null=True)
    cus_add1_th = models.CharField(max_length=150, blank=True, null=True)
    city_th = models.CharField(max_length=30, blank=True, null=True)
    sd = models.DecimalField(db_column='SD', max_digits=38, decimal_places=0, blank=True, null=True)  # Field name made lowercase.
    sn = models.DecimalField(db_column='SN', max_digits=38, decimal_places=0, blank=True, null=True)  # Field name made lowercase.
    cqty = models.DecimalField(db_column='CQTY', max_digits=4, decimal_places=0, blank=True, null=True)  # Field name made lowercase.
    dly_sd = models.IntegerField(db_column='DLY_SD')  # Field name made lowercase.
    dly_sn = models.IntegerField(db_column='DLY_SN')  # Field name made lowercase.
    dly_std = models.IntegerField(db_column='DLY_STD')  # Field name made lowercase.
    dly_stn = models.IntegerField(db_column='DLY_STN')  # Field name made lowercase.
    dly_dof = models.IntegerField(db_column='DLY_DOF')  # Field name made lowercase.
    dly_date = models.CharField(db_column='Dly_Date', max_length=13)  # Field name made lowercase.
    upd_date = models.DateTimeField(db_column='UPD_Date')  # Field name made lowercase.

    class Meta:
        managed = False
        ordering = ('cnt_id',)
        db_table = 'TCl_Contract_QTY'

    def __str__(self):
        return self.cus_name_th


class TclDailyWorking(models.Model):
    cnt_id = models.DecimalField(primary_key=True, max_digits=13, decimal_places=0)
    cus_name_th = models.CharField(max_length=120, blank=True, null=True)
    emp_id = models.DecimalField(max_digits=7, decimal_places=0, blank=True, null=True)
    fname = models.CharField(db_column='Fname', max_length=71, blank=True, null=True)  # Field name made lowercase.
    shf_type = models.CharField(max_length=1, blank=True, null=True)
    shf_desc = models.CharField(max_length=30, blank=True, null=True)
    dly_date = models.CharField(max_length=30, blank=True, null=True)
    upd_date = models.CharField(db_column='UPD_Date', max_length=30, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'TCL_Daily_Working'
