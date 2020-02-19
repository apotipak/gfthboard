# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Flooring(models.Model):
    name = models.CharField(db_column='Name', max_length=255, blank=True, null=True)  # Field name made lowercase.
    category = models.CharField(db_column='Category', max_length=255, blank=True, null=True)  # Field name made lowercase.
    price = models.DecimalField(db_column='Price', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    image_image_field = models.CharField(db_column='Image (image)', max_length=255, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    overview = models.CharField(db_column='Overview', max_length=255, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Flooring'


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


class LeaveType(models.Model):
    lve_id = models.DecimalField(max_digits=3, decimal_places=0)
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

    class Meta:
        managed = False
        db_table = 'Leave_Plan'


class LeaveEmployee(models.Model):
    emp_id = models.DecimalField(max_digits=7, decimal_places=0)
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
    emp_spid = models.DecimalField(db_column='Emp_SpID', max_digits=7, decimal_places=0, blank=True, null=True)  # Field name made lowercase.
    password = models.CharField(max_length=13)

    class Meta:
        managed = False
        db_table = 'Leave_employee'


class TclDailyWorking(models.Model):
    cnt_id = models.DecimalField(max_digits=13, decimal_places=0, blank=True, null=True)
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


class TclContractQty(models.Model):
    cnt_id = models.CharField(max_length=13, blank=True, null=True)
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
    upd_date = models.CharField(db_column='UPD_Date', max_length=30)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'TCl_Contract_QTY'


class VBiDlyPlanWork(models.Model):
    zone_en = models.CharField(max_length=30, blank=True, null=True)
    qty = models.DecimalField(db_column='Qty', max_digits=38, decimal_places=0, blank=True, null=True)  # Field name made lowercase.
    total = models.DecimalField(db_column='Total', max_digits=38, decimal_places=0, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'V_BI_DLY_Plan_work'


class VBiFeebyzone(models.Model):
    zone_en = models.CharField(max_length=30, blank=True, null=True)
    fee = models.DecimalField(db_column='Fee', max_digits=38, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    qty = models.DecimalField(db_column='QTY', max_digits=38, decimal_places=0, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'V_BI_FEEBYZONE'


class VBiTop10(models.Model):
    cus_name_en = models.CharField(max_length=120, blank=True, null=True)
    fee = models.DecimalField(db_column='Fee', max_digits=10, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    qty = models.DecimalField(db_column='QTY', max_digits=4, decimal_places=0, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'V_BI_Top10'


class VContractActive(models.Model):
    cus_id = models.DecimalField(max_digits=7, decimal_places=0, blank=True, null=True)
    cus_loc = models.CharField(max_length=7, blank=True, null=True)
    cnt_id = models.DecimalField(max_digits=13, decimal_places=0)
    zone_en = models.CharField(max_length=30, blank=True, null=True)
    cus_name_en = models.CharField(max_length=120, blank=True, null=True)
    bgroup = models.CharField(db_column='Bgroup', max_length=30, blank=True, null=True)  # Field name made lowercase.
    cnt_sale_amt = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    cnt_doc_no = models.CharField(max_length=25, blank=True, null=True)
    cnt_sign_frm = models.DateTimeField(blank=True, null=True)
    cnt_sign_to = models.DateTimeField(blank=True, null=True)
    cnt_guard_amt = models.DecimalField(max_digits=4, decimal_places=0, blank=True, null=True)
    cus_taxid = models.CharField(max_length=30, blank=True, null=True)
    btype = models.CharField(db_column='Btype', max_length=100, blank=True, null=True)  # Field name made lowercase.
    btype1 = models.CharField(db_column='Btype1', max_length=100, blank=True, null=True)  # Field name made lowercase.
    btype2 = models.CharField(db_column='Btype2', max_length=100, blank=True, null=True)  # Field name made lowercase.
    cnt_eff_frm = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'V_CONTRACT_ACTIVE'


class VContractActiveQty(models.Model):
    cus_id = models.DecimalField(max_digits=7, decimal_places=0, blank=True, null=True)
    cnt_id = models.DecimalField(max_digits=13, decimal_places=0)
    zone_en = models.CharField(max_length=30, blank=True, null=True)
    cus_name_en = models.CharField(max_length=120, blank=True, null=True)
    cnt_sale_amt = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    cnt_doc_no = models.CharField(max_length=25, blank=True, null=True)
    cnt_guard_amt = models.DecimalField(max_digits=4, decimal_places=0, blank=True, null=True)
    cnt_guard_work = models.DecimalField(db_column='cnt_guard_Work', max_digits=4, decimal_places=0, blank=True, null=True)  # Field name made lowercase.
    opn1 = models.DecimalField(max_digits=4, decimal_places=0, blank=True, null=True)
    opn2 = models.DecimalField(max_digits=4, decimal_places=0, blank=True, null=True)
    op1 = models.CharField(max_length=25, blank=True, null=True)
    op2 = models.CharField(max_length=25, blank=True, null=True)
    cnt_zone = models.DecimalField(max_digits=4, decimal_places=0, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'V_CONTRACT_ACTIVE_QTY'


class VDlyPlan(models.Model):
    cnt_id = models.DecimalField(max_digits=13, decimal_places=0)
    cnt_guard_amt = models.DecimalField(max_digits=4, decimal_places=0, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'V_DLY_plan'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class LeaveEmployeeinstance(models.Model):
    id = models.CharField(primary_key=True, max_length=32)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    created_date = models.DateTimeField()
    created_by = models.DecimalField(max_digits=7, decimal_places=0, blank=True, null=True)
    lve_act = models.IntegerField(blank=True, null=True)
    lve_act_hr = models.IntegerField(blank=True, null=True)
    updated_date = models.DateTimeField(blank=True, null=True)
    updated_by = models.DecimalField(max_digits=7, decimal_places=0, blank=True, null=True)
    status = models.CharField(max_length=1)
    emp_id = models.DecimalField(max_digits=7, decimal_places=0, blank=True, null=True)
    leave_type_id = models.DecimalField(max_digits=3, decimal_places=0, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'leave_employeeinstance'
