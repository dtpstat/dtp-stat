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
    list_display = ('datetime',)

    formfield_overrides = {
        JSONField: {'widget': PrettyJSONWidget},
    }