from django.core.management.base import BaseCommand
# from django.core.mail import send_mail
from django.conf import settings
from django.db import connection
from django.core import mail
from django.core.mail.backends.smtp import EmailBackend
from django.core.mail import EmailMultiAlternatives


def send_car_form_mail(subject, send_to, html_message, send_id):

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

        msg = mail.EmailMessage(
            subject=subject,
            body=html_message,
            from_email=host_user,
            to=[send_to],
            connection=con,
        )
        
        msg.content_subtype = 'html'
        mail_obj.send_messages([msg])
        print('Message has been sent.')

        mail_obj.close()
        print('SMTP server closed')

        # Change status from 2 to 0
        sql = "update post_office_email_win set status=0 where id=" + str(send_id)
        try:
        	with connection.cursor() as cursor:
        		cursor.execute(sql)
        except db.OperationalError as e:			
        	message = "<b>Please send this error to IT team or try again.</b><br>" + str(e)
        except db.Error as e:			
        	message = "<b>Please send this error to IT team or try again.</b><br>" + str(e)
        finally:
        	cursor.close()
        return True
    except Exception as _error:
        print('Error in sending mail >> {}'.format(_error))
        return False


class Command(BaseCommand):
	

	def handle(self, **options):
				
		TURN_CAR_FORM_SEND_MAIL_ON = getattr(settings, "TURN_CAR_FORM_SEND_MAIL_ON", None)	
		TURN_CAR_FORM_DUMMY_EMAIL_ON = getattr(settings, "TURN_CAR_FORM_DUMMY_EMAIL_ON", None)
		CAR_FORM_DUMMY_EMAIL = getattr(settings, "CAR_FORM_DUMMY_EMAIL", None)

		print("debug1")
		
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


		print("debug2")

		if email_list is not None:
			
			if TURN_CAR_FORM_SEND_MAIL_ON:
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
						if TURN_CAR_FORM_DUMMY_EMAIL_ON:
							print("sent to dummy email")
							# send_mail(subject, html_message, 'support.gfth@guardforce.co.th', [CAR_FORM_DUMMY_EMAIL], fail_silently=False)
							send_car_form_mail(subject, CAR_FORM_DUMMY_EMAIL, html_message, send_id)
						else:
							print("sent to owner email")
							# send_mail(subject, html_message, 'support.gfth@guardforce.co.th', [send_to], fail_silently=False)
					else:
						error_message = "Item number" + str(send_id) + " cannot be sent."						
				print("Send mail completed")
			else:
				print("CAR Form send mail is turn off.")		
