from django.urls import path
from . import views
from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('leave-policy/', views.LeavePolicy, name='leave_policy'),
    path('leave-history/', views.EmployeeInstanceListView.as_view(), name='leave_history'),
    path('leave-history/<int:pk>', views.EmployeeInstanceDetailView.as_view(), name='leave_history_detail'),
    path('leave-history/<uuid:pk>/delete/', views.EmployeeInstanceDelete.as_view(), name='leave_history_delete'),
    path('leave-timeline/', views.LeaveTimeline, name='leave_timeline'),
]

urlpatterns += [
    path('leave-approval/', views.LeaveApprovalListView.as_view(), name='leave_approval'),
    path('leave-approval/<uuid:pk>/approve/', views.EmployeeInstanceApprove, name='leave_approve'),
    path('leave-approval/<uuid:pk>/reject/', views.EmployeeInstanceReject, name='leave_reject'),
]

urlpatterns += [
    path('employee/create/', views.EmployeeNew, name='employee_create'),
]

urlpatterns += [
	url(r'^ajax/get_leave_reject_comment/(?P<pk>[^/]+)/$', views.get_leave_reject_comment, name='get_leave_reject_comment'),
    url(r'^ajax/get_leave_reason/(?P<pk>[^/]+)/$', views.get_leave_reason, name='get_leave_reason'),
    url(r'^ajax/m1817_check_leave_request_day/$', views.m1817_check_leave_request_day, name='m1817_check_leave_request_day'),
    url(r'^ajax/m1247_check_leave_request_day/$', views.m1247_check_leave_request_day, name='m1247_check_leave_request_day'),    
]


