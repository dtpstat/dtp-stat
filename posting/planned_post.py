from django.db import models
from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.utils import timezone
from django_q.tasks import Schedule

STATUS_CHOICES = [
    ('scheldured', 'Запланирован'),
    ('success', 'Успех'),
    ('failed', 'Катастрофа'),
]

class PlannedPost(models.Model):
    account = models.ForeignKey('posting.Account', on_delete=models.CASCADE, related_name='planned_posts')
    short = models.CharField(max_length=255)
    text = models.TextField()
    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_planned = models.DateTimeField(blank=True, null=True)
    scheduler_task_id = models.PositiveIntegerField(blank=True, null=True)
    status = models.CharField(
        max_length=10,
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
            if old.datetime_planned != self.datetime_planned and self.scheduler_task_id:
                # Переносим задачу в планировщике
                sched = Schedule.objects.get(pk=self.scheduler_task_id)
                sched.next_run = self.effective_datetime
                sched.save()
        super().save(*args, **kwargs)
        
    def delete(self, *args, **kwargs):
        if self.scheduler_task_id:
            try:
                sched = Schedule.objects.get(pk=self.scheduler_task_id)
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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.datetime_planned:
            local_dt = timezone.localtime(self.instance.datetime_planned)
            # self.fields['datetime_planned'].initial = local_dt.strftime('%Y-%m-%dT%H:%M')    
            self.initial['datetime_planned'] = local_dt.strftime('%Y-%m-%dT%H:%M')  
            
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
    list_display = ('status', 'short', 'account','datetime_planned', 'datetime_created_local')
    fields = ('account', 'short', 'text', 'datetime_planned')
    formfield_overrides = {
        models.DateTimeField: {
            'widget': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'form_class': forms.DateTimeField  # Заставляем использовать DateTimeField
        }
    }
    
    def get_readonly_fields(self, request, obj=None):
        readonly = list(super().get_readonly_fields(request, obj))
        if obj and obj.status == "success":
            # делаем все поля недоступными для редактирования
            readonly += [f.name for f in self.model._meta.fields]
        return readonly
    
    def datetime_created_local(self, obj):
        return timezone.localtime(obj.datetime_created)
    datetime_created_local.admin_order_field = 'datetime_created'  # сортировка по исходному полю
    datetime_created_local.short_description = 'Дата создания'
    
    def get_object(self, request, object_id, from_field=None):
        obj = super().get_object(request, object_id, from_field)
        request.plobj = obj
        return obj
    
    
def status_hook(task):
    # task — это объект Task из django_q
    post_id = task.args[0]  # мы в задачу передали post_id
    try:
        post = PlannedPost.objects.get(id=post_id)
    except PlannedPost.DoesNotExist:
        return
    
    if task.success:
        post.status = "success"
    else:
        post.status = "failed"
    post.save()