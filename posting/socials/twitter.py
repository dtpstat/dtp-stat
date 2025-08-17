from django import forms
from django.db import models
from django.contrib import admin

import tweepy

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
    
    @classmethod
    def send(self, post):
        model = post.account.social_data
        log_template = f"[{self.name}: {post.account.title}][{post.short}]" + " {0}"
        
        consumer_key = model.consumer_key
        consumer_secret = model.consumer_secret
        access_token = model.access_token
        access_token_secret = model.access_token_secret

        try:
            apiNew = tweepy.Client(
                access_token=access_token,
                access_token_secret=access_token_secret,
                consumer_key=consumer_key,
                consumer_secret=consumer_secret
            )

            apiNew.create_tweet(text=post.text)
        except Exception as e:
            raise RuntimeError(log_template.format(f"Ошибка при отправке твита: {e}"))
        
        return log_template.format("Твит успешно отправлен")
