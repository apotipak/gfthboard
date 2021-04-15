from django.urls import path
from . import views

urlpatterns = [

    path('prpo-company/', views.v_prpo_company, name='prpo_company'),

]