from django.urls import path
from . import views


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

