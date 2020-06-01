from datetime import datetime, timedelta

dayDelta = timedelta(days=1)

def checkBusinessHour(employee_type, start_date, end_date):
	status = True	
	if employee_type == 'M1':
		while (start_date <= end_date):
		    if start_date.hour in (0,1,2,3,4,5,6,7,12,18,19,20,21,22,23):
		    	status = False
		    if end_date.hour in (0,1,2,3,4,5,6,7,12,18,19,20,21,22,23):
		    	status = False
		    start_date += dayDelta
	return status

def checkLeaveRequestHour(employee_type, d1, d2):
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

def checkLunchTime(employee_type, start_date_hour, end_date_hour):
    if start_date_hour == 12 or end_date_hour == 12:
        return True
    else:
        return False
