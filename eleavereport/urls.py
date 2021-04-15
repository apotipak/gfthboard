from django.urls import path
from . import views
from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.ViewM1Report, name='view_m1_report'),
    # path('view-m1-pending-leave-request-report', views.ViewM1PendingLeaveRequestReport, name='view_m1_pending_leave_request_report'),
    path('view-m1-approved-leave-request-report', views.ViewM1ApprovedLeaveRequestReport, name='view_m1_approved_leave_request_report'),
]
