from django.urls import path
from django.conf.urls import url
from . import views

urlpatterns = [
    # Master Table
    path('', views.welcome, name='prpo-welcome'),
    path('currency/', views.currency, name='prpo-currency'),

    # Company
    path('company/list/', views.company_list, name='prpo-company-list'),
    path('company/manage/', views.company_manage, name='prpo-company-manage'),
    path('company/ajax-save-company/', views.ajax_save_company, name='prpo-ajax-save-company'),

    # url(r'^company/manage/(?P<company_id>\d+)/$', views.company_manage, name='prpo-company-manage'),
    # path('company/manage/', views.company_manage, name='prpo-company-manage'),

    path('department/', views.department, name='prpo-department'),
    path('user/', views.user, name='prpo-user'),
    path('category/', views.category, name='prpo-category'),
    path('item/', views.item, name='prpo-item'),
    path('vendor/', views.vendor, name='prpo-vendor'),

    # PR/PO
    path('pr-entry-inquiry/', views.pr_entry_inquiry, name='pr-entry-inquiry'),
    path('pr-inbox/', views.pr_inbox, name='prpo-pr-inbox'),
    path('po-inbox/', views.po_inbox, name='prpo-po-inbox'),

    # Get subcategory list based on category id
    url(r'^ajax-get-subcategory-list/(?P<category_id>\w+)/$', views.ajax_get_subcategory_list, name='prpo-ajax-get-subcategory-list'),

    # Get item list based on subcategory id
    url(r'^ajax-get-item-list-by-subcategory-id/(?P<subcategory_id>\w+)/$', views.ajax_get_item_list_by_subcategory_id, name='prpo-ajax-get-item-list-by-subcategory-id'),

    # PR Inquiry
    path('ajax-pr-inquiry/', views.ajax_pr_inquiry_list, name='ajax-pr-inquiry'),

    # PR Entry
    path('pr-entry/', views.pr_entry, name='pr-entry'),
    
]