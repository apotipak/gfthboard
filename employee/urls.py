from django.urls import path
from . import views


urlpatterns = [
	path('employee-list/', views.employeeListView.as_view(), name='employee-list'),
	path('employee-detail/<str:pk>', views.employeeDetailView.as_view(), name='employee-detail'),
]