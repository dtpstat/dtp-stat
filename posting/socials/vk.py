from django import forms
from django.db import models
from django.contrib import admin

import vk_api
import os

from .base import SocialNetworkAdminBase, HiddenModelAdmin, ServiceBase

class VkAccount(models.Model):
    phone_number = models.CharField(max_length=20)
    password = models.CharField(max_length=128)
    community_id = models.CharField(max_length=50)
    
class VkAccountForm(forms.ModelForm):
    class Meta:
        model = VkAccount
        fields = ['phone_number', 'password', 'community_id']
        
class VkAccountAdmin(SocialNetworkAdminBase, HiddenModelAdmin):
    social_network_name = 'vk'
    
admin.site.register(VkAccount, VkAccountAdmin)

class VkService(ServiceBase):
    name = 'VK'
    
    @classmethod
    def send(self, post):
        model = post.account.social_data
        log_template = f"[{self.name}: {post.account.title}][{post.short}]" + " {0}"
        
        phone_number = model.phone_number
        password = model.password
        community_id = model.community_id
        
        vk_session = vk_api.VkApi(phone_number, password)
        try:
            vk_session.auth(token_only=True)
        except Exception as e:
            raise RuntimeError(log_template.format(f"Ошибка авторизации: {e}"))
     
        vk = vk_session.get_api()
        try:
            vk.wall.post(owner_id=-int(community_id), from_group=1, message=post.text)
        except Exception as e:
            raise RuntimeError(log_template.format(f"Ошибка при отправке поста: {e}"))

        return log_template.format("Пост успешно отправлен")
        