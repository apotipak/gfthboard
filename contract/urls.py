from django.urls import path
from . import views


urlpatterns = [
	path('contract-list/', views.ContractListView.as_view(), name='contract-list'),
	path('contract-detail/<str:pk>', views.ContractDetailView.as_view(), name='contract-detail'),
]