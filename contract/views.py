from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .models import TclContractQty, TclDailyWorking
from django.shortcuts import get_object_or_404


class ContractListView(PermissionRequiredMixin, generic.ListView):
    template_name = 'contract/contract_list.html'    
    permission_required = ('contract.view_tclcontractqty')
    model = TclContractQty
    #paginate_by = 12

    def get_queryset(self):
        return TclContractQty.objects.all()


class ContractDetailView(PermissionRequiredMixin, generic.DetailView):
	permission_required = 'contract.view_tclcontractqty'
	template_name = 'contract/contract_detail.html'
	model = TclContractQty

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['cnt_id'] = self.kwargs['pk']
		context['TclContractQty'] = TclContractQty.objects.all()
		context['TclDailyWorking'] = TclDailyWorking.objects.filter(cnt_id__exact=context['cnt_id']).order_by('shf_type')
		return context

	"""
	def contract_detail_view(request, primary_key):
	    try:
	        contract = TclContractQty.objects.get(pk=primary_key)
	    except TclContractQty.DoesNotExist:
	        raise Http404('Contract does not exist')
	    
	    return render(request, 'contract/contract_detail.html', context={'contract': contract})
	"""
