from django.contrib.auth.models import User
from page.models import UserProfile
from django.core.exceptions import ObjectDoesNotExist


def getDefaultLanguage(username):
	default_language = 'th'
	
	if UserProfile.objects.filter(username=username).exists():
		try:
			default_language = UserProfile.objects.filter(username=username).values_list('language', flat=True).get()
		except UserProfile.DoesNotExists:
			default_language = 'en'
	
	print("debug: " + default_language)

	return default_language

