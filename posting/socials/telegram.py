from django import forms
from django.db import models
from django.contrib import admin

import telegram
import os

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
    
    @classmethod
    def send(self, post):
        model = post.account.social_data
        log_template = f"[{self.name}: {post.account.title}][{post.short}]" + " {0}"
        
        token = model.token
        channel_id = model.channel_id

        bot = telegram.Bot(token=token)

        try:
            bot.send_message(chat_id=channel_id, text=post.text)
        except Exception as e:
            raise RuntimeError(log_template.format(f"Ошибка при отправке поста: {e}"))
            
        return log_template.format("Пост успешно отправлен")
