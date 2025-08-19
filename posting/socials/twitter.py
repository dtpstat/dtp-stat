from django import forms
from django.db import models
from django.contrib import admin

import tweepy

from .base import SocialNetworkAdminBase, HiddenModelAdmin

class TwitterAccount(models.Model):
    name = 'Twitter'
    
    consumer_key = models.CharField(max_length=255)
    consumer_secret = models.CharField(max_length=255)
    access_token = models.CharField(max_length=255)
    access_token_secret = models.CharField(max_length=255)
    
    def send(self, post):
        log_template = f"[{self.name}: {post.account.title}][{post.short}]" + " {0}"

        try:
            apiNew = tweepy.Client(
                access_token=self.access_token,
                access_token_secret=self.access_token_secret,
                consumer_key=self.consumer_key,
                consumer_secret=self.consumer_secret
            )

            apiNew.create_tweet(text=post.text)
        except Exception as e:
            raise RuntimeError(log_template.format(f"Ошибка при отправке твита: {e}"))
        
        return log_template.format("Твит успешно отправлен")


class TwitterAccountForm(forms.ModelForm):
    class Meta:
        model = TwitterAccount
        fields = ['consumer_key', 'consumer_secret', 'access_token', 'access_token_secret']

class TwitterAccountAdmin(SocialNetworkAdminBase, HiddenModelAdmin):
    social_network_name = 'twitter'
    
admin.site.register(TwitterAccount, TwitterAccountAdmin)
