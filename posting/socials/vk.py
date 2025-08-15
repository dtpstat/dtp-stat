from django import forms
from django.db import models

from django.contrib import admin

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
    
    def convert(self, text):
        return f"VK converted: {text}"
    
    def send(self, text):
        return f"VK sent: {text}"
