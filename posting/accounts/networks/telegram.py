from django import forms
from django.db import models
from django.contrib import admin

from posting.accounts.network_base import SocialNetworkAdminBase, HiddenModelAdmin, SocialNetwork

class TelegramAccount(models.Model):
    token = models.CharField(max_length=255)
    channel_id = models.CharField(max_length=100)

class TelegramAccountForm(forms.ModelForm):
    class Meta:
        model = TelegramAccount
        fields = ['token', 'channel_id']
        
class TelegramAccountAdmin(SocialNetworkAdminBase, HiddenModelAdmin):
    social_network_name = 'telegram'
    
admin.site.register(TelegramAccount, TelegramAccountAdmin)

telegram = {'telegram': SocialNetwork('telegram', TelegramAccount, TelegramAccountForm, 'Telegram')}