from django.db import models


class EleaveReports(models.Model):
    class Meta:
        permissions = (
            ("can_view_m1_report", "Can view M1 reports"),
            ("can_view_m1_leave_report", "Can view M1 leave report"),
            ("can_view_m3_report", "Can view M3 reports"),
            ("can_view_m3_leave_report", "Can view M3 leave report"),            
            ("can_view_m5_report", "Can view M5 reports"),
            ("can_view_m5_leave_report", "Can view M5 leave report"),
        )
