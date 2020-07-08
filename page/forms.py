from django.forms import ModelForm
from django.contrib.auth.models import User
from .models import UserProfile, ComDivision
from leave.models import LeaveEmployee
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
		self.fields['password'].widget.attrs['placeholder'] = _("Enter old password")
		self.fields['new_password'].widget.attrs = {'class': 'form-control'}
		self.fields['new_password'].widget.attrs['placeholder'] = _("Enter new password")
		self.fields['confirm_new_password'].widget.attrs = {'class': 'form-control'}
		self.fields['confirm_new_password'].widget.attrs['placeholder'] = _("Reenter new password")

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
					raise forms.ValidationError(_("New password is name same"))
				else:
					if new_password == password:
						raise forms.ValidationError("รหัสผ่านใหม่ซ้ำกับรหัสผ่านเก่า")	
					else:
						return cleaned_data

			else:
				raise forms.ValidationError("รหัสใหม่ควรยาวอย่างน้อย 6 ตัวอักษร และประกอบด้วย ตัวเลข ตัวหนังสือ สัญลักษณ์")			

		else:
			raise forms.ValidationError(_("Incorrect old password"))


		return cleaned_data
		

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
		else:
			default_language = 'th'

		self.initial['language_code'] = default_language

	def clean(self):
		cleaned_data = super(LanguageForm, self).clean()
		language = self.cleaned_data.get('language_code')
		return cleaned_data


class ViewAllStaffForm(ModelForm):
	first_name = forms.CharField(label=_('Employee Name'), max_length=128, required=False, widget=forms.TextInput(attrs={'autocomplete':'off'}))	
	department_list = forms.ModelChoiceField(label=_('Select department'), queryset=None, required=False, widget=forms.Select(attrs={'class':'form-control'}))
	
	class Meta:
		model = LeaveEmployee
		fields = ['emp_id','emp_fname_en','emp_fname_th','pos_en','emp_fname_th','emp_lname_th','pos_th']

	def __init__(self, *args, **kwargs):
		department_id_included = {30,35,98,102,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,124,125,126,127,128,129,133,134,136,137,138,139,140,141,142,208,211,213,226,228,231,233,249,257,258,259,261,265,267,268,270,271,272}
		self.user = kwargs.pop('user')		
		super(ViewAllStaffForm, self).__init__(*args, **kwargs)
		self.fields['first_name'].widget.attrs={'class': 'form-control form-control-md'}
		self.fields['department_list'].queryset=ComDivision.objects.filter(com_id=1).filter(div_id__in=(department_id_included)).order_by('div_en')		
		self.fields['department_list'].widget.attrs={'class': 'form-control form-control-md'}
		self.fields['department_list'].empty_label = _("All departments")
		self.fields['first_name'].widget.attrs['placeholder'] = _("Enter employee name")
		#self.fields['department_list'].widget.attrs['placeholder'] = _("Select department")
		
	def clean(self):
		cleaned_data = super(ViewAllStaffForm, self).clean()
		first_name = self.cleaned_data.get('first_name')
		return cleaned_data

