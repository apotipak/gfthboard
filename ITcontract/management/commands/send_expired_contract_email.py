from django.core.management.base import BaseCommand
from django.conf import settings
from datetime import datetime
from django.db import connection
from django.core import mail
from django.core.mail.backends.smtp import EmailBackend
from django.core.mail import EmailMultiAlternatives
from ITcontract.models import ITcontractDB, ITContractEmailAlert


def send_expired_contract_email(subject, send_to_email, send_to_group_email, html_message):
	# print(subject, send_to_email, send_to_group_email, html_message)

	if send_to_email == "" and send_to_group_email == "":
		print("No email provided")
		return False

	try:
		con = mail.get_connection()
		con.open()

		host = getattr(settings, "EMAIL_HOST", None)
		host_user = getattr(settings, "EMAIL_HOST_USER", None)
		host_pass = getattr(settings, "EMAIL_HOST_PASSWORD", None)
		host_port = getattr(settings, "EMAIL_PORT", None)

		mail_obj = EmailBackend(
		    host=host,
		    port=host_port,
		    password=host_pass,
		    username=host_user,
		    use_tls=True,
		    timeout=10
		)

		if send_to_email != "":
			print("send_to_email only")
			msg = mail.EmailMessage(
			    subject=subject,
			    body=html_message,
			    from_email=host_user,
			    to=[send_to_email],
			    connection=con,
			)


		if send_to_email == "" and send_to_group_email != "":
			print("send_to_group_email only")
			msg = mail.EmailMessage(
			    subject=subject,
			    body=html_message,
			    from_email=host_user,
			    to=[send_to_group_email],
			    connection=con,
			)


		if send_to_email != "" and send_to_group_email != "":
			print("sent to both email and group email")
			msg = mail.EmailMessage(
			    subject=subject,
			    body=html_message,
			    from_email=host_user,
			    to=[send_to_email, send_to_group_email],
			    connection=con,
			)

		msg.content_subtype = 'html'
		mail_obj.send_messages([msg])    
		mail_obj.close()

		print('Message has been sent.')

		return True
	except Exception as _error:
		print('Error in sending mail >> {}'.format(_error))
		return False


class Command(BaseCommand):
	def handle(self, **options):
		reach_minimum_day = 0
		itcontract_email_alert_object = None
		itcontractdb_object = None
		expired_contract_list = []
		record = {}

		send_to_email = ""
		send_to_group_email = ""


		itcontract_email_alert_object = ITContractEmailAlert.objects.filter(alert_id=1).filter(app_name='ITcontract').get()
		if itcontract_email_alert_object is not None:
			alert_active = itcontract_email_alert_object.alert_active
			reach_minimum_day = itcontract_email_alert_object.reach_minimum_day
			send_to_email = itcontract_email_alert_object.send_to_email
			send_to_group_email = itcontract_email_alert_object.send_to_group_email

		if alert_active=="1":

			itcontractdb_object = ITcontractDB.objects.exclude(upd_flag='D').exclude(turn_off_notification=True).all().values_list('id','dept','vendor','description','person','tel','e_mail','start_date','end_date','price','remark','upd_by')
			# itcontractdb_object = ITcontractDB.objects.exclude(upd_flag='D').all().values_list('id','dept','vendor','description','person','tel','e_mail','start_date','end_date','price','remark','upd_by')

			if itcontractdb_object is not None:
				str_today_date = datetime.now().strftime("%Y-%m-%d")
				today_date = datetime.strptime(str_today_date, '%Y-%m-%d').date()

				for item in itcontractdb_object:
					it_contract_id = item[0]
					department = item[1]
					vendor = item[2]
					description = item[3]
					contact = item[4]
					phone = item[5]
					email = item[6]
					start_date = item[7]
					end_date = item[8]
					price = item[9]
					remark = item[10]
					upd_by = item[11]
					remaining_day = end_date.date() - today_date

					if (end_date.date() >= today_date):
						is_contract_expired = False
					else:
						is_contract_expired = True

					record = {
				    	"id": it_contract_id,
				    	"dept": department,
				    	"vendor": vendor,
				    	"description": description,
				    	"contact": contact,
				    	"phone": phone,
				    	"email": email,
				    	"start_date": start_date,
				    	"end_date": end_date,
				    	"price": price,
				    	"remark": remark,
				    	"upd_by": upd_by,
				    	"is_contract_expired": is_contract_expired,
				    	"remaining_day": remaining_day.days,
					}				

					if is_contract_expired:
						expired_contract_list.append(record)
						print("ID : ", it_contract_id)
					else:
						if remaining_day.days <= reach_minimum_day:						
							expired_contract_list.append(record)

			else:
				print("Not found expired contract")


			if len(expired_contract_list) > 0:
				
				subject = "GFTH Board - แจ้งเตือนสัญญาหมดอายุ"
				html_message = ""
				html_message += "เรียน แผนกไอที<br><br>"

				for item in expired_contract_list:
					it_contract_id = item['id']
					vendor = item['vendor']
					end_date = item['end_date'].strftime("%d/%m/%Y")
					is_contract_expired = item['is_contract_expired']
					remaining_day = item['remaining_day']

					if is_contract_expired:
						html_message += "สัญญาเลขที่ " + str(it_contract_id) + " ของบริษัท <b><a href='http://27.254.207.51:8080/ITcontract/'>" + str(vendor) + "</a></b> <span style='color: red;'>หมดอายุแล้ว</span><br>"
					else:
						html_message += "สัญญาเลขที่ " + str(it_contract_id) + " ของบริษัท <b><a href='http://27.254.207.51:8080/ITcontract/'>" + str(vendor) + "</a></b> จะสิ้นสุดในวันที่ " + str(end_date) + " - <b><span style='color: green;'>เหลือ " + str(remaining_day) + " วัน</span></b><br>"

				html_message += "<br>"
				html_message += "-- This email was automatically sent from system. Please do not reply. --"

				send_expired_contract_email(subject, send_to_email, send_to_group_email, html_message)
		else:
			print("Send email is turn off")

