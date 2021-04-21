from django.db import models


class EmployeeM1(models.Model):
    class Meta:
        permissions = (
            ("can_access_employee_m1", "Able to access M1 employee application."),
            ("can_access_employee_m1_pay_slip", "Able to access M1 employee pay slip."),
        )
