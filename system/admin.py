from django.contrib import admin
from .models import ContractPolicy


class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'created_on')
    search_fields = ['name', 'email']
    ordering = ['-name']
    list_filter = ['active']
    date_hierarchy = 'created_on'


class ContractPolicyAdmin(admin.ModelAdmin):    
	list_diaplay = ['username', 'zone_id', 'ComZone__zone_th']
	search_fields = ['username__username', 'zone_id__zone_en']


admin.site.register(ContractPolicy, ContractPolicyAdmin)
