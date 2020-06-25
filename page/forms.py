from django.forms import ModelForm
from django.contrib.auth.models import User
from .models import UserProfile
from django import forms
import re
from django.utils.translation import ugettext_lazy as _


class UserForm(ModelForm):
	password = forms.CharField(max_length=128, error_messages={'required': 'กรุณาป้อนรหัสผ่านเก่า'}, widget=forms.PasswordInput(attrs={'autocomplete':'off'}))
	new_password = forms.CharField(max_length=128, error_messages={'required': 'กรุณาป้อนรหัสผ่านใหม่'}, widget=forms.TextInput(attrs={'autocomplete':'off'}))
	confirm_new_password = forms.CharField(max_length=128, error_messages={'required': 'กรุณาป้อนรหัสผ่านใหม่อีกครั้ง'}, widget=forms.TextInput(attrs={'autocomplete':'off'}))

	class Meta:
		model = User
		fields = ['password']

	def __init__(self, *args, **kwargs):
		self.user = kwargs.pop('user')
		self.confirm_new_password = kwargs.pop('confirm_new_password', None)
		super(UserForm, self).__init__(*args, **kwargs)
		self.fields['password'].widget.attrs = {'class': 'form-control'}
		self.fields['password'].widget.attrs['placeholder'] = "ป้อนรหัสผ่านเก่า"
		self.fields['new_password'].widget.attrs = {'class': 'form-control'}
		self.fields['new_password'].widget.attrs['placeholder'] = "ป้อนรหัสผ่านใหม่"
		self.fields['confirm_new_password'].widget.attrs = {'class': 'form-control'}
		self.fields['confirm_new_password'].widget.attrs['placeholder'] = "ป้อนรหัสผ่านใหม่อีกครั้ง"

	def clean(self):
		cleaned_data = super(UserForm, self).clean()
		username = self.user.username
		password = self.cleaned_data.get('password')
		new_password = self.cleaned_data.get('new_password')
		confirm_new_password = self.cleaned_data.get('confirm_new_password')		
		userobj = User.objects.get(username=username)

		if userobj.check_password(password):
			if re.match(r"^(?=.*[\d])(?=.*[a-z])(?=.*[@#$])[\w\d@#$]{6,12}$", new_password):							
				if new_password != confirm_new_password:
					raise forms.ValidationError("รหัสผ่านใหม่ไม่ตรงกัน")
				else:
					if new_password == password:
						raise forms.ValidationError("รหัสผ่านใหม่ซ้ำกับรหัสผ่านเก่า")	
					else:
						return cleaned_data

			else:
				raise forms.ValidationError("รหัสใหม่ควรยาวอย่างน้อย 6 ตัวอักษร และประกอบด้วย ตัวเลข ตัวหนังสือ สัญลักษณ์")			

		else:
			raise forms.ValidationError("รหัสเก่าไม่ถูกต้อง")


		return cleaned_data

	'''
	def clean_password(self):
		cleaned_data = super(UserForm, self).clean()
		
		password = self.cleaned_data.get('password')
		username = self.user.username
		userobj = User.objects.get(username=username)
		if userobj.check_password(password):
			return password
		else:
			raise forms.ValidationError("รหัสผ่านเก่าไม่ถูกต้อง")

	def clean_new_password(self):
		data = super(UserForm, self).clean()
		new_password = self.cleaned_data['new_password']

		if new_password != "":					
			#if re.match(r"^(?=.*[\d])(?=.*[A-Z])(?=.*[a-z])(?=.*[@#$])[\w\d@#$]{6,12}$", new_password):
			if re.match(r"^(?=.*[\d])(?=.*[a-z])(?=.*[@#$])[\w\d@#$]{6,12}$", new_password):				
				return new_password
			else:
				raise forms.ValidationError("รหัสผ่านใหม่ควรยาวอย่างน้อย 6 ตัวอักษร และประกอบด้วย ตัวเลข ตัวหนังสือ สัญลักษณ์")
		else:
			raise forms.ValidationError("กรุณาป้อนรหัสผ่านใหม่")

	def clean_confirm_new_password(self):
		data = super(UserForm, self).clean()
		new_password = self.cleaned_data.get('new_password')
		confirm_new_password = self.cleaned_data.get('confirm_new_password')

		if confirm_new_password != "":
			if new_password != confirm_new_password:
				raise forms.ValidationError("รหัสผ่านใหม่ไม่ตรงกัน")
			else:
				return confirm_new_password
		else:
			raise forms.ValidationError("กรุณาป้อนรหัสผ่านใหม่อีกครั้ง")
	'''

class LanguageForm(ModelForm):
	language_options = (('en','English'),('th','Thai'))
	language_code = forms.CharField(label=_('Set Display Language'), max_length=2, widget=forms.Select(choices=language_options), initial=0)	

	class Meta:
		model = UserProfile
		fields = ['language']

	def __init__(self, *args, **kwargs):
		self.user = kwargs.pop('user')
		super(LanguageForm, self).__init__(*args, **kwargs)
		self.fields['language_code'].widget.attrs={'class': 'form-control'}

		if UserProfile.objects.filter(username=self.user.username).exists():
			default_language = UserProfile.objects.filter(username=self.user.username).values_list('language', flat=True).get()
			print("default lang = " + default_language)
		else:
			default_language = 'en'

		self.initial['language_code'] = default_language

	def clean(self):
		cleaned_data = super(LanguageForm, self).clean()
		language = self.cleaned_data.get('language_code')
		return cleaned_data
