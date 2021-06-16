from django.contrib.auth.models import User
from page.models import UserProfile
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from .models import UserPasswordLog, UserLoginLog
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required


def getDefaultLanguage(username):
	default_language = 'th'
	if UserProfile.objects.filter(username=username).exists():
		try:
			default_language = UserProfile.objects.filter(username=username).values_list('language', flat=True).get()
		except UserProfile.DoesNotExists:
			default_language = 'th'
	return default_language

def getDateFormatDisplay_backup(language):
    today_day = timezone.now().day
    today_month = timezone.now().strftime('%B')

    if language == "th":
    	#today_year = timezone.now().year + 543
    	today_year = timezone.now().year
    else:
    	today_year = timezone.now().year    

    today_date = str(today_day) + " " + today_month + " " + str(today_year)	

    return today_date


def getDateFormatDisplay(language):
    today_day = timezone.now().strftime("%d/%m/%Y")
    return today_day


@login_required(login_url='/accounts/login/')
def isPasswordChanged(request):
	emp_id = request.user.username

	try:
		employee_info = UserPasswordLog.objects.get(emp_id=emp_id)
	except UserPasswordLog.DoesNotExist:
		employee_info = None

	if employee_info is not None:
		is_password_changed = employee_info.is_password_changed
		if is_password_changed:
			return True
		else:
			return False
	else:
		return True


@login_required(login_url='/accounts/login/')
def isStillUseDefaultPassword(request):	
	default_password = "123@gfth"
	user_info = User.objects.filter(username=request.user.username).get()
	if user_info.check_password(default_password):
		return True
	else:
		return False


def getLastLogin(request):
	try:
		user_login_log_obj = UserLoginLog.objects.values_list('login_date', flat=True).filter(emp_id=request.user.username).order_by('-login_date')[1:2] or None
	except:
		user_login_log_obj = None

	if user_login_log_obj is not None:
		last_login = user_login_log_obj[0].strftime("%d/%B/%Y %H:%M:%S")
	else:
		last_login = ""

	return last_login