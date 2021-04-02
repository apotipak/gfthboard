from django.urls import path
from . import views

urlpatterns = [

    path('ITcontract-policy/', views.ITcontractPolicy, name='ITcontract_policy'),

]