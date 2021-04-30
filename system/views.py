from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .models import ContractPolicy, OutlookEmailActiveUserList
from django.shortcuts import get_object_or_404
from django.conf import settings
from leave.models import LeaveEmployee
from gfthboard.settings import MEDIA_ROOT
from page.rules import *
from django.db import connections
from datetime import datetime
from django.http import JsonResponse
from django.utils import translation
from django.utils.translation import ugettext as _
# from numpy import genfromtxt
from decimal import Decimal
from os import path
import django.db as db
import csv


class ContractPolicyListView(PermissionRequiredMixin, generic.ListView):
	page_title = settings.PROJECT_NAME
	db_server = settings.DATABASES['default']['HOST']
	project_name = settings.PROJECT_NAME
	project_version = settings.PROJECT_VERSION
	today_date = settings.TODAY_DATE
	template_name = 'system/contract_policy_list.html'    
	permission_required = ('system.view_contract_policy')

	def get_zone_list(self):
		username = self.request.user.username
		zone_list = ContractPolicy.objects.get(username__exact=username)
		return zone_list

	
	"""
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
	"""


@permission_required('system.add_outlookemailactiveuserlist', login_url='/accounts/login/')
def ManageOutlookEmailActiveUserList(request):
	dummy_data = False

	user_language = getDefaultLanguage(request.user.username)
	translation.activate(user_language)
	render_template_name = 'system/outlook_active_user_list.html'

	dattime_format = "%Y-%m-%d %H:%M:%S"

	page_title = settings.PROJECT_NAME
	db_server = settings.DATABASES['default']['HOST']
	project_name = settings.PROJECT_NAME
	project_version = settings.PROJECT_VERSION
	today_date = getDateFormatDisplay(user_language)

	available_period_obj = None
	available_period_list = []
	record = {}

	# For temporarially used only
	# Start
	if user_language == "th":
	    if request.user.username == "999999":
	    	username_display = request.user.first_name
	    else:
	        username_display = LeaveEmployee.objects.filter(emp_id=request.user.username).values_list('emp_fname_th', flat=True).get()
	else:
	    if request.user.username == "999999":
	        username_display = request.user.first_name
	    else:
	        username_display = LeaveEmployee.objects.filter(emp_id=request.user.username).values_list('emp_fname_en', flat=True).get()
	# End

	return render(request, render_template_name, {
		'page_title': settings.PROJECT_NAME,
		'today_date': today_date,
		'project_version': settings.PROJECT_VERSION,
		'db_server': settings.DATABASES['default']['HOST'],
		'project_name': settings.PROJECT_NAME,
		'user_language': user_language,
		'username_display': username_display,
		'available_period_obj': available_period_obj,
		'available_period_list': list(available_period_list),
	})



@permission_required('system.add_outlookemailactiveuserlist', login_url='/accounts/login/')
def ImportOutlokActiveUser(request):	
	
	csv_file = path.abspath("media\\system\\outlook.csv")

	try:
		with open(csv_file, newline='', encoding='utf-8') as csvfile:
			reader = csv.reader(csvfile)
			next(reader)
			data = list(reader)
		
		OutlookEmailActiveUserList.objects.all().delete()
		for item in data:

			if item[29] != "":
				# print(item[29])
				emp_id = Decimal(item[29])
			else:
				# print("blank")
				emp_id = None

			first_name = item[8]
			last_name = item[10]
			email = item[31]

			p = OutlookEmailActiveUserList(first_name=first_name, last_name=last_name, email=email, emp_id=emp_id)			
			p.save()
		
		is_error = False
		message = "Success"

	except Exception as e:
		is_error = True
		message = str(e)


	# TEST
	'''
	try:
		sql = "select count(*) from employee;"
		cursor = connections['reportdb'].cursor()
		cursor.execute(sql)
		leave_employeeinstance_object = cursor.fetchone()
		error_message = "No error"
	except db.OperationalError as e:
		error_message = "<b>Error: please send this error to IT team</b><br>" + str(e)      
	except db.Error as e:
	    error_message = "<b>Error: please send this error to IT team</b><br>" + str(e)
	finally:
	    cursor.close()

	if leave_employeeinstance_object is not None:
		print("HRMS-Employee 51 : ", leave_employeeinstance_object[0])
	else:
		print("ERROR")
	'''
	# TEST


	# TEST
	'''
	try:
		sql = "select count(*) from employee;"
		cursor = connections['hrms14'].cursor()
		cursor.execute(sql)
		leave_employeeinstance_object = cursor.fetchone()
		error_message = "No error"
	except db.OperationalError as e:
		error_message = "<b>Error: please send this error to IT team</b><br>" + str(e)      
	except db.Error as e:
	    error_message = "<b>Error: please send this error to IT team</b><br>" + str(e)
	except Exception as e:
		error_message = str(e)
	finally:
	    cursor.close()

	print(error_message)
	'''

	'''
	if leave_employeeinstance_object is not None:
		print("HRMS-Employee 14 : ", leave_employeeinstance_object[0])
	else:
		print("ERROR")
	'''
	# TEST



	# from django.db import connections
	# cursor = connections['reportdb'].cursor()
	# cursor.execute("select * from leave_employeeinstance")
	# cursor.close()

	response = JsonResponse(data={        
		"is_error": is_error,
		"message": message,
	})

	response.status_code = 200
	return response
