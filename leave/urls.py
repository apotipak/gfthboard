from django.urls import path
from . import views
from django.conf.urls import url


urlpatterns = [
    path('leave-policy/', views.LeavePolicy, name='leave_policy'),
    path('leave-history/', views.EmployeeInstanceListView.as_view(), name='leave_history'),
    path('leave-history/<int:pk>', views.EmployeeInstanceDetailView.as_view(), name='leave_history_detail'),
    path('leave-history/<uuid:pk>/delete/', views.EmployeeInstanceDelete.as_view(), name='leave_history_delete'),
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
    url(r'^ajax/check_leave_request_day/$', views.check_leave_request_day, name='check_leave_request_day'),
	#url(r'^ajax/get_hour_range/$', views.get_hour_range, name='get_hour_range'),
]