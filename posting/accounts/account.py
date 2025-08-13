from django.db import models
from django import forms
from django.contrib import admin
from django.urls import reverse
from django.shortcuts import redirect
from django.utils.http import urlencode


from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from posting.accounts.social_registry import TYPE_CHOICES

class Account(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    
    social_network = models.CharField(max_length=50, choices=TYPE_CHOICES, verbose_name="Соцсеть")
    datetime_creation = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255)

    # Поля для GenericForeignKey
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    social_data = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return f"{self.get_social_network_display()} — {self.title}"
    
    class Meta:
        verbose_name = 'Аккаунт соцсети'
        verbose_name_plural = 'Аккаунты соцсетей'
        
    def delete(self, using=None, keep_parents=False):
        # Если связанный объект соцсети существует — удаляем его
        if self.social_data:
            self.social_data.delete()
        # Затем вызываем стандартное удаление самого Account
        return super().delete(using=using, keep_parents=keep_parents)

class AccountForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Если объект существует (редактируем), заблокировать поле social_network
        if self.instance and self.instance.pk:
            self.fields['social_network'].disabled = True
        
    class Meta:
        model = Account
        fields = ['user', 'social_network', 'title']
   

class AccountAdmin(admin.ModelAdmin):
    form = AccountForm
    list_display = ['user', 'social_network', 'title'] 
    
    def add_view(self, request, form_url='', extra_context=None):
        if request.method == 'POST':
            title = request.POST.get('title', '')
            social_network = request.POST.get('social_network', '')
            user_id = request.POST.get('user')  # <-- берём id пользователя

            url_name = f'admin:posting_{social_network}account_add'
            url = reverse(url_name)
            query = urlencode({
                '_account_title': title,
                '_account_social_network': social_network,
                '_account_user_id': user_id,
            })
            redirect_url = f"{url}?{query}"
            return redirect(redirect_url)

        return super().add_view(request, form_url, extra_context)
    
    # TODO: Нормальное редактирование, опции:
    # [DONE] 1. Сохранять account -> перебрасыать на редактирование [network_base]
    # 2. Пробрассывать данные с account на [network_base] и там сохранять
    # 3. Сделать единую форму с account & [network_base] - удобнее всего!
    
    def response_change(self, request, obj):

        # Получаем имя соцсети
        social_network = obj.social_network.lower()
        # Получаем id связанной модели
        related_obj_id = obj.object_id

        # Строим URL редактирования для конкретной соцсети
        url_name = f'admin:posting_{social_network}account_change'
        url = reverse(url_name, args=[related_obj_id])
        return redirect(url)