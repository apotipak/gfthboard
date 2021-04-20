from django.urls import path
from django.conf.urls import url
from . import views

urlpatterns = [

    path('', views.ITcontractPolicy, name='ITcontract'),

    # Add
    url(r'^ajax_add_it_contract_item/$', views.ajax_add_it_contract_item, name='ajax_add_it_contract_item'),

    # Edit
    url(r'^ajax_get_it_contract_item/$', views.ajax_get_it_contract_item, name='ajax_get_it_contract_item'),

    # Update
    url(r'^ajax_save_it_contract_item/$', views.ajax_save_it_contract_item, name='ajax_save_it_contract_item'),
    
    # Delete   
    url(r'^ajax_delete_it_contract_item/$', views.ajax_delete_it_contract_item, name='ajax_delete_it_contract_item'),

    # Download
    url(r'^view_contract_document/(?P<it_contract_id>[^/]+)/$', views.view_contract_document, name='view_contract_document'),

    # Print
    url(r'^print-it-contract-report/$', views.ajax_print_it_contract_report, name='print-it-contract-report'),

    # Export
    url(r'^export-it-contract-to-excel/$', views.export_it_contract_to_excel, name='export_it_contract_to_excel'), 

    # Alert Setting
    path('alert-setting/', views.ITcontractAlertSetting, name='it_contract_alert_setting'),
    url(r'^ajax/update-email-alert-setting/$', views.AjaxUpdateEmailAlertSetting, name='ajax-update-email-alert-setting'),
]
