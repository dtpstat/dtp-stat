from django import forms
from django.db import models
from django.contrib import admin

import tweepy

from .base import SocialNetworkBase, SocialNetworkAdminBase, HiddenModelAdmin

class TwitterAccount(SocialNetworkBase):
    full_name = 'Twitter'
    
    consumer_key = models.CharField(max_length=255)
    consumer_secret = models.CharField(max_length=255)
    access_token = models.CharField(max_length=255)
    access_token_secret = models.CharField(max_length=255)
    
    def send(self, post):
        self.log_template = f"[{self.full_name}: {post.account.title}][{post.short}]" + " {0}"

        try:
            apiNew = tweepy.Client(
                access_token=self.access_token,
                access_token_secret=self.access_token_secret,
                consumer_key=self.consumer_key,
                consumer_secret=self.consumer_secret
            )

            apiNew.create_tweet(text=post.text)
        except Exception as e:
            return self.error(f"Ошибка при отправке твита: {e}")
        
        return self.log("Твит успешно отправлен")


class TwitterAccountForm(forms.ModelForm):
    class Meta:
        model = TwitterAccount
        fields = ['consumer_key', 'consumer_secret', 'access_token', 'access_token_secret']

class TwitterAccountAdmin(SocialNetworkAdminBase, HiddenModelAdmin):
    name = 'twitter'
    
admin.site.register(TwitterAccount, TwitterAccountAdmin)
