from django import forms
from django.db import models
from django.contrib import admin

from .base import SocialNetworkAdminBase, HiddenModelAdmin, ServiceBase

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

class TelegramService(ServiceBase):
    
    name = 'Telegram'
    
    def convert(self, text):
        return f"TG converted: {text}"
    def send(self, text):
        return f"TG sent: {text}"
