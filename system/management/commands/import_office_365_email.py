from django.core.management.base import BaseCommand
from django.conf import settings
from datetime import datetime
from django.db import connection
from system.models import OutlookEmailActiveUserList
from os.path import getmtime
from os.path import getsize
from os import path
from decimal import Decimal
import csv


def import_office_365_email():
	total = 0
	count = 0	
	office_365_email_list = []
	record = {}
	csv_file_size = 0

	csv_file = path.abspath("media\\system\\export_office_365_email.csv")
	if path.exists(csv_file):
		csv_file_is_existed = True	
		csv_file_created_date = datetime.fromtimestamp(getmtime(csv_file)).strftime('%Y-%m-%d %H:%M:%S')
		csv_file_size = getsize(csv_file)		
	else:
		csv_file_is_existed = False
		csv_file_created_date = None

	if csv_file_is_existed:
		
		if csv_file_size > 0 :
			try:
				record = {}
				with open(csv_file, newline='', encoding='utf-8') as csvfile:
					reader = csv.reader(csvfile)
					next(reader)
					next(reader)
					data = list(reader)

				OutlookEmailActiveUserList.objects.all().delete()

				# Reset auto increment key
				is_reset_auto_increment_error = True
				sql = "DBCC CHECKIDENT (system_outlook_email_active_user_list, RESEED, 0)"
				try:                
					cursor = connection.cursor()
					cursor.execute(sql)
					is_reset_auto_increment_error = False
				except db.OperationalError as e:
					message = "<b>Error: please send this error to IT team</b><br>" + str(e)
				except db.Error as e:
					message = "<b>Error: please send this error to IT team</b><br>" + str(e)
				finally:
					cursor.close()

				if is_reset_auto_increment_error:
					message = "Cannot reset auto increment number."
					is_error = True
				else:									
					for item in data:
						if item[2] != "" and item[2] is not None:
							emp_id = Decimal(item[2])
						else:
							emp_id = None

						first_name = item[0]
						last_name = item[1]
						email = item[4]
						outlook_obj = OutlookEmailActiveUserList(first_name=first_name, last_name=last_name, email=email, emp_id=emp_id, created_date=csv_file_created_date)
						outlook_obj.save()

					is_error = False
					message = "Import success"

			except Exception as e:
				is_error = True
				message = str(e)
		else:
			is_error = True
			message = "File is not ready. Please try again."
	else:	
		is_error = True
		message = "Export file is not existed. Please run Windows Schedule."

	print(message)


class Command(BaseCommand):
	def handle(self, **options):
		import_office_365_email()

