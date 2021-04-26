from django.shortcuts import render
from django.utils import timezone
from datetime import datetime
from django.conf import settings
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required
from django.utils import translation
from django.utils.translation import ugettext as _
from django.db.models import Sum
from page.rules import *
from django.http import JsonResponse
from django.db import connection
from leave.models import LeaveEmployee
from gfthboard.settings import MEDIA_ROOT
from os import path
import django.db as db
import sys
import os
import string
import random
from django.core import mail
from django.core.mail.backends.smtp import EmailBackend
from django.core.mail import EmailMultiAlternatives


@permission_required('epayslipm1.can_access_e_payslip_m1', login_url='/accounts/login/')
def EPaySlipM1(request):
	dummy_data = False

	user_language = getDefaultLanguage(request.user.username)
	translation.activate(user_language)
	render_template_name = 'epayslipm1/request_payslip.html'

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
	# end

	# Get available period for M1
	
	if dummy_data:
		sql = "select top 12 eps_prd_id,prd_year,prd_month,period from sp_slip1 "
	else:
		sql = "select top 12 eps_prd_id,prd_year,prd_month,period from sp_slip "

	sql += "where eps_emp_type='M1' "
	sql += "group by eps_prd_id,prd_year,prd_month,period "
	sql += "order by eps_prd_id desc;"
	print("SQL : ", sql)

	try:
		cursor = connection.cursor()
		cursor.execute(sql)
		available_period_obj = cursor.fetchall()
	except db.OperationalError as e:
		is_error = True
		error_message = "<b>Error: please send this error to IT team</b><br>" + str(e)
	except db.Error as e:
		is_error = True
		error_message = "<b>Error: please send this error to IT team</b><br>" + str(e)
	finally:
		cursor.close()

	if available_period_obj is not None:
		for item in available_period_obj:
			eps_prd_id = item[0]
			prd_year = item[1]
			prd_month = item[2]
			period = item[3]
			prd_month_name_en = datetime.strptime(str(item[2]), "%m").strftime("%B")
			prd_month_name_th = convert_thai_month_name(prd_month)
			record = {
				"eps_prd_id": eps_prd_id,
				"prd_year": prd_year,
				"prd_month": prd_month,
				"period": period,
				"prd_month_name_en": prd_month_name_en,
				"prd_month_name_th": prd_month_name_th,
			}
			available_period_list.append(record)			

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


@permission_required('epayslipm1.can_access_e_payslip_m1', login_url='/accounts/login/')
def AjaxSendPayslipM1(request):	
	dummy_data = False

	is_error = True
	message = "Error #0 - default error"
	pay_slip_object = None
	pay_slip_list = []
	record = {}

	# Check email
	primary_email = request.user.email
	if (primary_email is None ) or (primary_email == ""):
		response = JsonResponse(data={"is_error": True, "message": "Your email has not been setup properly. Please check."})
		response.status_code = 200
		return response

	user_language = getDefaultLanguage(request.user.username)
	translation.activate(user_language)

	render_template_name = 'epayslipm1/request_payslip.html'
	page_title = settings.PROJECT_NAME
	db_server = settings.DATABASES['default']['HOST']
	project_name = settings.PROJECT_NAME
	project_version = settings.PROJECT_VERSION
	today_date = getDateFormatDisplay(user_language)
	
	emp_id = request.user.username
	eps_prd_id = request.POST.get("selected_period")
	selected_period_name = request.POST.get("selected_period_name")
	
	if dummy_data:
		sql = "select * from sp_slip1 where eps_emp_id='" + str(emp_id) + "' and eps_prd_id='" + str(eps_prd_id) + "' and eps_emp_type='M1' order by prd_year desc, prd_month desc, pay_seq;"
	else:
		sql = "select * from sp_slip where eps_emp_id='" + str(emp_id) + "' and eps_prd_id='" + str(eps_prd_id) + "' and eps_emp_type='M1' order by prd_year desc, prd_month desc, pay_seq;"

	print("SQLLL : ", sql)

	try:
		cursor = connection.cursor()
		cursor.execute(sql)
		pay_slip_object = cursor.fetchall()
	except db.OperationalError as e:
		is_error = True
		message = "<b>Error: please send this error to IT team</b><br>" + str(e)
	except db.Error as e:
		is_error = True
		message = "<b>Error: please send this error to IT team</b><br>" + str(e)
	finally:
		cursor.close()

	if pay_slip_object is not None:
		for item in pay_slip_object:
			pay_th = item[0]
			pay_en = item[1]
			record = {
				"pay_th": pay_th,
				"pay_en": pay_en,	
			}

		# Generate PDF file
		is_error, message = generate_payslip_pdf_file_m1(emp_id, primary_email, pay_slip_object, eps_prd_id, selected_period_name)

		if is_error:
			is_error = True			
		else:
			is_error = False
			message = "ระบบส่ง " + "<span class='text-success'><b>Payslip " + str(selected_period_name) + "</b></span> ไว้ในเมล์บ็อกซ์ของคุณแล้ว<br><br>"
	else:
		is_error = True
		message = "ระบบไม่สามารถส่งไฟล์ Payslip ให้ท่านได้ กรุณาติดต่อฝ่ายบุคคลอีกครั้ง"

	response = JsonResponse(data={        
	    "is_error": is_error,
	    "message": message,
	})

	response.status_code = 200
	return response


def convert_thai_month_name(month_number):
	thai_month_name = "Unknown"

	if month_number == 1:
		thai_month_name = "มกราคม"
	elif month_number == 2:
		thai_month_name = "กุมภาพันธ์"
	elif month_number == 3:
		thai_month_name = "มีนาคม"
	elif month_number == 4:
		thai_month_name = "เมษายน"
	elif month_number == 5:
		thai_month_name = "พฤษภาคม"
	elif month_number == 6:
		thai_month_name = "มิถุนายน"
	elif month_number == 7:
		thai_month_name = "กรกฏาคม"
	elif month_number == 8:
		thai_month_name = "สิงหาคม"
	elif month_number == 9:
		thai_month_name = "กันยายน"
	elif month_number == 10:
		thai_month_name = "ตุลาคม"
	elif month_number == 11:
		thai_month_name = "พฤศจิกายน"
	elif month_number == 12:
		thai_month_name = "ธันวาคม"
	else:
		thai_month_name

	return thai_month_name


# Generate PDF File
def generate_payslip_pdf_file_m1(emp_id, primary_email, pay_slip_object, eps_prd_id, selected_period_name):
	dummy_data = False

	is_error = True
	message = ""	
	base_url = MEDIA_ROOT + '/epayslipm1/template/'
	template_name = base_url + 'payslip_m1_th.docx'	
	period_name = selected_period_name.replace("/", "_")
	file_name = str(emp_id) + "_payslip_" + period_name

	income_list = []
	deduct_list = []
	title_th = ""
	emp_fname_th = ""
	emp_lname_th = ""
	emp_full_name = ""
	dept_en = ""
	emp_dept = ""
	emp_acc_no = ""
	prd_year = ""
	prd_month = ""
	prd_date_paid = ""
	pay_tax = 0
	eps_prd_in = 0
	eps_prd_net = 0
	eps_ysm_in = 0
	eps_ysm_prv = 0
	eps_prd_de = 0
	eps_prd_tax = 0
	eps_ysm_tax = 0
	eps_ysm_soc = 0

	count = 0
	if pay_slip_object is not None:
		for item in pay_slip_object:
			if count == 0:
				title_th = item[24]
				emp_fname_th = item[20]
				emp_lname_th = item[21]
				emp_full_name = emp_fname_th.strip() + " " + emp_lname_th.strip()
				emp_dept = item[28]
				dept_en = item[23]
				emp_acc_no = str(item[25]).zfill(3) + "-" + str(item[26])
				prd_year = item[10]
				prd_month = item[11]
				prd_date_paid = item[16]
				
				# เงินได้ก่อนหักภาษี
				eps_prd_in = 0 if item[63] is None else str('{:,}'.format(item[63]))

				# เงินได้สุทธิ
				eps_prd_net = 0 if item[65] is None else '{:,}'.format(item[65])

				# เงินได้สะสม
				eps_ysm_in = 0 if item[50] is None else '{:,}'.format(item[50])

				# เงินสะสม
				eps_ysm_prv = 0 if item[55] is None else '{:,}'.format(item[55])

				# เงินหักรวม
				eps_prd_de = 0 if item[64] is None else '{:,}'.format(item[64])

				# ภาษี
				eps_prd_tax = 0 if item[66] is None else '{:,}'.format(item[66])

				# ภาษีสะสม
				eps_ysm_tax = 0 if item[57] is None else '{:,}'.format(item[57])

				# ประกันสังคม
				eps_ysm_soc = 0 if item[56] is None else '{:,}'.format(item[56])
			
			pay_seq = item[2]
			
			if pay_seq != 0:
				pay_inde = item[4]
				pay_rpt = item[3]
				pay_th = item[0]

				if not dummy_data:
					eps_amt = 0 if item[43] is None else '{:,}'.format(item[43])
				else:
					eps_amt = 1

				if item[6] == 1:
					pay_tax = "Before/ก่อน"
				elif item[6] == 0:
					pay_tax = "After/หลัง"
				else:
					pay_tax = "N/A"

				record = { "pay_rpt":pay_rpt, "pay_th":pay_th, "eps_amt":eps_amt, "pay_tax": pay_tax }

				if pay_inde == "I":					
					income_list.append(record)
					record = {}
				elif pay_inde == "D":					
					deduct_list.append(record)
					record = {}
			count = count + 1


	if dummy_data:
		context = {
			"emp_id": "xxxxxx",
			"title_th": "คุณ",
			"emp_fname_th": "ทดสอบ",
			"emp_lname_th": "ระบบ",
			"emp_full_name": "ทดสอบ ระบบใหม่",
			"dept_en": "Test Department",
			"emp_dept": "xxxx",
			"emp_acc_no": "xxx-xxxxxxxxxx",
		    "paid_period": 0,
		    "prd_year": prd_year,
		    "prd_month": prd_month,
		    "prd_date_paid": prd_date_paid.strftime("%d/%m/%Y"),
		    "pay_slip_object": pay_slip_object,
		    "income_list": list(income_list),
		    "deduct_list": list(deduct_list),
			"eps_prd_in": 1.00,
			"eps_prd_net": 1.00,
			"eps_ysm_in": 1.00,
			"eps_ysm_prv": 1.00,
			"eps_prd_de": 1.00,
			"eps_prd_tax": 1.00,
			"eps_ysm_tax": 1.00,
			"eps_ysm_soc": 1.00,
		}		
	else:
		context = {
			"emp_id": emp_id,
			"title_th": title_th,
			"emp_fname_th": emp_fname_th,
			"emp_lname_th": emp_lname_th,
			"emp_full_name": emp_full_name,
			"dept_en": dept_en,
			"emp_dept": emp_dept,
			"emp_acc_no": emp_acc_no,
		    "paid_period": 0,
		    "prd_year": prd_year,
		    "prd_month": prd_month,
		    "prd_date_paid": prd_date_paid.strftime("%d/%m/%Y"),
		    "pay_slip_object": pay_slip_object,
		    "income_list": list(income_list),
		    "deduct_list": list(deduct_list),
			"eps_prd_in": eps_prd_in,
			"eps_prd_net": eps_prd_net,
			"eps_ysm_in": eps_ysm_in,
			"eps_ysm_prv": eps_ysm_prv,
			"eps_prd_de": eps_prd_de,
			"eps_prd_tax": eps_prd_tax,
			"eps_ysm_tax": eps_ysm_tax,
			"eps_ysm_soc": eps_ysm_soc,
		}


	from docxtpl import DocxTemplate
	from docx.shared import Cm, Mm, Pt, Inches
	from docx.enum.section import WD_ORIENT
	from docx.enum.text import WD_LINE_SPACING
	from docx.enum.style import WD_STYLE_TYPE
		
	document = DocxTemplate(template_name)

	try:
		style = document.styles['Normal']
		font = style.font
		font.name = 'AngsanaUPC'
		font.size = Pt(14)
	except Exception as e:
		is_error = True
		message = str(e)


	# Generate Word file
	try:
		document.render(context)
		document.save(MEDIA_ROOT + '/epayslipm1/download/' + file_name + '_temp.docx')
		is_error = False
		message = "Generate file is success."		
	except Exception as e:
		is_error = True
		message = str(e)	


	from subprocess import  Popen
	docx_file = path.abspath("media\\epayslipm1\\download\\" + file_name + "_temp.docx")
	out_folder = path.abspath("media\\epayslipm1\\download\\")
		
	try:
		LIBRE_OFFICE = r"C:\Program Files\LibreOffice\program\soffice.exe"
		p = Popen([LIBRE_OFFICE, '--headless', '--convert-to', 'pdf', '--outdir', out_folder, docx_file])
		print([LIBRE_OFFICE, '--convert-to', 'pdf', docx_file])
		p.communicate()
	except Exception as e:
		is_error = True
		message = str(e)

	import PyPDF2 as p,os
	pdf_file = path.abspath("media\\epayslipm1\\download\\" + file_name + "_temp.pdf")
	try:		
		output = p.PdfFileWriter()
		f = open(pdf_file, "rb")
		pdf = p.PdfFileReader(f)

		for i in range(0, pdf.getNumPages()):
			output.addPage(pdf.getPage(i))

		outputstream = open(path.abspath("media\\epayslipm1\\download\\" + file_name + ".pdf"), "wb")


		count = 0
		bank_no = ""
		citizen_id = ""
		for item in pay_slip_object:
			if count == 0:
				bank_no = item[26]
				citizen_id = item[33]
			count = count + 1

		if citizen_id != "":
			# random_password = random_password_generator()
			random_password = citizen_id
		else:
			is_error = True
			message = "Your profile is not completed. Please contact HR department."

		output.encrypt(random_password, use_128bit=True)
		output.write(outputstream)
		outputstream.close()

		f.close()
		os.remove(pdf_file)
		os.remove(docx_file)

		# Send Email
		if citizen_id != "":
			send_email_success = email_payslip(emp_full_name, primary_email, file_name, prd_year, prd_month, citizen_id)
		else:
			is_error = True
			message = "Your profile is not completed. Please contact HR department."
		
	except Exception as e:
		is_error = True
		message = str(e)
		
	return is_error, message

	
# Send Email to Employee
def email_payslip(emp_full_name, send_to_email, file_name, prd_year, prd_month, random_password):
		
	if send_to_email == "" or file_name == "":
		is_send_email_success = False	
		return is_send_email_success

	try:
		con = mail.get_connection()
		con.open()

		host = getattr(settings, "EMAIL_HOST", None)
		host_user = getattr(settings, "EMAIL_HOST_USER", None)
		host_pass = getattr(settings, "EMAIL_HOST_PASSWORD", None)
		host_port = getattr(settings, "EMAIL_PORT", None)

		mail_obj = EmailBackend(
		    host = host,
		    port = host_port,
		    password = host_pass,
		    username = host_user,
		    use_tls = True,
		    timeout = 10
		)

		html_message = "เรียน คุณ" + str(emp_full_name) + "<br><br>"
		html_message += "ไฟล์นี้สามารถเปิดอ่านได้โดยใช้รหัสบัตรประชาชนของท่าน<br><br>"
		html_message += "<b>เพื่อรักษาความเป็นส่วนตัวของข้อมูล <span style='color:red;'>ห้ามส่งต่อหรือตอบกลับและควรลบอีเมล์นี้</span> หากใช้งานเสร็จแล้ว</b><br><br>"
		html_message += "<hr>"
		html_message += "<b>IT Tips: 2 ขั้นตอนป้องกันข้อมูลส่วนตัว</b><br>"
		html_message += "1. ตั้งรหัสให้เดายาก<br>"
		html_message += "2. เปลี่ยนรหัสให้บ่อยขึ้น<br>"
		html_message += "<hr>"
		html_message += "<br><i>This email was automatically sent from system. Please do not reply.</i>"

		if send_to_email != "":
			msg = mail.EmailMessage(
			    subject = "HRMS - เอกสารสำคัญ (Payslip " + str(prd_year) + "/" + str(prd_month) + ")",
			    body = html_message,
			    from_email = host_user,
			    to = [send_to_email],			    
			    connection = con,
			)

		msg.content_subtype = 'html'
		msg.attach_file(path.abspath("media\\epayslipm1\\download\\" + str(file_name) + ".pdf"))
		mail_obj.send_messages([msg])
		mail_obj.close()
		
		is_send_email_success = True
		return True

	except Exception as _error:
		print('Error in sending mail >> {}'.format(_error))
		is_send_email_success = False
		return False			


def random_password_generator(size=8, chars=string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for _ in range(size))
