from django.db import models


class EleaveReports(models.Model):
    class Meta:
        permissions = (
            ("can_view_m1_report", "Can view M1 report"),
            # ("can_view_m1_pending_leave_request_report", "Can view M1 pending leave request report"),
            ("can_view_m1_approved_leave_request_report", "Can view M1 approved leave request report"),
        )
