from django.db import models


class EleaveReports(models.Model):
    class Meta:
        permissions = (
            ("can_view_m1_report", "Can view M1 report"),
            ("can_view_m1_leave_report", "Can view M1 leave report"),
        )
