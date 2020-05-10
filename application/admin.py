from django.contrib import admin
from . import models

# Register your models here.
@admin.register(models.BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'title', 'created_by')
    ordering = ('created_at',)
