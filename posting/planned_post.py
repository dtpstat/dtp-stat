from django.db import models
from django import forms
from django.contrib import admin

from django.utils.timezone import localtime

STATUS_CHOICES = [
    ('scheldured', 'Запланирован'),
    ('success', 'Успех'),
    ('failed', 'Катастрофа'),
]

class PlannedPost(models.Model):
    target = models.ForeignKey('posting.Account', on_delete=models.CASCADE, related_name='planned_posts')
    short = models.CharField(max_length=255)
    text = models.TextField()
    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_planned = models.DateTimeField()
    scheduler_task_id = models.PositiveIntegerField(blank=True, null=True)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        blank=True,
        null=True,
        verbose_name='Статус'
    )
    
    class Meta:
        ordering = ('-datetime_planned',)
        verbose_name = 'Ручной постинг'
        verbose_name_plural = 'Ручной постинг'

    def __str__(self):
        return f"Planned {self.short} to {self.target} at {self.datetime_planned}"

class PlannedPostForm(forms.ModelForm):
    class Meta:
        model = PlannedPost
        fields = ['short', 'text', 'datetime_planned']
        widgets = {
            'datetime_planned': forms.DateTimeInput(attrs={'type': 'datetime-local'})
        }

class PlannedPostAdmin(admin.ModelAdmin):
    list_display = ('status', 'short', 'target','datetime_planned', 'datetime_created_local')
    formfield_overrides = {
        models.DateTimeField: {'widget': forms.DateTimeInput(attrs={'type': 'datetime-local'})}
    }
    
    def datetime_created_local(self, obj):
        return localtime(obj.datetime_created)
    datetime_created_local.admin_order_field = 'datetime_created'  # сортировка по исходному полю
    datetime_created_local.short_description = 'Дата создания'
    
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
