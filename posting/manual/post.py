from django.db import models
from django import forms
from django.contrib import admin

class PlannedPost(models.Model):
    target = models.ForeignKey('posting.Account', on_delete=models.CASCADE, related_name='planned_posts')
    short = models.CharField(max_length=255)
    text = models.TextField()
    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_planned = models.DateTimeField()
    # сюда можно записывать id задачи в Celery/cron/whatever
    link_to_cron_task = models.CharField(max_length=255, blank=True, null=True)

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
    list_display = ('short', 'target','datetime_planned', 'datetime_created')
    formfield_overrides = {
        models.DateTimeField: {'widget': forms.DateTimeInput(attrs={'type': 'datetime-local'})}
    }