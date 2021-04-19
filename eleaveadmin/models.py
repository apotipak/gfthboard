from django.db import models

class EleaveAdmin(models.Model):
    class Meta:
        permissions = (
        	("is_eleave_admin", "This is an eleave administrator"),
            ("can_create_m1_leave_request", "Can create M1 leave request"),
            ("can_create_m5_leave_request", "Can create M5 leave request"),
        )
