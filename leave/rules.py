from datetime import datetime
from datetime import timedelta
from django.contrib.auth.models import Group
from django.utils.translation import ugettext_lazy as _
from leave.models import LeaveEmployee


dayDelta = timedelta(days=1)

def checkM1817TotalHours(employee_type, d1, d2, leave_type_id):
	d1_temp = d1
	d2_temp = d2
	start_date = d1
	end_date = d2

	start_working_hour = 8
	stop_working_hour = 17
	
	leave_type_include_weekend_list = {'6','7','10','11','13','15'}
	if leave_type_id not in leave_type_include_weekend_list:
		excluded_day = {5, 6}		
	else:
		excluded_day = {}

	excluded_hour = {0, 1, 2, 3, 4, 5, 6, 7, 12, 18, 19, 20, 21, 22, 23}

	total_hour = 0
	total_minute = 0
	grand_total_hour = 0
	count = 0
	
	while (end_date >= start_date):
		if start_date.weekday() not in excluded_day:
			if (start_date.day == end_date.day):
				if (start_date.hour <= start_working_hour):
					if(end_date.hour <= stop_working_hour):
						for i in range(start_working_hour, end_date.hour):
							if i not in excluded_hour:
								total_hour += 1
								total_minute += 60
					else:
						for i in range(start_working_hour, stop_working_hour):
							if i not in excluded_hour:
								total_hour += 1
								total_minute += 60
				else:
					for i in range(start_date.hour, end_date.hour):
						if i not in excluded_hour:
							total_hour += 1
							total_minute += 60
			else:
				for i in range(start_date.hour, stop_working_hour):
					if i not in excluded_hour:
						total_hour += 1
						total_minute += 60

		grand_total_hour += total_hour
		total_hour = 0
		start_date += dayDelta

	count = checkM1247TotalHours('M1247', d1_temp, d2_temp, leave_type_id)	
	if not count.is_integer():
		return True, _("ช่วงวันลามีเศษครึ่งชั่วโมง")

	return False, grand_total_hour


def checkM1247TotalHours(employee_type, start_date, end_date, leave_type_id):
	total_day = 0
	total_hour = 0
	result = 0
	day = 0
	hour = 0

	leave_type_include_weekend_list = {'6', '7', '10', '11', '13', '15'}
	if leave_type_id not in leave_type_include_weekend_list:
		excluded_day = {5, 6}
	else:
		excluded_day = {}

	while end_date >= start_date:
		next_date = start_date + dayDelta

		if next_date < end_date:
			if start_date.weekday() not in excluded_day:
				result = ((next_date - start_date).total_seconds() / 60.0) / 60
				day = result // 24
				hour = round(result % 24,1)
		else:
			if start_date.weekday() not in excluded_day:
				result = ((end_date - start_date).total_seconds() / 60.0) / 60
				day = result // 24
				hour = round(result % 24,1)

		total_day = total_day + day
		total_hour = total_hour + hour
		day = 0
		hour = 0
		start_date += dayDelta

	if total_hour == 24:
		grand_total_hour = (total_day * 8) + (total_hour / 24) * 8
	else:
		grand_total_hour = (total_day * 8) + total_hour	
		
	return grand_total_hour


def checkM1247StandardBusinessRules(start_date, end_date, leave_type_id):
	if (start_date > end_date):
		return True, _("วันที่เริ่มต้นต้องน้อยกว่าวันที่สุดท้าย")
	elif (start_date == end_date):
	    return True, _("เลือกช่วงเวลาไม่ถูกต้อง")
	else:
		total_hour = checkM1247TotalHours('M1247', start_date, end_date, leave_type_id)
		print("debug 1 : " + str(total_hour))

		if total_hour <= 0:
			return True, _("วันลาตรงกับเสาร์-อาทิตย์")

		if total_hour.is_integer():
			return False, total_hour
		else:
			return True, _("ช่วงวันลามีเศษครึ่งชั่วโมง " + str(total_hour))
					
	return False, ""


def checkStandardBusinessRules(start_date, end_date):
	if (start_date > end_date):
		return True, _("วันที่เริ่มต้นต้องน้อยกว่าวันที่สุดท้าย")
	elif (start_date == end_date):
	    return True, _("เลือกช่วงเวลาไม่ถูกต้อง")
	else:
		total_minute = (end_date - start_date).total_seconds() / 60.0
		if (total_minute % 60) > 0:
			return True, _("ช่วงวันลามีเศษครึ่งชั่วโมง")

	return False, ""



def checkLeaveRequestOverMonth(employee_type, d1, d2):
	if(d1.month != d2.month):
		return True
	else:
		return False


def checkM1247BusinessRules(employee_type, start_date, end_date, leave_type_id):
	total_day = 0
	total_hour = 0
	result = 0
	day = 0
	hour = 0

	leave_type_include_weekend_list = {'6', '7', '10', '11', '13', '15'}
	if leave_type_id not in leave_type_include_weekend_list:
		excluded_day = {5, 6}
	else:
		excluded_day = {}

	while end_date >= start_date:
		next_date = start_date + dayDelta

		if next_date < end_date:
			if start_date.weekday() not in excluded_day:
				result = ((next_date - start_date).total_seconds() / 60.0) / 60
				day = result // 24
				hour = round(result % 24,1)
		else:
			if start_date.weekday() not in excluded_day:
				result = ((end_date - start_date).total_seconds() / 60.0) / 60
				day = result // 24
				hour = round(result % 24,1)

		total_day = total_day + day
		total_hour = total_hour + hour
		day = 0
		hour = 0
		start_date += dayDelta

	if total_hour == 24:
		grand_total_hour = (total_day * 8) + (total_hour / 24) * 8
	else:
		grand_total_hour = (total_day * 8) + total_hour	

	return False, grand_total_hour


def checkM1817BusinessRules(employee_type, start_date, end_date, leave_type_id):
	start_working_hour = 8
	stop_working_hour = 17
	
	leave_type_include_weekend_list = {'6','7','10','11','13','15'}
	if leave_type_id not in leave_type_include_weekend_list:
		excluded_day = {5, 6}		
	else:
		excluded_day = {}

	excluded_hour = {0, 1, 2, 3, 4, 5, 6, 7, 12, 18, 19, 20, 21, 22, 23}

	total_hour = 0
	total_minute = 0
	grand_total_hour = 0
	
	while (end_date >= start_date):
		if start_date.weekday() not in excluded_day:
			if (start_date.day == end_date.day):
				if (start_date.hour <= start_working_hour):
					if(end_date.hour <= stop_working_hour):
						for i in range(start_working_hour, end_date.hour):
							if i not in excluded_hour:
								total_hour += 1
								total_minute += 60
					else:
						for i in range(start_working_hour, stop_working_hour):
							if i not in excluded_hour:
								total_hour += 1
								total_minute += 60
				else:
					for i in range(start_date.hour, end_date.hour):
						if i not in excluded_hour:
							total_hour += 1
							total_minute += 60
			else:
				for i in range(start_date.hour, stop_working_hour):
					if i not in excluded_hour:
						total_hour += 1
						total_minute += 60

		grand_total_hour += total_hour
		total_hour = 0
		start_date += dayDelta

	return grand_total_hour


def checkLeaveRequestApproval(username):
	count = LeaveEmployee.objects.filter(emp_spid__exact=username).count()
	if count > 0:
		return True
	else:
		return False


def checkLeaveTypeIncludeWeekend(leave_type_id):
	leave_type_include_weekend_list = {'6','7','10','11','13','15'}
	if leave_type_id not in leave_type_include_weekend_list:		
		return True
	else:
		return False


def checkLeaveTypeIncludePublicHoliday(leave_type_id):
	leave_type_include_public_holiday_list = {'6','7','10','11','13','15'}
	if leave_type_id not in leave_type_include_public_holiday_list:		
		return True
	else:
		return False

