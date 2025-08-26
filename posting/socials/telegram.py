from django import forms
from django.db import models
from django.contrib import admin

import telegram
import os

from .base import SocialNetworkBase, SocialNetworkAdminBase, HiddenModelAdmin

class TelegramAccount(SocialNetworkBase):
    full_name = 'Telegram'
    
    token = models.CharField(max_length=255)
    channel_id = models.CharField(max_length=100)
    
    ckeditor_config = {
        'toolbar': [
            SocialNetworkBase.ckeditor_toolbar_top,
            '/',
            [
                'Bold','Italic','Underline','Strike', '-',
                'Link','Unlink', '-',
                'Blockquote', '-',
                'Image', '-',
                'SpecialChar','EmojiPanel', '-',
                'RemoveFormat',
            ],
        ],
        'allowedContent': (
            'b i u strike strong em;'           # текстовое форматирование
            'a[!href];'                         # ссылки и файлы
            'blockquote;'                       # цитаты
            'img[!src,alt,width,height];'       # изображения
        ),
        'extraPlugins': SocialNetworkBase.ckeditor_extra_plugins,
    }
    
    def post(self, post):
        self.log_template = f"[{self.full_name}: {post.account.title}][{post.short}]" + " {0}"

        bot = telegram.Bot(token=self.token)

        try:
            bot.send_message(chat_id=self.channel_id, text=post.text)
        except Exception as e:
            return self.error(f"Ошибка при отправке поста: {e}")
            
        return self.log("Пост успешно отправлен")

class TelegramAccountForm(forms.ModelForm):
    class Meta:
        model = TelegramAccount
        fields = ['token', 'channel_id']
        
class TelegramAccountAdmin(SocialNetworkAdminBase, HiddenModelAdmin):
    name = 'telegram'
    
admin.site.register(TelegramAccount, TelegramAccountAdmin)
