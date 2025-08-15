from django import forms
from django.db import models
from django.contrib import admin

from .base import SocialNetworkAdminBase, HiddenModelAdmin, ServiceBase

class TwitterAccount(models.Model):
    consumer_key = models.CharField(max_length=255)
    consumer_secret = models.CharField(max_length=255)
    access_token = models.CharField(max_length=255)
    access_token_secret = models.CharField(max_length=255)

class TwitterAccountForm(forms.ModelForm):
    class Meta:
        model = TwitterAccount
        fields = ['consumer_key', 'consumer_secret', 'access_token', 'access_token_secret']

class TwitterAccountAdmin(SocialNetworkAdminBase, HiddenModelAdmin):
    social_network_name = 'twitter'
    
admin.site.register(TwitterAccount, TwitterAccountAdmin)

class TwitterService(ServiceBase):
    
    name = 'Twitter'
    
    def convert(self, text):
        return f"Twitter converted: {text}"
    
    def send(self, text):
        return f"Twitter sent: {text}"
