from datetime import datetime
from datetime import timedelta
from django.contrib.auth.models import Group
from django.utils.translation import ugettext_lazy as _


dayDelta = timedelta(days=1)


def checkStandardBusinessRules(start_date, end_date):
	if (start_date > end_date):
		return True, _("ลาวันที่ > ถึงวันที่")
	elif (start_date == end_date):
	    return True, _("เลือกช่วงเวลาไม่ถูกต้อง")
	else:
		total_minute = (end_date - start_date).total_seconds() / 60.0
		if (total_minute % 60) > 0:
			return True, _("ช่วงวันลามีเศษครึ่งชั่วโมง")

	return False, ""


def checkM1247BusinessRules(employee_type, d1, d2):
	total_hour = 0
	result = total_hour = ((d2 - d1).total_seconds() / 60.0) / 60
	if(result > 0):
		if result > 8:
			#return True, _("สามารถเลือกได้ไม่เกิน 4 ช.ม.ต่อหนึ่งใบลา และไม่รวมเวลาพักเบรค")			
			total_hour = result
		else:
			total_hour = result

	print("Result: " + str(total_hour))

	if total_hour > 23:                    
		day = total_hour // 24                    
		if total_hour % 24 >= 9:
			if (total_hour % 24) -1 == 8:
				hour = 0
				day += 1
			else:
				hour = (total_hour % 24)
		else:
			hour = total_hour % 24
	else:             
		if total_hour <= 9:
			if total_hour == 1:
				total_hour = total_hour
				day = total_hour // 8
				hour = total_hour % 8				
			else:
				total_hour = total_hour - 1
				day = total_hour // 8
				hour = total_hour % 8
		else:
			day = 1
			hour = 0	

	total_hour = (day * 8) + hour
	print("Debug: " + str(total_hour))
	return False, total_hour



def checkM1817BusinessRules(employee_type, d1, d2):
	start_working_hour = 8
	stop_working_hour = 17

	excluded_day = {5, 6}
	excluded_hour = {0, 1, 2, 3, 4, 5, 6, 7, 12, 18, 19, 20, 21, 22, 23}

	total_hour = 0
	total_minute = 0
	grand_total_hour = 0
	
	while (d2 >= d1):
		if d1.weekday() not in excluded_day:
			if (d1.day == d2.day):
				if (d1.hour <= start_working_hour):
					if(d2.hour <= stop_working_hour):
						for i in range(start_working_hour, d2.hour):
							if i not in excluded_hour:
								total_hour += 1
								total_minute += 60
					else:
						for i in range(start_working_hour, stop_working_hour):
							if i not in excluded_hour:
								total_hour += 1
								total_minute += 60
				else:
					for i in range(d1.hour, d2.hour):
						if i not in excluded_hour:
							total_hour += 1
							total_minute += 60
			else:
				for i in range(d1.hour, stop_working_hour):
					if i not in excluded_hour:
						total_hour += 1
						total_minute += 60

		grand_total_hour += total_hour
		total_hour = 0
		d1 += dayDelta;

	return grand_total_hour
	
def checkM1LeaveRequestHour(employee_type, d1, d2):
	start_working_hour = 8
	stop_working_hour = 17
	excluded_day = {5, 6}
	excluded_hour = {0, 1, 2, 3, 4, 5, 6, 7, 12, 18, 19, 20, 21, 22, 23}

	total_hour = 0
	grand_total_hour = 0

	while (d2 >= d1):
		if d1.weekday() not in excluded_day:
			if (d1.day == d2.day):
				if (d1.hour <= start_working_hour):
					if(d2.hour <= stop_working_hour):
						for i in range(start_working_hour, d2.hour):
							if i not in excluded_hour:
								total_hour += 1
					else:
						for i in range(start_working_hour, stop_working_hour):
							if i not in excluded_hour:
								total_hour += 1
				else:
					for i in range(d1.hour, d2.hour):
						if i not in excluded_hour:
							total_hour += 1
			else:
				for i in range(d1.hour, stop_working_hour):
					if i not in excluded_hour:
						total_hour += 1

		grand_total_hour += total_hour
		total_hour = 0
		d1 += dayDelta;

	return grand_total_hour


def checkM1LeaveRequestOverMonth(employee_type, d1, d2):
	if(d1.month != d2.month):
		return True
	else:
		return False

def is_in_multiple_groups(user):
    m1817manager = "E-Leave-M1-8-17-Manager"
    m1817staff = "E-Leave-M1-8-17-Staff"    
    m1024manager = "E-Leave-M1-0-24-Manager"
    m1024staff = "E-Leave-M1-0-24-Staff"
    users_in_group = Group.objects.get(name=m1817staff).user_set.all()
    return user.groups.filter(name__in=[m1817manager, m1817staff, m1024manager, m1024staff]).exists()

# check employee leave type
def getEmployeeWorkingPeriod(user):
    m1817manager = "E-Leave-M1-8-17-Manager"
    employeeWorkingPeriod = m1817manager

    return employeeWorkingPeriod
