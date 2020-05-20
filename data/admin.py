from django.contrib import admin
from data import models

from django.contrib.postgres.fields import JSONField
from django.forms import widgets

import json


class PrettyJSONWidget(widgets.Textarea):
    def format_value(self, value):
        try:
            value = json.dumps(json.loads(value), indent=2, ensure_ascii=False)
            row_lengths = [len(r) for r in value.split('\n')]
            self.attrs['rows'] = min(max(len(row_lengths) + 2, 10), 30)
            self.attrs['cols'] = min(max(max(row_lengths) + 2, 40), 120)
            return value
        except Exception as e:
            pass


@admin.register(models.DTP)
class DTPAdmin(admin.ModelAdmin):
    list_display = ('datetime', 'category', 'region')
    raw_id_fields = ('region',)
    search_fields = ('region__name',)
    date_hierarchy = 'datetime'
    filter_horizontal = ('weather', 'nearby', 'road_conditions', 'tags', 'participant_categories')

    formfield_overrides = {
        JSONField: {'widget': PrettyJSONWidget},
    }


@admin.register(models.Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('name', 'level',)
    search_fields = ('name',)
    raw_id_fields = ('parent_region',)
    ordering = ('level', 'name')
    list_filter = ('level',)


@admin.register(models.Download)
class DownloadAdmin(admin.ModelAdmin):
    list_display = ('region', 'date', 'base_data', 'tags')
    raw_id_fields = ('region',)
    search_fields = ('region__name',)
    ordering = ('-date', 'region__name')
    date_hierarchy = 'date'
    list_filter = ('base_data', 'tags',)

    list_select_related = (
        'region',
    )
