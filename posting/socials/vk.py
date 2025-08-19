from django import forms
from django.db import models
from django.contrib import admin

import vk_api
import os

from .base import SocialNetworkAdminBase, HiddenModelAdmin

class VkAccount(models.Model):
    name = 'VK'
    
    phone_number = models.CharField(max_length=20)
    password = models.CharField(max_length=128)
    community_id = models.CharField(max_length=50)
    
    def send(self, post):
        log_template = f"[{self.name}: {post.account.title}][{post.short}]" + " {0}"
        
        vk_session = vk_api.VkApi(self.phone_number, self.password)
        try:
            vk_session.auth(token_only=True)
        except Exception as e:
            raise RuntimeError(log_template.format(f"Ошибка авторизации: {e}"))
     
        vk = vk_session.get_api()
        try:
            vk.wall.post(owner_id=-int(self.community_id), from_group=1, message=post.text)
        except Exception as e:
            raise RuntimeError(log_template.format(f"Ошибка при отправке поста: {e}"))

        return log_template.format("Пост успешно отправлен")
    
class VkAccountForm(forms.ModelForm):
    class Meta:
        model = VkAccount
        fields = ['phone_number', 'password', 'community_id']
        
class VkAccountAdmin(SocialNetworkAdminBase, HiddenModelAdmin):
    social_network_name = 'vk'
    
admin.site.register(VkAccount, VkAccountAdmin)
    