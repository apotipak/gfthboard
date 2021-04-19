from django.urls import path
from . import views
from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('create-m1-leave-request', views.CreateM1LeaveRequest, name='create_m1_leave_request'),
    url(r'^ajax/search_employee/$', views.ajax_search_employee, name='ajax_search_employee'),
]
