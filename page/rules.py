from django.contrib.auth.models import User
from page.models import UserProfile
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone


def getDefaultLanguage(username):
	default_language = 'th'
	if UserProfile.objects.filter(username=username).exists():
		try:
			default_language = UserProfile.objects.filter(username=username).values_list('language', flat=True).get()
		except UserProfile.DoesNotExists:
			default_language = 'th'
	return default_language

def getDateFormatDisplay(language):
    today_day = timezone.now().day
    today_month = timezone.now().strftime('%B')
    if language == "th":
    	#today_year = timezone.now().year + 543
    	today_year = timezone.now().year
    else:
    	today_year = timezone.now().year
    today_date = str(today_day) + " " + today_month + " " + str(today_year)	
    return today_date