from django.db import models
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import get_user_model

class SocialNetworkBase(models.Model):
    class Meta:
        abstract = True

    full_name = None
    log_template = None
    
    ckeditor_toolbar_top = [
        'Cut', 'Copy', 'Paste', 'PasteText', 'PasteFromWord', 'PasteFromDocs', '-',
        'SelectAll', '-',
        'Undo', 'Redo', '-',
        'Find', 'Replace', '-',
        'spellchecker', 'Scayt', '-',
        'Source', '-',
        'Maximize'
    ]
    ckeditor_extra_plugins = 'emoji,pastefromgdocs,autogrow,selectallcontextmenu,autolink'
    
    def log(self, message):
        return self.log_template.format(message)
        
    def error(self, message):
        return "[ERROR]" + self.log_template.format(message)
    
    def clean_publish_data(self, text):
        raise NotImplementedError
    
    def post(self, post):
        raise NotImplementedError

class SocialNetworkAdminBase(admin.ModelAdmin):
    
    name = None
    
    def response_add(self, request, obj, post_url_continue=None):
        from posting.account import Account  # импорт внутрь метода!
        
        if not self.name:
            raise NotImplementedError('social_network_name must be set')

        account_title = request.GET.get('_account_title', '')
        account_social_network = request.GET.get('_account_social_network', self.name)
        user_id = request.GET.get('_account_user_id')

        User = get_user_model()
        user = User.objects.get(pk=user_id)

        social_type = ContentType.objects.get_for_model(obj)
        Account.objects.create(
            user=user,
            social_network=account_social_network,
            title=account_title,
            social_type=social_type,
            social_id=obj.pk,
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