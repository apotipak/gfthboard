from django.contrib.admin.sites import AdminSite
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.admin.forms import AdminAuthenticationForm
from django_otp.admin import OTPAdminSite, OTPAuthenticationFormMixin
from django.contrib import admin
from django import forms


class CustomAuthForm(OTPAuthenticationFormMixin, AuthenticationForm):
    print("DEBUG")
    otp_error_messages = dict(OTPAuthenticationFormMixin.otp_error_messages,
        token_required = 'Please enter your authentication code.',
        invalid_token = 'Incorrect authentication code. Please try again.',
    )

    otp_device = forms.CharField(required=False, widget=forms.Select)
    otp_token = forms.CharField(required=False, widget=forms.TextInput(attrs={'autocomplete': 'off'}))
    otp_challenge = forms.CharField(required=False)
    recaptcha_token = forms.CharField(required=True)

    def clean(self):
        url = 'https://www.google.com/recaptcha/api/siteverify'
        params = {
            'secret': 'SECRET',
            'response': self.cleaned_data['recaptcha_token']
        }
        response = requests.post(url, params)
        print(response.json())
        if response.json()['success'] == False:
            raise forms.ValidationError('ReCAPTCHA is invalid.')
        if response.status_code == requests.codes.ok:
            print(response.json()['success'])
            print(response.json()['action'])
            if response.json()['success'] and response.json()['action'] == '/admin/login/':
                print('Captcha valid for user={}'.format(self.cleaned_data.get('username')))
            else:
                print('Captcha valid for user={}'.format(self.cleaned_data.get('username')))
                raise forms.ValidationError('ReCAPTCHA is invalid.')
        else:
                print('Captcha valid for user={}'.format(self.cleaned_data.get('username')))
        self.cleaned_data = super().clean() # Moved
        self.clean_otp(self.get_user()) # changed
        print(self.cleaned_data)
        return self.cleaned_data

# AdminSite.login_form = CustomAuthForm
