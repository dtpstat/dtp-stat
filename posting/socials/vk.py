from django import forms
from django.db import models
from django.contrib import admin

import vk_api
import os

from .base import SocialNetworkBase, SocialNetworkAdminBase, HiddenModelAdmin

class VkAccount(SocialNetworkBase):
    full_name = 'VK'
    
    phone_number = models.CharField(max_length=20)
    password = models.CharField(max_length=128)
    community_id = models.CharField(max_length=50)
    
    ckeditor_config = {
        'toolbar': [
            SocialNetworkBase.ckeditor_toolbar_top,
            '/',
            [
                'Image', '-',
                'SpecialChar','EmojiPanel', '-',
                'RemoveFormat',
            ],
        ],
        'allowedContent': (
            'img[!src,alt,width,height];'       # изображения
        ),
        'extraPlugins': SocialNetworkBase.ckeditor_extra_plugins,
    }
    
    def post(self, post):
        self.log_template = f"[{self.full_name}: {post.account.title}][{post.short}]" + " {0}"
        
        vk_session = vk_api.VkApi(self.phone_number, self.password)
        try:
            vk_session.auth(token_only=True)
        except Exception as e:
            return self.error(f"Ошибка авторизации: {e}")
     
        vk = vk_session.get_api()
        try:
            vk.wall.post(owner_id=-int(self.community_id), from_group=1, message=post.text)
        except Exception as e:
            return self.error(f"Ошибка при отправке поста: {e}")

        return self.log("Пост успешно отправлен")
    
class VkAccountForm(forms.ModelForm):
    class Meta:
        model = VkAccount
        fields = ['phone_number', 'password', 'community_id']
        
class VkAccountAdmin(SocialNetworkAdminBase, HiddenModelAdmin):
    name = 'vk'
    
admin.site.register(VkAccount, VkAccountAdmin)
    