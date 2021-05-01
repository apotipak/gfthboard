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
from decimal import Decimal
from os import path
import django.db as db
import csv
import subprocess, sys


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

	# Get latest updated date
	latest_updated = OutlookEmailActiveUserList.objects.values_list('created_date', flat=True).first()

	office_365_email_list = []
	record = {}

	# Get current email list
	outlook_email = OutlookEmailActiveUserList.objects.all().order_by('first_name')
	if outlook_email is None:
		office_365_email_list = None
	else:
		count = 0
		for item in outlook_email:
			record = {
				"first_name": item.first_name,
				"last_name": item.last_name,
				"email": item.email,
			}

			office_365_email_list.append(record)
			count = count + 1

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
		'last_updated': latest_updated.strftime("%d/%m/%Y %H:%M:%S"),
		'office_365_email_list': office_365_email_list,
		'total': count,
	})


@permission_required('system.add_outlookemailactiveuserlist', login_url='/accounts/login/')
def ImportOutlokActiveUser(request):
	# Get latest updated date
	latest_updated = OutlookEmailActiveUserList.objects.values_list('created_date', flat=True).first()
	total = 0
	count = 0	
	office_365_email_list = []
	record = {}

	cred_file = path.abspath("temp\\cred.txt")
	if path.exists(cred_file):
		cred_file_is_existed = True
	else:
		cred_file_is_existed = False

	if cred_file_is_existed:
		try:
			p = subprocess.Popen(["powershell.exe", "C:\\gfthboard\\temp\\email_script_1.ps1"], cwd="C:\\gfthboard\\temp", stdout=sys.stdout)
			p.communicate()			

			# Get latest updated date
			latest_updated = OutlookEmailActiveUserList.objects.values_list('created_date', flat=True).first()

			csv_file = path.abspath("media\\system\\export_outlook_365_email.csv")
			if path.exists(csv_file):
				csv_file_is_existed = True
			else:
				csv_file_is_existed = False

			if csv_file_is_existed:
				try:
					record = {}
					with open(csv_file, newline='', encoding='utf-8') as csvfile:
						reader = csv.reader(csvfile)
						next(reader)
						next(reader)
						data = list(reader)

					OutlookEmailActiveUserList.objects.all().delete()

					save_time = datetime.now()
					
					for item in data:
						if item[2] != "" and item[2] is not None:
							emp_id = Decimal(item[2])
						else:
							emp_id = None

						first_name = item[0]
						last_name = item[1]
						email = item[4]

						record = {
							"first_name": first_name,
							"last_name": last_name,
							"email": email,							
						}

						office_365_email_list.append(record)
						count = count + 1
						outlook_obj = OutlookEmailActiveUserList(first_name=first_name, last_name=last_name, email=email, emp_id=emp_id, created_date=save_time)
						outlook_obj.save()

					# Get latest updated date
					latest_updated = OutlookEmailActiveUserList.objects.values_list('created_date', flat=True).first()

					is_error = False
					message = "Success"

				except Exception as e:
					is_error = True
					message = str(e)
			else:
				print("If csv file is not existed, do nothing.")
				is_error = True
				message = "Export file is not existed."

		except subprocess.CalledProcessError as e:
			is_error = True
			message = str(e)

	else:
		is_error = True
		message = "ระบบไม่อนุญาติให้ดึงไฟล์จาก Office 365"
	
	response = JsonResponse(data={        
		"is_error": is_error,
		"message": message,
		"latest_updated": latest_updated.strftime("%d/%m/%Y %H:%M:%S"),
		"office_365_email_list": list(office_365_email_list),
		"total": count,
	})

	response.status_code = 200
	return response
