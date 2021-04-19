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
from leave.models import LeavePlan, LeaveHoliday, LeaveEmployee, LeaveType, EmployeeInstance
import django.db as db
from django.db import connection
from page.rules import *
from django.utils import timezone
from leave.models import LeaveEmployee
from django.http import JsonResponse
from .forms import EmployeeM1247Form
from .rules import *


def convertDateToYYYYMMDD(old_date):
	new_date_format = ""
	temp = old_date.split('-')
	new_date_format = str(temp[2]) + "-" + str(temp[1]) + "-" + str(temp[0])	
	return new_date_format


@permission_required('eleaveadmin.can_create_m1_leave_request', login_url='/accounts/login/')
def CreateM1LeaveRequest(request):
    user_language = getDefaultLanguage(request.user.username)
    translation.activate(user_language)
    
    dattime_format = "%Y-%m-%d %H:%M:%S"

    page_title = settings.PROJECT_NAME
    db_server = settings.DATABASES['default']['HOST']
    project_name = settings.PROJECT_NAME
    project_version = settings.PROJECT_VERSION
    today_date = getDateFormatDisplay(user_language)
        
    if request.method == "POST":
        form = EmployeeM1247Form(request.POST, request.FILES, user=request.user)
        render_template_name = 'eleaveadmin/create_m1_leave_request.html'

        if form.is_valid():           
            start_date = form.cleaned_data['start_date']
            start_hour = form.cleaned_data['start_hour']
            start_minute = form.cleaned_data['start_minute']

            end_date = form.cleaned_data['end_date']
            end_hour = form.cleaned_data['end_hour']            
            end_minute = form.cleaned_data['end_minute']

            d1 = str(start_date) + ' ' + str(start_hour) + ':' + str(start_minute) + ':00'
            d2 = str(end_date) + ' ' + str(end_hour) + ':' + str(end_minute) + ':00'
            start_date = datetime.strptime(d1, dattime_format)
            end_date = datetime.strptime(d2, dattime_format)

            leave_type_id = form.data['leave_type']
            leave_type = form.cleaned_data['leave_type']
            leave_reason = form.cleaned_data['leave_reason']
            username = request.user.username
            fullname = request.user.first_name + " " + request.user.last_name
            created_by = request.user.username                        

            employee = form.save(commit=False)

            employee.start_date = start_date
            employee.end_date = end_date
            employee.emp_id = request.user.username
            employee.created_by = request.user.username
            employee.leave_reason = leave_reason
            
            found_m1247_error = checkM1247BusinessRules('M1247', start_date, end_date, leave_type_id)
            if found_m1247_error[0]:
                raise forms.ValidationError(found_m1247_error[1])
            else:
                grand_total_hours = found_m1247_error[1]

            employee.lve_act = grand_total_hours // 8
            employee.lve_act_hr = grand_total_hours % 8
        
            employee.save()
            ref = employee.id 

            day_hour_display = ""
            if grand_total_hours // 8 > 0:
                day_hour_display += str(grand_total_hours // 8) + ' วัน '
            if grand_total_hours % 8 > 0:
                day_hour_display += str(grand_total_hours % 8) + ' ช.ม.'

            # EMPLOYEE SENDS LEAVE REQUEST EMAIL
            if request.user.username not in excluded_username:

                if settings.TURN_SEND_MAIL_ON:                    
                    employee = LeaveEmployee.objects.get(emp_id=request.user.username)
                    supervisor_id = employee.emp_spid
                    supervisor = User.objects.get(username=supervisor_id)
                    supervisor_email = supervisor.email
                    recipients = [supervisor_email]                
                    employee_full_name = employee.emp_fname_th + ' ' + employee.emp_lname_th
                    supervisor_obj = LeaveEmployee.objects.get(emp_id=supervisor_id)
                    supervisor_fullname = supervisor_obj.emp_fname_th + " " + supervisor_obj.emp_lname_th
                    
                    if settings.TURN_DUMMY_EMAIL_ON:
                        recipients = settings.DUMMY_EMAIL

                    if len(leave_reason) <= 0:
                        leave_reason = _('There is no reason provided.')

                    mail.send(                        
                        recipients, # To
                        settings.DEFAULT_FROM_EMAIL, # From
                        subject = 'E-Leave: ' + employee_full_name + ' - ขออนุมัติวันลา',
                        message = 'E-Leave: ' + employee_full_name + ' - ขออนุมัติวันลา',
                        html_message = 'เรียน คุณ <strong>' + supervisor_fullname + '</strong><br><br>'
                            'พนักงานแจ้งใช้สิทธิ์วันลาตามรายละเอียดด้านล่าง<br><br>'                            
                            'ชื่อพนักงาน: <strong>' + employee_full_name + '</strong><br>'
                            'ประเภทการลา: <strong>' + str(leave_type) + '</strong><br>'
                            'ลาวันที่: <strong>' + str(start_date.strftime("%d-%b-%Y %H:%M")) + '</strong> ถึงวันที่ <strong>' + str(end_date.strftime("%d-%b-%Y %H:%M")) + '</strong><br>'
                            'จำนวน: <strong>' + day_hour_display + '</strong><br>'
                            'เหตุผลการลา: <strong>' + leave_reason + '</strong><br><br>'
                            'กรุณา <a href="http://27.254.207.51:8080">ล็อคอินที่นี่</a> เพื่อดำเนินการพิจารณาต่อไป<br>'
                            '<br><br>--This email was sent from E-Leave System<br>'
                            'ref: ' + str(ref) + '<br>'
                    )

            return HttpResponseRedirect('/leave/leave-history/?submitted=True')
              
    else:
        form = EmployeeM1247Form(user=request.user)
        render_template_name = 'eleaveadmin/create_m1_leave_request.html'
        
    # Check number of waiting leave request
    waiting_for_approval_item = len(EmployeeInstance.objects.raw("select * from leave_employeeinstance as ei inner join leave_employee e on ei.emp_id = e.emp_id where ei.emp_id in (select emp_id from leave_employee where emp_spid=" + request.user.username + ") and ei.status in ('p') and year(end_date)='2021'"))     
    
    # Check leave approval right
    if checkLeaveRequestApproval(request.user.username):
        able_to_approve_leave_request = True
    else:
        able_to_approve_leave_request = False

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

    return render(request, render_template_name, {
        'form': form,
        'page_title': settings.PROJECT_NAME,
        'today_date': today_date,
        'project_version': settings.PROJECT_VERSION,
        'db_server': settings.DATABASES['default']['HOST'],
        'project_name': settings.PROJECT_NAME,
        'waiting_for_approval_item': waiting_for_approval_item,
        'able_to_approve_leave_request': able_to_approve_leave_request,
        'user_language': user_language,
        'username_display': username_display,
    })



@permission_required('eleaveadmin.can_create_m1_leave_request', login_url='/accounts/login/')
def ajax_search_employee(request):
	is_found = False
	message = "Not found"
	employee_information = ""
	search_employee_object = None
	leave_type_object = None
	leave_type_list = {}
	search_emp_id = ""
	search_emp_fname = ""
	search_emp_lname = ""
	search_emp_pos_th = ""
	search_emp_div_th = ""

	emp_id = None if request.POST.get('emp_id') == "" else request.POST.get('emp_id')
	# emp_fname = None if request.POST.get('emp_fname') == "" else request.POST.get('emp_fname')
	# emp_lname = None if request.POST.get('emp_lname') == "" else request.POST.get('emp_lname')

	if emp_id is not None:
		sql = "select emp_id,emp_fname_th,emp_lname_th,pos_th,div_th from leave_employee where emp_type='M1' and emp_id='" + str(emp_id) + "';"
	else:
		response = JsonResponse(data={
			"success": True,
			"is_found": False,
			"message": "Please enter employee ID",
			"search_emp_id": search_emp_id,
			"search_emp_fname": search_emp_fname,
			"search_emp_lname": search_emp_lname,
			"search_emp_pos_th": search_emp_pos_th,
			"search_emp_div_th": search_emp_div_th			
		})
		response.status_code = 200
		return response			

	try:				
		cursor = connection.cursor()
		cursor.execute(sql)
		search_employee_object = cursor.fetchone()
		
		if search_employee_object is not None:			
			message = "Found"
			is_found = True
			search_emp_id = search_employee_object[0]
			search_emp_fname = search_employee_object[1]
			search_emp_lname = search_employee_object[2]
			search_emp_pos_th = search_employee_object[3]			
			search_emp_div_th = search_employee_object[4]
		else:
			message = "ไม่พบข้อมูลพนักงานในระบบ"

	except db.OperationalError as e:
		is_found = False
		message = "<b>Error: please send this error to IT team</b><br>" + str(e)		
	except db.Error as e:
		is_found = False
		message = "<b>Error: please send this error to IT team</b><br>" + str(e)
	finally:
		cursor.close()


	# Generate Leave Type
	if search_employee_object is not None:
		sql = "select lp.lve_id,lt.lve_th from leave_plan lp ";
		sql += "left join leave_type lt on lp.lve_id=lt.lve_id ";
		sql += "where lp.emp_id='900662' and lp.lve_year='2021' ";
		sql += "order by lp.lve_id;"

		try:				
			cursor = connection.cursor()
			cursor.execute(sql)
			leave_type_object = cursor.fetchall()			
		except db.OperationalError as e:
			is_found = False
			message = "<b>Error: please send this error to IT team</b><br>" + str(e)		
		except db.Error as e:
			is_found = False
			message = "<b>Error: please send this error to IT team</b><br>" + str(e)
		finally:
			cursor.close()		

	response = JsonResponse(data={
	    "success": True,
	    "is_found": is_found,
	    "message": message,
		"search_emp_id": search_emp_id,
		"search_emp_fname": search_emp_fname,
		"search_emp_lname": search_emp_lname,
		"search_emp_pos_th": search_emp_pos_th,
		"search_emp_div_th": search_emp_div_th,
		"leave_type_list": list(leave_type_object),
	})
	
	response.status_code = 200
	return response	



'''
@permission_required('eleaveadmin.can_create_m1_leave_request', login_url='/accounts/login/')
def CreateM1LeaveRequest_Temp(request):
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

	leave_request_pending_object = None
	leave_request_pending_list = {}

	if user_language == "th":
		username_display = LeaveEmployee.objects.filter(emp_id=request.user.username).values_list('emp_fname_th', flat=True).get()
	else:
		username_display = LeaveEmployee.objects.filter(emp_id=request.user.username).values_list('emp_fname_en', flat=True).get()

	return render(request, 'eleaveadmin/create_m1_leave_request.html', {
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
'''

