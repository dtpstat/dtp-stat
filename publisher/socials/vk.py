import os, copy
from django import forms
from django.db import models
from django.contrib import admin
from django_cryptography.fields import encrypt
from .base import SocialNetworkBase, SocialNetworkAdminBase, HiddenModelAdmin

import vk_api

class VkAccount(SocialNetworkBase):
    full_name = 'VK'
    
    phone_number = encrypt(models.CharField(max_length=20))
    password = encrypt(models.CharField(max_length=128))
    community_id = models.CharField(max_length=50)
    
    cckeditor_config = copy.deepcopy(SocialNetworkBase.ckeditor_config)
    ckeditor_config['toolbar'].append([
        'Image', '-',
        'SpecialChar','EmojiPanel', '-',
        'RemoveFormat',
    ])
    ckeditor_config['allowedContent'] = (
        'img[!src,alt,width,height];'       # изображения
        'a[!href];'                         # авто-ссылки
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
        
        vk_session = vk_api.VkApi(self.phone_number, self.password)
        try:
            vk_session.auth(token_only=True)
        except Exception as e:
            return self.error(f"Ошибка авторизации: {e}")
     
        vk = vk_session.get_api()
        
        content, photo_src = self.clean_publish_data(post.content)
        
        if (photo_src):
            try:
                upload = vk_api.VkUpload(vk_session)
                photo = upload.photo_wall(photo_src, group_id=self.community_id)[0]
            except Exception as e:
                return self.error(f"Ошибка при загрузке фото: {e}")
            
        attachment = f"photo{photo['owner_id']}_{photo['id']}" if (photo_src) else None

        try:
            vk.wall.post(owner_id=-int(self.community_id), from_group=1, message=post.content, attachments=attachment)
        except Exception as e:
            return self.error(f"Ошибка при отправке поста: {e}")

        return self.log("Пост успешно отправлен")
    
class VkAccountForm(forms.ModelForm):
    class Meta:
        model = VkAccount
        fields = ['phone_number', 'password', 'community_id']
        widgets = {
            'phone_number': forms.PasswordInput(render_value=False),
            'password': forms.PasswordInput(render_value=False),
        }
        
class VkAccountAdmin(SocialNetworkAdminBase, HiddenModelAdmin):
    name = 'vk'
    
admin.site.register(VkAccount, VkAccountAdmin)
    