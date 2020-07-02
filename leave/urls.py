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
    path('leave-pending-approve/', views.LeavePendingApproveListView.as_view(), name='leave_pending_approve'),
    path('leave-approval/<uuid:pk>/approve/', views.EmployeeInstanceApprove, name='leave_approve'),
    path('leave-approval/<uuid:pk>/reject/', views.EmployeeInstanceReject, name='leave_reject'),

    path('leave-approved/', views.LeaveApprovedListView.as_view(), name='leave_approved'),
    path('leave-rejected/', views.LeaveRejectedListView.as_view(), name='leave_rejected'),
]

urlpatterns += [
    path('employee/create/', views.EmployeeNew, name='employee_create'),
]

urlpatterns += [
	url(r'^ajax/get_leave_reject_comment/(?P<pk>[^/]+)/$', views.get_leave_reject_comment, name='get_leave_reject_comment'),
    url(r'^ajax/get_leave_reason/(?P<pk>[^/]+)/$', views.get_leave_reason, name='get_leave_reason'),
    url(r'^ajax/get_employee_leave_history/(?P<emp_id>[^/]+)/$', views.get_employee_leave_history, name='get_employee_leave_history'),
    url(r'^ajax/m1817_check_leave_request_day/$', views.m1817_check_leave_request_day, name='m1817_check_leave_request_day'),
    url(r'^ajax/m1247_check_leave_request_day/$', views.m1247_check_leave_request_day, name='m1247_check_leave_request_day'),    
]


