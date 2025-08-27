from django import forms
from django.db import models
from django.contrib import admin
from django_cryptography.fields import encrypt

import telegram
import os

from .base import SocialNetworkBase, SocialNetworkAdminBase, HiddenModelAdmin

class TelegramAccount(SocialNetworkBase):
    full_name = 'Telegram'
    
    token = encrypt(models.CharField(max_length=255))
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
    
    def clean_publish_data(self, text):    
        # 1. Находим <img> и сохраняем src
        img_match = re.search(r'<img [^>]*src="([^"]+)"[^>]*>', text)
        photo_src = img_match.group(1) if img_match else None
        
        # 2. Удаляем <img> из текста
        text = re.sub(r'<img [^>]*>', '', text)

        # 3. Убираем теги <p> и <br />, оставляя переносы строк
        text = re.sub(r'</?p>', '', text)
        text = re.sub(r'<br\s*/?>', '\n', text)
    
        return text.strip(), photo_src
    
    def post(self, post):
        self.log_template = f"[{self.full_name}: {post.account.title}][{post.short}]" + " {0}"

        bot = telegram.Bot(token=self.token)
        
        text, photo_src = self.clean_publish_data(post.text)
        
        try:
            if (photo_src):
                bot.sendPhoto(chat_id=self.channel_id, photo=photo_src, caption=text)
            else:
                bot.send_message(chat_id=self.channel_id, text=text)
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
