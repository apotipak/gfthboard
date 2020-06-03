from django.forms import ModelForm
from django.contrib.auth.models import User
from django import forms

class UserForm(ModelForm):
	password = forms.CharField(max_length=128)

	class Meta:
		model = User
		fields = ['password']

	def __init__(self, *args, **kwargs):
		self.user = kwargs.pop('user')
		super(UserForm, self).__init__(*args, **kwargs)
		self.fields['password'].widget.attrs = {'class': 'form-control'}
		self.fields['password'].queryset = User.objects.filter(User__username=self.user.username)

	def clean(self):
		cleaned_data = super(UserForm, self).clean()
		old_password = self.cleaned_data.get('old_password')
		return cleaned_data