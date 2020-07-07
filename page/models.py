from django.db import models
from django.contrib.auth.models import User


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
