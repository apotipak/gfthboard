from django.urls import path
from . import views
from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.ViewM1Report, name='view_m1_report'),
    path('view-m1-leave-report', views.ViewM1LeaveReport, name='view_m1_leave_report'),

    path('view-m3-report', views.ViewM3Report, name='view_m3_report'),
    path('view-m3-leave-report', views.ViewM3LeaveReport, name='view_m3_leave_report'),

    path('view-m5-report', views.ViewM5Report, name='view_m5_report'),
    path('view-m5-leave-report', views.ViewM5LeaveReport, name='view_m5_leave_report'),
]
