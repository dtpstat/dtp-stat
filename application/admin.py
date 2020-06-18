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


@admin.register(models.Moderator)
class ModeratorAdmin(admin.ModelAdmin):
    list_display = ('user', 'regions_list')
    filter_horizontal = ('regions',)
    search_fields = ('user__username', 'region__name')
    ordering = ('created_at',)

    list_select_related = (
        'user',
    )


@admin.register(models.OpenData)
class OpenDataAdmin(admin.ModelAdmin):
    list_display = ('region', 'date')
