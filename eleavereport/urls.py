from django.urls import path
from . import views
from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.ViewM1Report, name='view_m1_report'),
    path('view-m1-leave-report', views.ViewM1LeaveReport, name='view_m1_leave_report'),
]
