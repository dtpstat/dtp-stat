from django.db import models
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import get_user_model
from abc import ABC, abstractmethod

class SocialNetworkAdminBase(admin.ModelAdmin):
    social_network_name = None  # должен быть переопределён в наследнике

    def response_add(self, request, obj, post_url_continue=None):
        from posting.account import Account  # импорт внутрь метода!
        
        if not self.social_network_name:
            raise NotImplementedError('social_network_name must be set')

        account_title = request.GET.get('_account_title', '')
        account_social_network = request.GET.get('_account_social_network', self.social_network_name)
        user_id = request.GET.get('_account_user_id')

        User = get_user_model()
        user = User.objects.get(pk=user_id)

        content_type = ContentType.objects.get_for_model(obj)
        Account.objects.create(
            user=user,
            social_network=account_social_network,
            title=account_title,
            content_type=content_type,
            object_id=obj.pk,
        )

        url = reverse('admin:posting_account_changelist')
        return HttpResponseRedirect(url)
    
    def response_change(self, request, obj):
        # После изменения соцсети → список аккаунтов
        url = reverse('admin:posting_account_changelist')
        return HttpResponseRedirect(url)


class HiddenModelAdmin(admin.ModelAdmin):
    def get_model_perms(self, request):
        # Возвращаем пустой словарь — модель не будет видна в админке, но доступна по прямой ссылке
        return {}
    
class ServiceBase(ABC):
    name = None  # должен быть переопределён в наследнике

    @classmethod
    @abstractmethod
    def send(self, post):
        pass