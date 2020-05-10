from django.contrib import admin
from . import models


@admin.register(models.BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'title', 'created_by')
    ordering = ('created_at',)


@admin.register(models.Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug')
    ordering = ('title',)
