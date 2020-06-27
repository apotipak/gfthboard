from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .models import TclContractQty, TclDailyWorking
from system.models import ContractPolicy
from leave.models import LeaveEmployee
from django.shortcuts import get_object_or_404
from django.conf import settings
from page.rules import *
from django.utils import translation


class ContractListView(PermissionRequiredMixin, generic.ListView):
	page_title = settings.PROJECT_NAME
	db_server = settings.DATABASES['default']['HOST']
	project_name = settings.PROJECT_NAME
	project_version = settings.PROJECT_VERSION
	today_date = settings.TODAY_DATE
	template_name = 'contract/contract_list.html'    
	permission_required = ('contract.view_tclcontractqty')
	model = TclContractQty
	
	def get_context_data(self, **kwargs):
		context = super(ContractListView, self).get_context_data(**kwargs)

		user_language = getDefaultLanguage(self.request.user.username)
		translation.activate(user_language)

		if user_language == "th":
			username_display = LeaveEmployee.objects.filter(emp_id=self.request.user.username).values_list('emp_fname_th', flat=True).get()
		else:
			username_display = LeaveEmployee.objects.filter(emp_id=self.request.user.username).values_list('emp_fname_en', flat=True).get()		

		context.update({
			'page_title': settings.PROJECT_NAME,
			'today_date': settings.TODAY_DATE,
			'project_version': settings.PROJECT_VERSION,
			'db_server': settings.DATABASES['default']['HOST'],
			'project_name': settings.PROJECT_NAME,
			'username_display': username_display,
		})

		return context

	def get_zone_list(self):
		username = self.request.user.username
		zone_list = ContractPolicy.objects.get(username__exact=username)

		return zone_list

	def get_queryset(self):
		username = self.request.user.username
		contract_policy_list = ContractPolicy.objects.select_related('zone', 'user').filter(username__exact=username).values('zone__zone_en')
		queryset = TclContractQty.objects.filter(zone_en__in=[contract_policy_list])

		return queryset


class ContractDetailView(PermissionRequiredMixin, generic.DetailView):
	page_title = settings.PROJECT_NAME
	db_server = settings.DATABASES['default']['HOST']
	project_name = settings.PROJECT_NAME
	project_version = settings.PROJECT_VERSION
	today_date = settings.TODAY_DATE
	template_name = 'contract/contract_detail.html'    
	permission_required = ('contract.view_tclcontractqty')
	model = TclContractQty

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)

		user_language = getDefaultLanguage(self.request.user.username)
		translation.activate(user_language)

		if user_language == "th":
			username_display = LeaveEmployee.objects.filter(emp_id=self.request.user.username).values_list('emp_fname_th', flat=True).get()
		else:
			username_display = LeaveEmployee.objects.filter(emp_id=self.request.user.username).values_list('emp_fname_en', flat=True).get()		

		context['cnt_id'] = self.kwargs['pk']
		context['TclContractQty'] = TclContractQty.objects.all()
		context['TclDailyWorking'] = TclDailyWorking.objects.filter(cnt_id__exact=context['cnt_id']).order_by('shf_type')
		context['page_title'] = settings.PROJECT_NAME
		context['db_server'] = settings.DATABASES['default']['HOST']
		context['project_name'] = settings.PROJECT_NAME
		context['project_version'] = settings.PROJECT_VERSION
		context['today_date'] = settings.TODAY_DATE
		context['template_name'] = 'contract/contract_detail.html'    
		context['permission_required'] = ('contract.view_tclcontractqty')
		context['username_display'] = username_display

		return context

	def get_queryset(self):
		username = self.request.user.username
		contract_id = self.kwargs['pk']
		contract_policy_list = ContractPolicy.objects.select_related('zone', 'user').filter(username__exact=username).values('zone__zone_en')
		queryset = TclContractQty.objects.filter(cnt_id__exact=contract_id).filter(zone_en__in=[contract_policy_list])

		return queryset
