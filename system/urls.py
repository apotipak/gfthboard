from django.urls import path
from . import views
from django.conf.urls import url


urlpatterns = [
	#path('contract-list/', views.ContractListView.as_view(), name='contract-list'),
	path('', views.ManageOutlookEmailActiveUserList, name='manage_outlook_email_active_user_list'),
	url(r'^ajax/import_outlook_active_user/$', views.ImportOutlokActiveUser, name='ajax_import_outlook_active_user'),
]