from django.contrib.auth.models import User
from page.models import UserProfile


def getDefaultLanguage(username):
	default_language = UserProfile.objects.filter(username=username).values_list('language', flat=True).get()
	if default_language:
		return default_language
	else:
		return 'en'

