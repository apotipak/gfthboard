from django.urls import path
from . import views
from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.EPaySlipM1, name='e_payslip_m1'),
    url(r'^ajax/send_pay_slip_m1/$', views.AjaxSendPayslipM1, name='ajax_send_pay_slip_m1'),
    # url(r'^ajax/generate_payslip_m1/(?P<emp_id>\d+)/(?P<period>\w+)/$', views.generate_payslip_m1, name='generate_payslip_m1'),
]
