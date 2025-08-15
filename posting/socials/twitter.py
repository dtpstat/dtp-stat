from django import forms
from django.db import models
from django.contrib import admin

from posting.accounts.network_base import SocialNetworkAdminBase, HiddenModelAdmin, SocialNetwork

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

twitter = {'twitter': SocialNetwork('twitter', TwitterAccount, TwitterAccount, 'Twitter')}