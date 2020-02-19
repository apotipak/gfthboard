from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('staff-profile', views.StaffProfile, name='staff-profile'),
]
