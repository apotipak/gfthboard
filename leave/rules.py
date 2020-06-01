from datetime import datetime, timedelta

dayDelta = timedelta(days=1)

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