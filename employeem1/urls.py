from django.urls import path
from . import views
from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    # path('', views.EmployeeM1Dashboard, name='employee_m1_dashboard'),
    path('payslip/', views.EmployeeM1PaySlip, name='employee_m1_pay_slip'),

    # url(r'^ajax/create_m1_leave_request/$', views.AjaxCreateM1LeaveRequest, name='ajax_create_m1_leave_request'),
    # url(r'^ajax/search_employee/$', views.ajax_search_employee, name='ajax_search_employee'),
]
