from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .models import TclContractQty, TclDailyWorking
from django.shortcuts import get_object_or_404
from django.conf import settings


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
		context.update({
			'page_title': settings.PROJECT_NAME,
			'today_date': settings.TODAY_DATE,
			'project_version': settings.PROJECT_VERSION,
			'db_server': settings.DATABASES['default']['HOST'],
			'project_name': settings.PROJECT_NAME,
		})
		return context

	def get_queryset(self):
		current_login_user = self.request.user.username
		return TclContractQty.objects.all()


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
		model = TclContractQty		
		return context

	"""
	def contract_detail_view(request, primary_key):
	    try:
	        contract = TclContractQty.objects.get(pk=primary_key)
	    except TclContractQty.DoesNotExist:
	        raise Http404('Contract does not exist')
	    
	    return render(request, 'contract/contract_detail.html', context={'contract': contract})
	"""
