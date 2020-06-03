from django.forms import ModelForm
from django.contrib.auth.models import User
from django import forms

class UserForm(ModelForm):
	password = forms.CharField(max_length=128, error_messages={'required': 'กรุณาป้อนรหัสผ่านเก่า'}, widget=forms.PasswordInput(attrs={'autocomplete':'off'}))
	new_password = forms.CharField(max_length=128, error_messages={'required': 'กรุณาป้อนรหัสผ่านใหม่'}, widget=forms.TextInput(attrs={'autocomplete':'off'}))
	confirm_new_password = forms.CharField(max_length=128, error_messages={'required': 'กรุณาป้อนรหัสผ่านใหม่อีกครั้ง'}, widget=forms.TextInput(attrs={'autocomplete':'off'}))

	class Meta:
		model = User
		fields = ['password']

	def __init__(self, *args, **kwargs):
		self.user = kwargs.pop('user')
		super(UserForm, self).__init__(*args, **kwargs)
		self.fields['password'].widget.attrs = {'class': 'form-control'}
		self.fields['password'].widget.attrs['placeholder'] = "ป้อนรหัสผ่านเก่า"
		self.fields['new_password'].widget.attrs = {'class': 'form-control'}
		self.fields['new_password'].widget.attrs['placeholder'] = "ป้อนรหัสผ่านใหม่"
		self.fields['confirm_new_password'].widget.attrs = {'class': 'form-control'}
		self.fields['confirm_new_password'].widget.attrs['placeholder'] = "ป้อนรหัสผ่านใหม่อีกครั้ง"

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
		new_password = self.cleaned_data.get('new_password')
		if new_password != "":
			return new_password
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
