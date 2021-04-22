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
from docxtpl import DocxTemplate
from docx.shared import Cm, Mm, Pt, Inches
from docx.enum.section import WD_ORIENT
from docx.enum.text import WD_LINE_SPACING
from docx.enum.style import WD_STYLE_TYPE
from os import path
# from docx2pdf import convert
import django.db as db
import PyPDF2 as p,os
import sys
import os
import comtypes.client


@permission_required('epayslipm1.can_access_e_payslip_m1', login_url='/accounts/login/')
def EPaySlipM1(request):
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
	sql = "select top 12 eps_prd_id,prd_year,prd_month,period from sp_slip1 "
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
	is_error = True
	message = "Error #0 - default error"
	pay_slip_object = None
	pay_slip_list = []
	record = {}

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
	
	sql = "select * from sp_slip1 where eps_emp_id='" + str(emp_id) + "' and eps_prd_id='" + str(eps_prd_id) + "' and eps_emp_type='M1' order by prd_year desc, prd_month desc, pay_seq;"
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
			print(pay_th)
			record = {
				"pay_th": pay_th,
				"pay_en": pay_en,				
			}

		# Generate PDF file
		is_error, message = generate_payslip_pdf_file_m1(emp_id, pay_slip_object)

		if is_error:
			is_error = True			
		else:
			is_error = False
			message = "ระบบส่งไฟล์ Payslip " + "<span class='text-success'><b>Period " + str(selected_period_name) + "</b></span> ไปที่ Mailbox ของท่านแล้ว กรุณาตรวจสอบ"

		# Send Email
		# TODO

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
def generate_payslip_pdf_file_m1(emp_id, pay_slip_object):
	is_error = True
	message = ""	
	base_url = MEDIA_ROOT + '/epayslipm1/template/'
	template_name = base_url + 'payslip_m1_th.docx'
	file_name = str(emp_id) + "_payslip"

	document = DocxTemplate(template_name)
	style = document.styles['Normal']
	font = style.font
	font.name = 'AngsanaUPC'
	font.size = Pt(14)

	context = {
		"emp_id": emp_id,
	    "paid_period": "1",
	}

	# Generate Word file
	try:
		document.render(context)
		document.save(MEDIA_ROOT + '/epayslipm1/download/' + file_name + "_temp.docx")    
		is_error = False
		message = "Generate file is success."		
	except Exception as e:
		is_error = True
		message = str(e);


	# Generate PDF file
	try:
		docx_file = path.abspath("media\\epayslipm1\\download\\" + file_name + "_temp.docx")
		pdf_file = path.abspath("media\\epayslipm1\\download\\" + file_name + "_temp.pdf")    
		
		# convert(docx_file, pdf_file)
		
		wdFormatPDF = 17
		word = comtypes.client.CreateObject('Word.Application')
		doc = word.Documents.Open(docx_file)
		doc.SaveAs(pdf_file, FileFormat=wdFormatPDF)
		doc.Close()
		word.Quit()		
		
		output = p.PdfFileWriter()
		f = open(pdf_file, "rb")
		pdf = p.PdfFileReader(f)

		for i in range(0, pdf.getNumPages()):
			output.addPage(pdf.getPage(i))

		outputstream = open(path.abspath("media\\epayslipm1\\download\\" + file_name + ".pdf"), "wb")

		output.encrypt("mypass", use_128bit=True)
		output.write(outputstream)
		outputstream.close()

		f.close()
		os.remove(pdf_file)
		os.remove(docx_file)

	except Exception as e:
		is_error = True
		message = str(e)

	return is_error, message


# Send Email to Employee
@permission_required('dailyattendreport.can_access_psn_slip_d1_report', login_url='/accounts/login/')
def send_payslip():
	print("todo")

