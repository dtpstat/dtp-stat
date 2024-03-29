from django.contrib import admin
from django.contrib.admin import SimpleListFilter

from data import models
from django.db.models import Q

from django.db.models import JSONField
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


class YanameListFilter(admin.SimpleListFilter):

    title = 'Has ya_name'
    parameter_name = 'has_ya_name'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Yes'),
            ('no',  'No'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(ya_name__isnull=False).exclude(ya_name='')
        if self.value() == 'no':
            return queryset.filter(Q(ya_name__isnull=True) | Q(ya_name__exact=''))


@admin.register(models.Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('role', 'gender', 'severity')
    search_fields = ('dtp__gibdd_slug',)
    raw_id_fields = ('vehicle', 'dtp',)


class RegionFilter(SimpleListFilter):
    title = 'Region'
    parameter_name = 'region'

    def lookups(self, request, model_admin):
        regions = models.Region.objects.filter(level=1).order_by('name')
        return [(c.id, c.name) for c in regions]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(region__parent_region=self.value())
        return queryset


@admin.register(models.DTP)
class DTPAdmin(admin.ModelAdmin):
    list_display = ('gibdd_slug', 'region', 'datetime', 'gibdd_latest_change', 'gibdd_latest_check')
    raw_id_fields = ('region',)
    search_fields = ('region__name', 'region__parent_region__name', 'gibdd_slug')
    date_hierarchy = 'datetime'
    filter_horizontal = ('weather', 'nearby', 'road_conditions', 'tags', 'participant_categories')
    list_filter = ('point_is_verified', 'status', 'gibdd_latest_check', 'gibdd_latest_change', RegionFilter)

    formfield_overrides = {
        JSONField: {'widget': PrettyJSONWidget},
    }


@admin.register(models.Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent_region', 'level', 'ya_name')
    search_fields = ('name',)
    raw_id_fields = ('parent_region',)
    ordering = ('level', 'name')
    list_filter = ('level', YanameListFilter,)


@admin.register(models.Download)
class DownloadAdmin(admin.ModelAdmin):
    list_display = ('region', 'date', 'last_update', 'last_tags_update')
    raw_id_fields = ('region',)
    search_fields = ('region__name',)
    ordering = ('-date', 'region__name')
    date_hierarchy = 'date'
    list_filter = ('last_update', )

    list_select_related = (
        'region',
    )


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(models.Severity)
class SeverityAdmin(admin.ModelAdmin):
    list_display = ('name','description')

    formfield_overrides = {
        JSONField: {'widget': PrettyJSONWidget},
    }

@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name','code', 'is_filter')
    search_fields = ('name','code',)
    list_filter = ('is_filter',)

@admin.register(models.Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('gibdd_slug','vehicle_model', 'year', 'brand','ownership')
    search_fields = ('brand','year',)
    list_filter = ('year', 'brand')
