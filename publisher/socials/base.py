from django.db import models
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect
from django.urls import reverse

class SocialNetworkBase(models.Model):
    class Meta:
        abstract = True

    full_name = None
    log_template = None
    
    ckeditor_config = {
        'toolbar': [
            [
                'Cut', 'Copy', 'Paste', 'PasteText', 'PasteFromWord', 'PasteFromDocs', '-',
                'SelectAll', '-',
                'Undo', 'Redo', '-',
                'Find', 'Replace', '-',
                'spellchecker', 'Scayt', '-',
                'Source', '-',
                'Maximize'
            ],
            '/',
        ],
        'autoGrow_minHeight': 250,
        'autoGrow_maxHeight': 600,
        'autoGrow_onStartup': True,
        'toolbarCanCollapse': True,
        'language': 'ru',
        'removeFormatTags': (
            'b,i,u,strike,strong,em,hr,a,img,blockquote'
        ),
        'extraPlugins': 'emoji,pastefromgdocs,autogrow,selectallcontextmenu,autolink',
    }
    
    
    def log(self, message):
        return self.log_template.format(message)
        
    def error(self, message):
        return "[ERROR]" + self.log_template.format(message)
    
    def clean_publish_data(self, content):
        raise NotImplementedError
    
    def post(self, post):
        raise NotImplementedError

class SocialNetworkAdminBase(admin.ModelAdmin):
    
    name = None
    
    def response_add(self, request, obj, post_url_continue=None):
        from publisher.account import Account  # импорт внутрь метода!
        
        if not self.name:
            raise NotImplementedError('social_network_name must be set')

        account_title = request.GET.get('_account_title', '')
        account_social_network = request.GET.get('_account_social_network', self.name)
        social_type = ContentType.objects.get_for_model(obj)
        
        Account.objects.create(
            social_network=account_social_network,
            title=account_title,
            social_type=social_type,
            social_id=obj.pk,
        )

        url = reverse('admin:publisher_account_changelist')
        return HttpResponseRedirect(url)
    
    def response_change(self, request, obj):
        # После изменения соцсети → список аккаунтов
        url = reverse('admin:publisher_account_changelist')
        return HttpResponseRedirect(url)


class HiddenModelAdmin(admin.ModelAdmin):
    def get_model_perms(self, request):
        # Возвращаем пустой словарь — модель не будет видна в админке, но доступна по прямой ссылке
        return {}