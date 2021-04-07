from django.urls import path
from django.conf.urls import url
from . import views

urlpatterns = [

    path('', views.ITcontractPolicy, name='ITcontract'),
    url(r'^ajax_get_it_contract_item/$', views.ajax_get_it_contract_item, name='ajax_get_it_contract_item'),
    
]