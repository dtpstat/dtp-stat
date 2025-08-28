import re, copy
from django import forms
from django.db import models
from django.contrib import admin
from django_cryptography.fields import encrypt
from .base import SocialNetworkBase, SocialNetworkAdminBase, HiddenModelAdmin

import telegram

class TelegramAccount(SocialNetworkBase):
    full_name = 'Telegram'
    
    token = encrypt(models.CharField(max_length=255))
    channel_id = models.CharField(max_length=100)
    
    ckeditor_config = copy.deepcopy(SocialNetworkBase.ckeditor_config)
    ckeditor_config['toolbar'].append([
        'Bold','Italic','Underline','Strike', '-',
        'Link','Unlink', '-',
        'Blockquote', '-',
        'Image', '-',
        'SpecialChar','EmojiPanel', '-',
        'RemoveFormat',
    ])
    ckeditor_config['allowedContent'] = (
        'b i u strike strong em;'           # текстовое форматирование
        'a[!href];'                         # ссылки
        'blockquote;'                       # цитаты
        'img[!src,alt,width,height];'       # изображения
    )
    
    def clean_publish_data(self, content):    
        # 1. Находим <img> и сохраняем src
        img_match = re.search(r'<img [^>]*src="([^"]+)"[^>]*>', content)
        photo_src = img_match.group(1) if img_match else None
        
        # 2. Удаляем <img> из текста
        content = re.sub(r'<img [^>]*>', '', content)

        # 3. Убираем теги <p> и <br />, оставляя переносы строк
        content = re.sub(r'</?p>', '', content)
        content = re.sub(r'<br\s*/?>', '\n', content)
    
        return content.strip(), photo_src
    
    def post(self, post):
        self.log_template = f"[{self.full_name}: {post.account.title}][{post.short}]" + " {0}"

        try:
            bot = telegram.Bot(token=self.token)
        except telegram.error.InvalidToken as e:
            return self.error(f"Недействительный токен: {e}")

        content, photo_src = self.clean_publish_data(post.content)

        try:
            if photo_src:
                # Telegram умеет брать фото как файлом, так и по URL
                bot.send_photo(
                    chat_id=self.channel_id,
                    photo=photo_src,
                    caption=content,
                    parse_mode='HTML',
                    timeout=30
                )

                bot.send_message(
                    chat_id=self.channel_id,
                    text=content,
                    parse_mode='HTML',
                    timeout=30
                )            else:
                bot.send_message(
                    chat_id=self.channel_id,
                    text=content,
                    timeout=30
                )
        except telegram.error.Unauthorized as e:
            return self.error(f"Ошибка авторизации: {e}")
        except telegram.error.BadRequest as e:
            return self.error(f"Некорректный запрос: {e}")
        except Exception as e:
            return self.error(f"Ошибка при отправке поста: {e}")

        return self.log("Пост успешно отправлен")
class TelegramAccountForm(forms.ModelForm):
    class Meta:
        model = TelegramAccount
        fields = ['token', 'channel_id']
        widgets = {
            'token': forms.PasswordInput(render_value=False),
        }
        
class TelegramAccountAdmin(SocialNetworkAdminBase, HiddenModelAdmin):
    name = 'telegram'
    
admin.site.register(TelegramAccount, TelegramAccountAdmin)
