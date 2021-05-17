from django.db import models
import django.db as db
from django.db import connection

class PrpoActions(models.Model):
    atid = models.IntegerField(db_column='atID')  # Field name made lowercase.
    atname = models.CharField(db_column='atName', max_length=20)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'PRPO_Actions'

class PrpoCompany(models.Model):
    cpid = models.IntegerField(primary_key=True , db_column='cpID')  # Field name made lowercase.
    cpnumber = models.CharField(db_column='cpNumber', max_length=5)  # Field name made lowercase.
    cpcountry = models.IntegerField(db_column='cpCountry')  # Field name made lowercase.
    cpname = models.CharField(db_column='cpName', max_length=50)  # Field name made lowercase.
    cpshortcut = models.CharField(db_column='cpShortCut', max_length=2)  # Field name made lowercase.
    cpaltername = models.CharField(db_column='cpAlterName', max_length=100)  # Field name made lowercase.
    cpaddress = models.CharField(db_column='cpAddress', max_length=150, blank=True, null=True)  # Field name made lowercase.
    cpalteraddr = models.CharField(db_column='cpAlterAddr', max_length=150, blank=True, null=True)  # Field name made lowercase.
    cptel = models.CharField(db_column='cpTel', max_length=30, blank=True, null=True)  # Field name made lowercase.
    cpfax = models.CharField(db_column='cpFax', max_length=30, blank=True, null=True)  # Field name made lowercase.
    cpcurrency = models.IntegerField(db_column='cpCurrency')  # Field name made lowercase.
    cplogo = models.CharField(db_column='cpLogo', max_length=100, blank=True, null=True)  # Field name made lowercase.
    cpponotes = models.TextField(db_column='cpPONotes', blank=True, null=True)  # Field name made lowercase.
    cpvpflag = models.BooleanField(db_column='cpVPFlag')  # Field name made lowercase.
    cpverifypercent = models.FloatField(db_column='cpVerifyPercent')  # Field name made lowercase.
    cpvvflag = models.BooleanField(db_column='cpVVFlag')  # Field name made lowercase.
    cpverifyvalue = models.FloatField(db_column='cpVerifyValue')  # Field name made lowercase.
    cpverifyapprover = models.BooleanField(db_column='cpVerifyApprover')  # Field name made lowercase.
    cpprmaxid = models.IntegerField(db_column='cpPRMaxID')  # Field name made lowercase.
    cppomaxid = models.IntegerField(db_column='cpPOMaxID')  # Field name made lowercase.
    fldremainnum = models.DecimalField(db_column='FldRemainNum', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    fldremainchar1 = models.CharField(db_column='FldRemainChar1', max_length=30, blank=True, null=True)  # Field name made lowercase.
    fldremainchar2 = models.CharField(db_column='FldRemainChar2', max_length=30, blank=True, null=True)  # Field name made lowercase.
    opuser = models.IntegerField(db_column='opUser')  # Field name made lowercase.
    optime = models.DateTimeField(db_column='opTime')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'PRPO_Company'

    def prpocompanylist(request):
        #UserName = request.user.username
        #now = datetime.datetime.now()
        #LeaveYear = str(now.year)

        #if UserName == 'superadmin':
        #    ITcontractPolicyInstance = ""
        #else:

        #print("DEBUG")
        sql = "Select cpid  ,cpnumber,cpname,cpaltername,cpshortcut from prpo_company ";
        employee_expend_obj = None
        record = {}
        try:
            cursor = connection.cursor()
            cursor.execute(sql)
            prpocompanyInstance = cursor.fetchall()
        except db.OperationalError as e:
            is_error = True
            error_message = "<b>Error: please send this error to IT team</b><br>" + str(e)
        except db.Error as e:
            is_error = True
            error_message = "<b>Error: please send this error to IT team</b><br>" + str(e)
        finally:
            cursor.close()
        #prpocompanyInstance = PrpoCompany.objects.raw("Select cpid as id ,cpnumber,cpname,cpaltername,cpshortcut from prpo_company ")
        return prpocompanyInstance



