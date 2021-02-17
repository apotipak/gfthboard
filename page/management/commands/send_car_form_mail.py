from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from django.db import connection


class Command(BaseCommand):
	def handle(self, **options):
		
		PRIVATE_DIR = getattr(settings, "PRIVATE_DIR", None)
		TURN_DUMMY_EMAIL_ON = getattr(settings, "TURN_DUMMY_EMAIL_ON", None)
		DUMMY_EMAIL = getattr(settings, "DUMMY_EMAIL", None)

		email_list = None
		sql = "select * from post_office_email_win where status=2;"        
		try:
			with connection.cursor() as cursor:     
				cursor.execute(sql)
				email_list = cursor.fetchall()
		except db.OperationalError as e:
			is_found = False
			message = "<b>Please send this error to IT team or try again.</b><br>" + str(e)
		except db.Error as e:
			is_found = False
			message = "<b>Please send this error to IT team or try again.</b><br>" + str(e)
		finally:
			cursor.close()

		if email_list is not None:
			
			for item in email_list:
				send_id = item[0]
				send_from = item[1]
				send_to = item[2]
				subject = item[5]
				message = item[6]
				html_message = item[7]
				status = item[8]
				created_date = item[10]

				if (send_to is not None or send_to != ""):
					if TURN_DUMMY_EMAIL_ON:
						send_mail(subject, html_message, 'support.gfth@guardforce.co.th', [DUMMY_EMAIL], fail_silently=False)
					else:					
						send_mail(subject, html_message, 'support.gfth@guardforce.co.th', [send_to], fail_silently=False)
				else:
					error_message = "Item number" + str(send_id) + " cannot be sent."
								
		print("Send mail completed")

