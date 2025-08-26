from django.db import models
from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.utils import timezone
from django_q.tasks import Schedule, Task
from django_q.models import Success, Failure
from django.utils.html import format_html
from django.urls import reverse
from ckeditor_uploader.fields import RichTextUploadingField
from posting.socials.socials import CKEDITOR_CONFIGS
from posting.scheduler import schedule_task
import json

STATUS_CHOICES = [
    ('scheldured', 'Запланирован'),
    ('success', 'Успех'),
    ('caughtError', 'Ошибка'),
    ('uncaughtError', 'Катастрофа'),
]

class PlannedPost(models.Model):
    account = models.ForeignKey('posting.Account', on_delete=models.CASCADE, related_name='planned_posts')
    short = models.CharField(max_length=255)
    text = RichTextUploadingField(
        verbose_name='Текст',
        config_name='social_networks'
    )
    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_planned = models.DateTimeField(blank=True, null=True)
    schedule = models.ForeignKey(Schedule, on_delete=models.SET_NULL, null=True, blank=True, related_name='planned_posts')
    task = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True, blank=True, related_name='planned_posts')
    status = models.CharField(
        max_length=13,
        choices=STATUS_CHOICES,
        blank=True,
        null=True,
        verbose_name='Статус'
    )
    
    @property
    def effective_datetime(self):
        """Возвращает фактическое время публикации: либо запланированное, либо текущее"""
        return self.datetime_planned or timezone.now()
    
    def clean(self):
        super().clean()
        if self.datetime_planned and self.datetime_planned < timezone.now():
            raise ValidationError({
                'datetime_planned': "Planned time cannot be in the past!"
            })
            
    def save(self, *args, **kwargs):
        if self.pk:  # если объект уже существует
            old = PlannedPost.objects.get(pk=self.pk)
            super().save(*args, **kwargs)
            if old.datetime_planned != self.datetime_planned and self.schedule:
                # Переносим задачу в планировщике
                sched = self.schedule
                sched.next_run = self.effective_datetime
                sched.save()
        else:  # новый объект
            super().save(*args, **kwargs)
            self.status = 'scheldured'
            self.schedule = schedule_task(self)
            # self.message_user(request, "Ошибка шедулирования", level=messages.ERROR)
            super().save(update_fields=['status', 'schedule'])

    def delete(self, *args, **kwargs):
        if self.schedule:
            try:
                sched = self.schedule
                sched.delete()  # удаляем задачу из планировщика
            except Schedule.DoesNotExist:
                pass
        super().delete(*args, **kwargs)
    
    class Meta:
        ordering = ('-datetime_planned',)
        verbose_name = 'Ручной постинг'
        verbose_name_plural = 'Ручной постинг'

    def __str__(self):
        return f"Planned {self.short} to {self.account} at {self.datetime_planned}"

class PlannedPostForm(forms.ModelForm):
    class Meta:
        model = PlannedPost
        fields = ['short', 'text', 'datetime_planned']
        widgets = {
            'datetime_planned': forms.DateTimeInput(attrs={'type': 'datetime-local'})
        }
        help_texts = {
            'datetime_planned': "Оставьте пустым, чтобы опубликовать сразу."
        }
        
    class Media:
        js = ('js/planned_post_editor.js',)
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Timezones
        if self.instance and self.instance.datetime_planned:
            local_dt = timezone.localtime(self.instance.datetime_planned)    
            self.initial['datetime_planned'] = local_dt.strftime('%Y-%m-%dT%H:%M') 

        # Block CKEditor if form is read-only
        if self.instance and self.instance.status and self.instance.status != "scheldured":
            for field_name in self.fields:
                model_field = self._meta.model._meta.get_field(field_name)
                if isinstance(model_field, RichTextUploadingField):
                    # делаем CKEditor disabled
                    self.fields[field_name].widget.attrs['disabled'] = True
        
        # сериализуем конфиги в JSON и кладём в data-атрибут textarea
        self.fields['text'].widget.attrs['data-ckeditor-configs'] = json.dumps(CKEDITOR_CONFIGS)
            
    def clean_datetime_planned(self):
        dt = self.cleaned_data.get('datetime_planned')
        if dt is None:
            return dt
        # Конвертируем локальное время в timezone-aware
        if timezone.is_naive(dt):
            dt = timezone.make_aware(dt, timezone.get_current_timezone())
        if dt < timezone.now():
            raise forms.ValidationError("Запланированное время не может быть в прошлом")
        return dt    

class PlannedPostAdmin(admin.ModelAdmin):
    form = PlannedPostForm 
    list_display = ('short','account', 'clickable_status', 'datetime_planned', 'datetime_created_local')
    fields = ('short', 'account', "clickable_status", 'text', 'datetime_planned')
    readonly_fields = ('clickable_status',)
    formfield_overrides = {
        models.DateTimeField: {
            'widget': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'form_class': forms.DateTimeField  # Заставляем использовать DateTimeField
        }
    }
    
    def clickable_status(self, obj):
        
        print(f"Task: {obj.task}")
        
        if not obj.task:
            return obj.get_status_display()
        
        if Success.objects.filter(id=obj.task.id).exists():
            url = reverse("admin:django_q_success_change", args=[obj.task.id])
        elif Failure.objects.filter(id=obj.task.id).exists():
            url = reverse("admin:django_q_failure_change", args=[obj.task.id])
        else:
            return obj.get_status_display()
        
        return format_html('<b><a href="{}">{}</a></b>', url, obj.get_status_display())

    clickable_status.short_description = "Status"
    
    def get_readonly_fields(self, request, obj=None):
        readonly = list(super().get_readonly_fields(request, obj))
        if obj and obj.status != "scheldured":
            # добавляем все поля кроме RichTextUploadingField
            readonly += [
                f.name for f in self.model._meta.fields
                if not isinstance(f, RichTextUploadingField)
            ]
        return readonly
    
    def datetime_created_local(self, obj):
        return timezone.localtime(obj.datetime_created)
    datetime_created_local.admin_order_field = 'datetime_created'  # сортировка по исходному полю
    datetime_created_local.short_description = 'Дата создания'
    
    def get_object(self, request, object_id, from_field=None):
        obj = super().get_object(request, object_id, from_field)
        request.plobj = obj
        return obj