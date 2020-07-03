from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('staff-profile', views.StaffProfile, name='staff-profile'),
    path('staff-password', views.StaffPassword, name='staff-password'),
    path('staff-language', views.StaffLanguage, name='staff-language'),
    path('faq', views.faq, name='faq'),
    path('what-is-new', views.whatisnew, name='what-is-new'),
    path('help-eleave', views.HelpEleave, name='help-eleave'),    
]
