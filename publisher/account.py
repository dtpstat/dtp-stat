from django.db import models
from django import forms
from django.contrib import admin, messages
from django.urls import path, reverse, NoReverseMatch
from django.shortcuts import render, redirect
from django.utils.http import urlencode
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from .socials.socials import TYPE_CHOICES

class Account(models.Model):
    
    social_network = models.CharField(max_length=50, choices=TYPE_CHOICES, verbose_name="Соцсеть")
    datetime_creation = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255)

    social_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    social_id = models.PositiveIntegerField()
    social = GenericForeignKey('social_type', 'social_id')

    def __str__(self):
        return f"{self.get_social_network_display()}: {self.title}"
    
    class Meta:
        verbose_name = 'Аккаунт соцсети'
        verbose_name_plural = 'Аккаунты соцсетей'
        
    def delete(self, using=None, keep_parents=False):
        # Если связанный объект соцсети существует — удаляем его
        if self.social:
            self.social.delete()
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
        fields = ['social_network', 'title']
   
# action — только перенаправление на custom view с selected ids
def action_schedule_post(modeladmin, request, queryset):
    selected = queryset.values_list('pk', flat=True)
    # Передаём список id через GET (или POST) — если много id, лучше через POST или session.
    ids = ",".join(str(pk) for pk in selected)
    url = reverse('admin:accounts_schedule_posts') + "?" + urlencode({'ids': ids})
    return redirect(url)
action_schedule_post.short_description = "Запланировать публикацию поста"

class AccountAdmin(admin.ModelAdmin):
    form = AccountForm
    list_display = ['social_network', 'title']
    
    def add_view(self, request, form_url=''):
        if request.method == 'POST':
            title = request.POST.get('title', '')
            social_network = request.POST.get('social_network', '')
            url_name = f'admin:publisher_{social_network}account_add'
            
            # validate network and resolve URL safely
            if social_network not in dict(TYPE_CHOICES):
                self.message_user(
                    request,
                    "Некорректная соцсеть.",
                    level=messages.ERROR
                )
                return super().add_view(request, form_url)
            
            try:
                url = reverse(url_name)
            except NoReverseMatch:
                self.message_user(
                    request,
                    "Страница добавления для этой соцсети не найдена.",
                    level=messages.ERROR
                )
                return super().add_view(request, form_url)
 
            query = urlencode({
                '_account_title': title,
                '_account_social_network': social_network,
            })
            redirect_url = f"{url}?{query}"
            return redirect(redirect_url)
        
        return super().add_view(request, form_url)
    
    # TODO: Нормальное редактирование, опции:
    # [DONE] 1. Сохранять account -> перебрасыать на редактирование [network_base]
    # 2. Пробрассывать данные с account на [network_base] и там сохранять
    # 3. Сделать единую форму с account & [network_base] - удобнее всего!
    
    def response_change(self, request, obj):

        # Получаем имя соцсети
        social_network = obj.social_network.lower()
        # Получаем id связанной модели
        related_obj_id = obj.social_id

        # Строим URL редактирования для конкретной соцсети
        if not related_obj_id:
            self.message_user(request, "Связанный объект соцсети ещё не создан.", level=messages.WARNING)
            return super().response_change(request, obj)
        url_name = f'admin:publisher_{social_network}account_change'
        try:
            url = reverse(url_name, args=[related_obj_id])
        except Exception:
            self.message_user(request, "Страница редактирования для этой соцсети не найдена.", level=messages.ERROR)
            return super().response_change(request, obj)
        return redirect(url)

    actions = [action_schedule_post] # Регистрируем action

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path('schedule-posts/', self.admin_site.admin_view(self.schedule_posts_view), name='accounts_schedule_posts'),
        ]
        return custom + urls

    def schedule_posts_view(self, request):
        from django.db import transaction
        from publisher.planned_post import PlannedPostForm
       
        ids = request.GET.get('ids') or request.POST.get('ids')
        if not ids:
            self.message_user(request, "Не выбраны аккаунты.", level=messages.WARNING)
            return redirect(reverse('admin:publisher_account_changelist'))

        try:
            pks = [int(x) for x in ids.split(',') if x.strip()]
        except ValueError:
            self.message_user(request, "Некорректные идентификаторы аккаунтов.", level=messages.ERROR)
            return redirect(reverse('admin:publisher_account_changelist'))
        
        accounts = Account.objects.filter(pk__in=pks).select_related()
         
        # Сформируем список форм: для каждого account — PlannedPostForm
        form_objects = []
        if request.method == 'POST':
            # POST: создаём формы из incoming data
            valid = True
            created = []
            for acc in accounts:
                prefix = f'acc_{acc.pk}'
                post_form = PlannedPostForm(request.POST, prefix=prefix)

                if post_form.is_valid():
                    from publisher.scheduler import schedule_task
                        
                    try:
                        with transaction.atomic():
                            # create PlannedPost
                            pp = post_form.save(commit=False)
                            pp.account = acc
                            pp.status = 'scheduled'
                            pp.save()
                            
                            # Scheduler:
                            pp.schedule = schedule_task(pp)
                            pp.save(update_fields=['status', 'schedule'])
                            
                            created.append(pp)
                    except Exception as e:
                        self.message_user(request, f"Ошибка при планировании постов: {str(e)}", level=messages.ERROR)
                        valid = False
                else:
                    valid = False
                    form_objects.append((acc, post_form))
            if valid:
                self.message_user(request, f"Создано {len(created)} запланированных постов.")
                return redirect(reverse('admin:publisher_plannedpost_changelist'))
            # если невалидны — fallthrough: render forms with errors
        else:
            # GET: показываем пустые формы (prefilled title/user if you want)
            for acc in accounts:
                prefix = f'acc_{acc.pk}'
                pf = PlannedPostForm(prefix=prefix)
                form_objects.append((acc, pf))

        context = dict(
            self.admin_site.each_context(request),
            title="Запланировать публикации",
            form_objects=form_objects,
            ids=ids,
        )
        return render(request, 'schedule_posts.html', context)
