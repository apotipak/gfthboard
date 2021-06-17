from django.shortcuts import render
from django.utils import timezone
from datetime import datetime
from django.conf import settings
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required
from django.utils import translation
from django.utils.translation import ugettext as _
import django.db as db
from django.db import connection
from page.rules import *
from django.utils import timezone
from leave.models import LeaveEmployee
from page.rules import *


@permission_required('eleavereport.can_view_m3_report', login_url='/accounts/login/')
def ViewM3Report(request):
	if isStillUseDefaultPassword(request):
		template_name = 'page/force_change_password.html'
		return render(request, template_name, {})
	else:
		if isPasswordExpired(request):
			if isPasswordChanged(request):
				template_name = 'page/force_change_password.html'
				return render(request, template_name, {})

	user_language = getDefaultLanguage(request.user.username)
	translation.activate(user_language)	
	page_title = settings.PROJECT_NAME
	db_server = settings.DATABASES['default']['HOST']
	project_name = settings.PROJECT_NAME
	project_version = settings.PROJECT_VERSION

	today_day = timezone.now().strftime('%d')
	today_month = timezone.now().strftime('%m')
	today_year = timezone.now().year
	today_date = str(today_day) + "-" + today_month + "-" + str(today_year)	

	start_date = today_date if request.POST.get('start_date') is None else request.POST.get('start_date')
	end_date = today_date if request.POST.get('end_date') is None else request.POST.get('end_date')
	convertDateToYYYYMMDD(start_date)

	print("start_date:", start_date)
	print("end_date:", end_date)

	leave_request_pending_object = None	
	# sql = "select emp_id,leave_type_id,start_date,end_date,created_date from leave_employeeinstance where year(start_date)=year(getdate()) and status='p' "	

	sql = "select l.emp_id,e.emp_fname_th,e.emp_lname_th,e.pos_th,e.div_th,l.leave_type_id,lt.lve_th,l.start_date,l.end_date,l.created_date,"
	sql += "l.lve_act,l.lve_act_hr,l.document "
	# sql += "from leave_employeeinstance l "
	sql += "from leave_act l "
	sql += "left join leave_employee e on l.emp_id=e.emp_id "
	sql += "left join leave_type lt on l.leave_type_id=lt.lve_id "
	sql += "where year(start_date)=year(getdate()) and status='p' "
	sql += "and l.start_date between CONVERT(datetime,'" + convertDateToYYYYMMDD(start_date) + "') and "
	sql += "CONVERT(datetime,'" + convertDateToYYYYMMDD(end_date) + " 23:59:59:999') and "
	sql += "l.emp_type='M3' "
	sql += "order by created_date desc;"
	print("SQL:", sql)

	try:				
		cursor = connection.cursor()
		cursor.execute(sql)
		leave_request_pending_object = cursor.fetchall()
		error_message = "No error"
	except db.OperationalError as e:
		error_message = "<b>Error: please send this error to IT team</b><br>" + str(e)		
	except db.Error as e:
		error_message = "<b>Error: please send this error to IT team</b><br>" + str(e)
	finally:
		cursor.close()

	record = {}	
	leave_request_pending_list = []

	if leave_request_pending_object is not None:
		print("Total=", len(leave_request_pending_object))
		row_count = 1
		for item in leave_request_pending_object:				
			record = {
				"row_count": row_count,
				"emp_id": item[0],
				'emp_fname_th': item[1],
				'emp_lname_th': item[2],
				'pos_th': item[3],
				'div_th': item[4],
				"leave_type_id": item[5],
				"leave_type_th": item[6],
				"start_date": item[7],
				"end_date": item[8],
				"created_date": item[9],

			}
			leave_request_pending_list.append(record)
			row_count = row_count + 1	

	if user_language == "th":
		username_display = LeaveEmployee.objects.filter(emp_id=request.user.username).values_list('emp_fname_th', flat=True).get()
	else:
		username_display = LeaveEmployee.objects.filter(emp_id=request.user.username).values_list('emp_fname_en', flat=True).get()

	today_date = getDateFormatDisplay(user_language)

	return render(request, 'eleavereport/report_list.html', {
	    'page_title': settings.PROJECT_NAME,
	    'today_date': today_date,
	    'project_version': settings.PROJECT_VERSION,
	    'db_server': settings.DATABASES['default']['HOST'],
	    'project_name': settings.PROJECT_NAME,
	    'leave_request_pending_list': list(leave_request_pending_list),
	    'start_date': start_date,
	    'end_date': end_date,
	    'username_display': username_display,
	})


@permission_required('eleavereport.can_view_m3_leave_report', login_url='/accounts/login/')
def ViewM3LeaveReport(request):
	if isStillUseDefaultPassword(request):
		template_name = 'page/force_change_password.html'
		return render(request, template_name, {})
	else:
		if isPasswordExpired(request):
			if isPasswordChanged(request):
				template_name = 'page/force_change_password.html'
				return render(request, template_name, {})

	user_language = getDefaultLanguage(request.user.username)
	translation.activate(user_language)	
	page_title = settings.PROJECT_NAME
	db_server = settings.DATABASES['default']['HOST']
	project_name = settings.PROJECT_NAME
	project_version = settings.PROJECT_VERSION

	today_day = timezone.now().strftime('%d')
	today_month = timezone.now().strftime('%m')
	today_year = timezone.now().year
	today_date = str(today_day) + "-" + today_month + "-" + str(today_year)	

	start_date = today_date if request.POST.get('start_date') is None else request.POST.get('start_date')
	end_date = today_date if request.POST.get('end_date') is None else request.POST.get('end_date')
	convertDateToYYYYMMDD(start_date)

	print("start_date:", start_date)
	print("end_date:", end_date)

	leave_request_approved_object = None

	sql = "select l.emp_id,e.emp_fname_th,e.emp_lname_th,e.pos_th,e.div_th,l.leave_type_id,lt.lve_th,l.start_date,l.end_date,l.created_date,l.updated_date,l.updated_by,l.status,"
	sql += "l.lve_act,l.lve_act_hr,l.document "
	sql += "from leave_act l "
	sql += "left join leave_employee e on l.emp_id=e.emp_id "
	sql += "left join leave_type lt on l.leave_type_id=lt.lve_id "
	sql += "where year(start_date)=year(getdate()) and status in ('a','C','p') "
	sql += "and l.start_date between CONVERT(datetime,'" + convertDateToYYYYMMDD(start_date) + "') and "
	sql += "CONVERT(datetime,'" + convertDateToYYYYMMDD(end_date) + " 23:59:59:999') and "
	sql += "l.emp_type='M3' "
	sql += "order by created_date desc;"


	'''
	sql = "select l.emp_id,e.emp_fname_th,e.emp_lname_th,e.pos_th,e.div_th,l.leave_type_id,lt.lve_th,l.start_date,l.end_date,l.created_date,l.updated_date,l.updated_by,l.status,"
	sql += "l.lve_act,l.lve_act_hr,le.document "
	sql += "from leave_act l "
	sql += "left join leave_employeeinstance le on l.start_date=le.start_date and l.end_date=le.end_date "
	sql += "left join leave_employee e on l.emp_id=e.emp_id "
	sql += "left join leave_type lt on l.leave_type_id=lt.lve_id "	
	sql += "where year(l.start_date)=year(getdate()) and l.status in ('a','C','p') "
	sql += "and l.start_date between CONVERT(datetime,'" + convertDateToYYYYMMDD(start_date) + "') and CONVERT(datetime,'" + convertDateToYYYYMMDD(end_date) + " 23:59:59:999') and "
	sql += "l.emp_type='M3' "
	sql += "order by l.created_date desc, l.id;"
	'''

	print("SQL:", sql)

	try:
		cursor = connection.cursor()
		cursor.execute(sql)
		leave_request_approved_object = cursor.fetchall()
		error_message = "No error"
	except db.OperationalError as e:
		error_message = "<b>Error: please send this error to IT team</b><br>" + str(e)		
	except db.Error as e:
		error_message = "<b>Error: please send this error to IT team</b><br>" + str(e)
	finally:
		cursor.close()

	record = {}	
	leave_request_approved_list = []

	if leave_request_approved_object is not None:
		print("Total=", len(leave_request_approved_object))
		
		row_count = 1
		leave_act_id_temp = 0

		for item in leave_request_approved_object:
			leave_act_id = item[0]			
			attach_file = item[15] if item[15] is not None else ""
			emp_fname_th = item[1].strip() if item[1] is not None else ""
			emp_lname_th = item[2].strip() if item[2] is not None else ""

			record = {
				"row_count": row_count,
				"emp_id": item[0],
				'emp_fname_th': emp_fname_th,
				'emp_lname_th': emp_lname_th,
				'pos_th': item[3],
				'div_th': item[4],
				"leave_type_id": item[5],
				"leave_type_th": item[6],
				"start_date": item[7],
				"end_date": item[8],
				"created_date": item[9],
				"updated_date": item[10],
				"updated_by": item[11],
				"status": item[12],
				"lve_act": item[13],
				"lve_act_hr": item[13],
				"attach_file": attach_file,
			}
			
			leave_request_approved_list.append(record)
			row_count = row_count + 1

			'''
			if leave_act_id != leave_act_id_temp:
				leave_request_approved_list.append(record)
				row_count = row_count + 1
				leave_act_id_temp = leave_act_id
			'''

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

	today_date = getDateFormatDisplay(user_language)
	
	return render(request, 'eleavereport/view_m3_leave_report.html', {
	    'page_title': settings.PROJECT_NAME,
	    'today_date': today_date,
	    'project_version': settings.PROJECT_VERSION,
	    'db_server': settings.DATABASES['default']['HOST'],
	    'project_name': settings.PROJECT_NAME,
	    'leave_request_approved_list': list(leave_request_approved_list),
	    'start_date': start_date,
	    'end_date': end_date,	    
	    'username_display': username_display,
	})


@permission_required('eleavereport.can_view_m5_report', login_url='/accounts/login/')
def ViewM5Report(request):
	if isStillUseDefaultPassword(request):
		template_name = 'page/force_change_password.html'
		return render(request, template_name, {})
	else:
		if isPasswordExpired(request):
			if isPasswordChanged(request):
				template_name = 'page/force_change_password.html'
				return render(request, template_name, {})
					
	user_language = getDefaultLanguage(request.user.username)
	translation.activate(user_language)	
	page_title = settings.PROJECT_NAME
	db_server = settings.DATABASES['default']['HOST']
	project_name = settings.PROJECT_NAME
	project_version = settings.PROJECT_VERSION

	today_day = timezone.now().strftime('%d')
	today_month = timezone.now().strftime('%m')
	today_year = timezone.now().year
	today_date = str(today_day) + "-" + today_month + "-" + str(today_year)	

	start_date = today_date if request.POST.get('start_date') is None else request.POST.get('start_date')
	end_date = today_date if request.POST.get('end_date') is None else request.POST.get('end_date')
	convertDateToYYYYMMDD(start_date)

	print("start_date:", start_date)
	print("end_date:", end_date)

	leave_request_pending_object = None	
	# sql = "select emp_id,leave_type_id,start_date,end_date,created_date from leave_employeeinstance where year(start_date)=year(getdate()) and status='p' "	

	sql = "select l.emp_id,e.emp_fname_th,e.emp_lname_th,e.pos_th,e.div_th,l.leave_type_id,lt.lve_th,l.start_date,l.end_date,l.created_date,"	
	sql += "l.lve_act,l.lve_act_hr,l.document "
	# sql += "from leave_employeeinstance l "
	sql += "from leave_act l "
	sql += "left join leave_employee e on l.emp_id=e.emp_id "
	sql += "left join leave_type lt on l.leave_type_id=lt.lve_id "
	sql += "where year(start_date)=year(getdate()) and status='p' "
	sql += "and l.start_date between CONVERT(datetime,'" + convertDateToYYYYMMDD(start_date) + "') and "
	sql += "CONVERT(datetime,'" + convertDateToYYYYMMDD(end_date) + " 23:59:59:999') and "
	sql += "l.emp_type='M5' "
	sql += "order by created_date desc;"
	print("SQL M5 :", sql)

	try:				
		cursor = connection.cursor()
		cursor.execute(sql)
		leave_request_pending_object = cursor.fetchall()
		error_message = "No error"
	except db.OperationalError as e:
		error_message = "<b>Error: please send this error to IT team</b><br>" + str(e)		
	except db.Error as e:
		error_message = "<b>Error: please send this error to IT team</b><br>" + str(e)
	finally:
		cursor.close()

	record = {}	
	leave_request_pending_list = []

	if leave_request_pending_object is not None:
		print("Total=", len(leave_request_pending_object))
		row_count = 1
		for item in leave_request_pending_object:				
			record = {
				"row_count": row_count,
				"emp_id": item[0],
				'emp_fname_th': item[1],
				'emp_lname_th': item[2],
				'pos_th': item[3],
				'div_th': item[4],
				"leave_type_id": item[5],
				"leave_type_th": item[6],
				"start_date": item[7],
				"end_date": item[8],
				"created_date": item[9],

			}
			leave_request_pending_list.append(record)
			row_count = row_count + 1	

	if user_language == "th":
		username_display = LeaveEmployee.objects.filter(emp_id=request.user.username).values_list('emp_fname_th', flat=True).get()
	else:
		username_display = LeaveEmployee.objects.filter(emp_id=request.user.username).values_list('emp_fname_en', flat=True).get()

	today_date = getDateFormatDisplay(user_language)

	return render(request, 'eleavereport/report_list.html', {
	    'page_title': settings.PROJECT_NAME,
	    'today_date': today_date,
	    'project_version': settings.PROJECT_VERSION,
	    'db_server': settings.DATABASES['default']['HOST'],
	    'project_name': settings.PROJECT_NAME,
	    'leave_request_pending_list': list(leave_request_pending_list),
	    'start_date': start_date,
	    'end_date': end_date,
	    'username_display': username_display,
	})


@permission_required('eleavereport.can_view_m5_leave_report', login_url='/accounts/login/')
def ViewM5LeaveReport(request):
	if isStillUseDefaultPassword(request):
		template_name = 'page/force_change_password.html'
		return render(request, template_name, {})
	else:
		if isPasswordExpired(request):
			if isPasswordChanged(request):
				template_name = 'page/force_change_password.html'
				return render(request, template_name, {})

	user_language = getDefaultLanguage(request.user.username)
	translation.activate(user_language)	
	page_title = settings.PROJECT_NAME
	db_server = settings.DATABASES['default']['HOST']
	project_name = settings.PROJECT_NAME
	project_version = settings.PROJECT_VERSION

	today_day = timezone.now().strftime('%d')
	today_month = timezone.now().strftime('%m')
	today_year = timezone.now().year
	today_date = str(today_day) + "-" + today_month + "-" + str(today_year)	

	start_date = today_date if request.POST.get('start_date') is None else request.POST.get('start_date')
	end_date = today_date if request.POST.get('end_date') is None else request.POST.get('end_date')
	convertDateToYYYYMMDD(start_date)

	print("start_date:", start_date)
	print("end_date:", end_date)

	leave_request_approved_object = None	

	sql = "select l.emp_id,e.emp_fname_th,e.emp_lname_th,e.pos_th,e.div_th,l.leave_type_id,lt.lve_th,l.start_date,l.end_date,l.created_date,l.updated_date,l.updated_by,l.status,"	
	sql += "l.lve_act,l.lve_act_hr,l.document "
	sql += "from leave_act l "
	sql += "left join leave_employee e on l.emp_id=e.emp_id "
	sql += "left join leave_type lt on l.leave_type_id=lt.lve_id "
	sql += "where year(start_date)=year(getdate()) and status in ('a','C','p') "
	sql += "and l.start_date between CONVERT(datetime,'" + convertDateToYYYYMMDD(start_date) + "') and "
	sql += "CONVERT(datetime,'" + convertDateToYYYYMMDD(end_date) + " 23:59:59:999') and "
	sql += "l.emp_type='M5' "
	sql += "order by created_date desc;"

	'''
	sql = "select l.emp_id,e.emp_fname_th,e.emp_lname_th,e.pos_th,e.div_th,l.leave_type_id,lt.lve_th,l.start_date,l.end_date,l.created_date,l.updated_date,l.updated_by,l.status,"
	sql += "l.lve_act,l.lve_act_hr,le.document "
	sql += "from leave_act l "
	sql += "left join leave_employeeinstance le on l.start_date=le.start_date and l.end_date=le.end_date "
	sql += "left join leave_employee e on l.emp_id=e.emp_id "
	sql += "left join leave_type lt on l.leave_type_id=lt.lve_id "	
	sql += "where year(l.start_date)=year(getdate()) and l.status in ('a','C','p') "
	sql += "and l.start_date between CONVERT(datetime,'" + convertDateToYYYYMMDD(start_date) + "') and CONVERT(datetime,'" + convertDateToYYYYMMDD(end_date) + " 23:59:59:999') and "
	sql += "l.emp_type='M5' "
	sql += "order by l.created_date desc, l.id;"
	'''

	print("SQL:", sql)

	try:				
		cursor = connection.cursor()
		cursor.execute(sql)
		leave_request_approved_object = cursor.fetchall()
		error_message = "No error"
	except db.OperationalError as e:
		error_message = "<b>Error: please send this error to IT team</b><br>" + str(e)		
	except db.Error as e:
		error_message = "<b>Error: please send this error to IT team</b><br>" + str(e)
	finally:
		cursor.close()

	record = {}	
	leave_request_approved_list = []

	if leave_request_approved_object is not None:
		print("Total=", len(leave_request_approved_object))
		
		row_count = 1
		leave_act_id_temp = 0

		for item in leave_request_approved_object:
			leave_act_id = item[0]
			attach_file = item[15] if item[15] is not None else ""
			emp_fname_th = item[1].strip() if item[1] is not None else ""
			emp_lname_th = item[2].strip() if item[2] is not None else ""

			record = {
				"row_count": row_count,
				"emp_id": item[0],
				'emp_fname_th': emp_fname_th,
				'emp_lname_th': emp_lname_th,
				'pos_th': item[3],
				'div_th': item[4],
				"leave_type_id": item[5],
				"leave_type_th": item[6],
				"start_date": item[7],
				"end_date": item[8],
				"created_date": item[9],
				"updated_date": item[10],
				"updated_by": item[11],
				"status": item[12],
				"lve_act": item[13],
				"lve_act_hr": item[14],
				"attach_file": attach_file,				
			}
			
			leave_request_approved_list.append(record)
			row_count = row_count + 1

			'''
			if leave_act_id != leave_act_id_temp:
				leave_request_approved_list.append(record)
				row_count = row_count + 1
				leave_act_id_temp = leave_act_id			
			'''

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

	today_date = getDateFormatDisplay(user_language)
	
	return render(request, 'eleavereport/view_m5_leave_report.html', {
	    'page_title': settings.PROJECT_NAME,
	    'today_date': today_date,
	    'project_version': settings.PROJECT_VERSION,
	    'db_server': settings.DATABASES['default']['HOST'],
	    'project_name': settings.PROJECT_NAME,
	    'leave_request_approved_list': list(leave_request_approved_list),
	    'start_date': start_date,
	    'end_date': end_date,	    
	    'username_display': username_display,
	})


@permission_required('eleavereport.can_view_m1_report', login_url='/accounts/login/')
def ViewM1Report(request):
	if isStillUseDefaultPassword(request):
		template_name = 'page/force_change_password.html'
		return render(request, template_name, {})
	else:
		if isPasswordExpired(request):
			if isPasswordChanged(request):
				template_name = 'page/force_change_password.html'
				return render(request, template_name, {})

	user_language = getDefaultLanguage(request.user.username)
	translation.activate(user_language)	
	page_title = settings.PROJECT_NAME
	db_server = settings.DATABASES['default']['HOST']
	project_name = settings.PROJECT_NAME
	project_version = settings.PROJECT_VERSION

	today_day = timezone.now().strftime('%d')
	today_month = timezone.now().strftime('%m')
	today_year = timezone.now().year
	today_date = str(today_day) + "-" + today_month + "-" + str(today_year)	

	start_date = today_date if request.POST.get('start_date') is None else request.POST.get('start_date')
	end_date = today_date if request.POST.get('end_date') is None else request.POST.get('end_date')
	convertDateToYYYYMMDD(start_date)

	print("start_date:", start_date)
	print("end_date:", end_date)

	leave_request_pending_object = None	
	# sql = "select emp_id,leave_type_id,start_date,end_date,created_date from leave_employeeinstance where year(start_date)=year(getdate()) and status='p' "	

	# sql = "select l.emp_id,e.emp_fname_th,e.emp_lname_th,e.pos_th,e.div_th,l.leave_type_id,lt.lve_th,l.start_date,l.end_date,l.created_date,"
	# sql += "l.lve_act,l.lve_act_hr "
	sql = "select l.emp_id,e.emp_fname_th,e.emp_lname_th,e.pos_th,e.div_th,l.leave_type_id,lt.lve_th,l.start_date,l.end_date,l.created_date,l.updated_date,l.updated_by,l.status,"
	sql += "l.lve_act,l.lve_act_hr,l.document "
	# sql += "from leave_employeeinstance l "
	sql += "from leave_act l "
	sql += "left join leave_employee e on l.emp_id=e.emp_id "
	sql += "left join leave_type lt on l.leave_type_id=lt.lve_id "
	sql += "where year(start_date)=year(getdate()) and status='p' "
	sql += "and l.start_date between CONVERT(datetime,'" + convertDateToYYYYMMDD(start_date) + "') and "
	sql += "CONVERT(datetime,'" + convertDateToYYYYMMDD(end_date) + " 23:59:59:999') and "
	sql += "l.emp_type='M1' "
	sql += "order by created_date desc;"
	print("SQL:", sql)

	try:				
		cursor = connection.cursor()
		cursor.execute(sql)
		leave_request_pending_object = cursor.fetchall()
		error_message = "No error"
	except db.OperationalError as e:
		error_message = "<b>Error: please send this error to IT team</b><br>" + str(e)		
	except db.Error as e:
		error_message = "<b>Error: please send this error to IT team</b><br>" + str(e)
	finally:
		cursor.close()

	record = {}	
	leave_request_pending_list = []

	if leave_request_pending_object is not None:
		print("Total=", len(leave_request_pending_object))
		row_count = 1
		for item in leave_request_pending_object:				
			record = {
				"row_count": row_count,
				"emp_id": item[0],
				'emp_fname_th': item[1],
				'emp_lname_th': item[2],
				'pos_th': item[3],
				'div_th': item[4],
				"leave_type_id": item[5],
				"leave_type_th": item[6],
				"start_date": item[7],
				"end_date": item[8],
				"created_date": item[9],
				"updated_date": item[10],
				"updated_by": item[11],
				"status": item[12],
				"lve_act": item[13],
				"lve_act_hr": item[14],
			}
			leave_request_pending_list.append(record)
			row_count = row_count + 1	

	if user_language == "th":
		username_display = LeaveEmployee.objects.filter(emp_id=request.user.username).values_list('emp_fname_th', flat=True).get()
	else:
		username_display = LeaveEmployee.objects.filter(emp_id=request.user.username).values_list('emp_fname_en', flat=True).get()

	today_date = getDateFormatDisplay(user_language)

	return render(request, 'eleavereport/report_list.html', {
	    'page_title': settings.PROJECT_NAME,
	    'today_date': today_date,
	    'project_version': settings.PROJECT_VERSION,
	    'db_server': settings.DATABASES['default']['HOST'],
	    'project_name': settings.PROJECT_NAME,
	    'leave_request_pending_list': list(leave_request_pending_list),
	    'start_date': start_date,
	    'end_date': end_date,
	    'username_display': username_display,
	})


@permission_required('eleavereport.can_view_m1_leave_report', login_url='/accounts/login/')
def ViewM1LeaveReport(request):
	if isStillUseDefaultPassword(request):
		template_name = 'page/force_change_password.html'
		return render(request, template_name, {})
	else:
		if isPasswordExpired(request):
			if isPasswordChanged(request):
				template_name = 'page/force_change_password.html'
				return render(request, template_name, {})	
	
	user_language = getDefaultLanguage(request.user.username)
	translation.activate(user_language)	
	page_title = settings.PROJECT_NAME
	db_server = settings.DATABASES['default']['HOST']
	project_name = settings.PROJECT_NAME
	project_version = settings.PROJECT_VERSION

	today_day = timezone.now().strftime('%d')
	today_month = timezone.now().strftime('%m')
	today_year = timezone.now().year
	today_date = str(today_day) + "-" + today_month + "-" + str(today_year)	

	start_date = today_date if request.POST.get('start_date') is None else request.POST.get('start_date')
	end_date = today_date if request.POST.get('end_date') is None else request.POST.get('end_date')
	convertDateToYYYYMMDD(start_date)

	print("start_date:", start_date)
	print("end_date:", end_date)

	leave_request_approved_object = None	
	# sql = "select emp_id,leave_type_id,start_date,end_date,created_date from leave_employeeinstance where year(start_date)=year(getdate()) and status='p' "	
	
	sql = "select l.emp_id,e.emp_fname_th,e.emp_lname_th,e.pos_th,e.div_th,l.leave_type_id,lt.lve_th,l.start_date,l.end_date,l.created_date,l.updated_date,l.updated_by,l.status,"
	sql += "l.lve_act,l.lve_act_hr,l.document,l.leave_reason "
	# sql += "from leave_employeeinstance l "
	sql += "from leave_act l "
	sql += "left join leave_employee e on l.emp_id=e.emp_id "
	sql += "left join leave_type lt on l.leave_type_id=lt.lve_id "
	sql += "where year(start_date)=year(getdate()) and status in ('a','C','p') "
	sql += "and l.start_date between CONVERT(datetime,'" + convertDateToYYYYMMDD(start_date) + "') and "
	sql += "CONVERT(datetime,'" + convertDateToYYYYMMDD(end_date) + " 23:59:59:999') and "
	sql += "l.emp_type='M1' "
	sql += "order by created_date desc;"
	

	# amnaj
	'''
	sql = "select l.emp_id,e.emp_fname_th,e.emp_lname_th,e.pos_th,e.div_th,l.leave_type_id,lt.lve_th,l.start_date,l.end_date,l.created_date,l.updated_date,l.updated_by,l.status,"
	sql += "l.lve_act,l.lve_act_hr,le.document "
	sql += "from leave_act l "
	sql += "left join leave_employeeinstance le on l.start_date=le.start_date and l.end_date=le.end_date "
	sql += "left join leave_employee e on l.emp_id=e.emp_id "
	sql += "left join leave_type lt on l.leave_type_id=lt.lve_id "	
	sql += "where year(l.start_date)=year(getdate()) and l.status in ('a','C','p') "
	sql += "and l.start_date between CONVERT(datetime,'" + convertDateToYYYYMMDD(start_date) + "') and CONVERT(datetime,'" + convertDateToYYYYMMDD(end_date) + " 23:59:59:999') and "
	sql += "l.emp_type='M1' "
	sql += "order by l.created_date desc, l.id;"
	'''

	try:				
		cursor = connection.cursor()
		cursor.execute(sql)
		leave_request_approved_object = cursor.fetchall()
		error_message = "No error"
	except db.OperationalError as e:
		error_message = "<b>Error: please send this error to IT team</b><br>" + str(e)		
	except db.Error as e:
		error_message = "<b>Error: please send this error to IT team</b><br>" + str(e)
	finally:
		cursor.close()

	record = {}	
	leave_request_approved_list = []

	if leave_request_approved_object is not None:
		print("Total=", len(leave_request_approved_object))
		
		row_count = 1
		leave_act_id_temp = 0

		for item in leave_request_approved_object:

			leave_act_id = item[0]
			attach_file = item[15] if item[15] is not None else ""
			emp_fname_th = item[1].strip() if item[1] is not None else ""
			emp_lname_th = item[2].strip() if item[2] is not None else ""
			
			record = {
				"row_count": row_count,
				"emp_id": item[0],
				'emp_fname_th': emp_fname_th,
				'emp_lname_th': emp_lname_th,
				'pos_th': item[3],
				'div_th': item[4],
				"leave_type_id": item[5],
				"leave_type_th": item[6],
				"start_date": item[7],
				"end_date": item[8],
				"created_date": item[9],
				"updated_date": item[10],
				"updated_by": item[11],
				"status": item[12],
				"lve_act": item[13],
				"lve_act_hr": item[14],
				"attach_file": attach_file,
			}

			leave_request_approved_list.append(record)
			row_count = row_count + 1

			'''
			if leave_act_id != leave_act_id_temp:
				leave_request_approved_list.append(record)
				row_count = row_count + 1
				leave_act_id_temp = leave_act_id
			'''
			
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

	today_date = getDateFormatDisplay(user_language)
	
	return render(request, 'eleavereport/view_m1_leave_report.html', {
	    'page_title': settings.PROJECT_NAME,
	    'today_date': today_date,
	    'project_version': settings.PROJECT_VERSION,
	    'db_server': settings.DATABASES['default']['HOST'],
	    'project_name': settings.PROJECT_NAME,
	    'leave_request_approved_list': list(leave_request_approved_list),
	    'start_date': start_date,
	    'end_date': end_date,	    
	    'username_display': username_display,
	})


def convertDateToYYYYMMDD(old_date):
	new_date_format = ""
	temp = old_date.split('-')
	new_date_format = str(temp[2]) + "-" + str(temp[1]) + "-" + str(temp[0])	
	return new_date_format