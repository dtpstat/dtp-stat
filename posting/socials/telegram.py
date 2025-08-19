from django import forms
from django.db import models
from django.contrib import admin

import telegram
import os

from .base import SocialNetworkAdminBase, HiddenModelAdmin

class TelegramAccount(models.Model):
    name = 'Telegram'
    
    token = models.CharField(max_length=255)
    channel_id = models.CharField(max_length=100)
    
    def send(self, post):
        log_template = f"[{self.name}: {post.account.title}][{post.short}]" + " {0}"

        bot = telegram.Bot(token=self.token)

        try:
            bot.send_message(chat_id=self.channel_id, text=post.text)
        except Exception as e:
            raise RuntimeError(log_template.format(f"Ошибка при отправке поста: {e}"))
            
        return log_template.format("Пост успешно отправлен")

class TelegramAccountForm(forms.ModelForm):
    class Meta:
        model = TelegramAccount
        fields = ['token', 'channel_id']
        
class TelegramAccountAdmin(SocialNetworkAdminBase, HiddenModelAdmin):
    social_network_name = 'telegram'
    
admin.site.register(TelegramAccount, TelegramAccountAdmin)
