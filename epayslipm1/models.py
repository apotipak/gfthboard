from django.db import models


class EPayslipM1(models.Model):
    class Meta:
        permissions = (
            ("can_access_e_payslip_m1", "Able to access E-Payslip M1."),
        )
        managed = False
        db_table = 'sp_slip1'
