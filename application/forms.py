from django import forms
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Invisible

class FixPoint(forms.Form):
    captcha = ReCaptchaField()
    lat = forms.FloatField()
    long = forms.FloatField()