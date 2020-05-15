from django import forms
from captcha.fields import ReCaptchaField
from allauth.account.forms import SetPasswordField, PasswordField
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from allauth.account.forms import SignupForm
from application import models


class FixPoint(forms.Form):
    captcha = ReCaptchaField()
    lat = forms.FloatField(required=False)
    long = forms.FloatField(required=False)


class FixPointModerator(forms.Form):
    lat = forms.FloatField(required=False)
    long = forms.FloatField(required=False)


class MyCustomSignupForm(SignupForm):

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        if username not in [x.username for x in models.Moderator.objects.all()]:
            raise ValidationError('Вас нет в списке модераторов. Если вы хотите стать им в своем регионе, напишите нам на почту info@dtp-stat.ru')

    def save(self, request):
        user = super(MyCustomSignupForm, self).save(request)
        models.Moderator.objects.filter(username=user.username).update(user=user)
        return user