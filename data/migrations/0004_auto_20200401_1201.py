# Generated by Django 3.0.4 on 2020-04-01 12:01

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0003_auto_20200330_2350'),
    ]

    operations = [
        migrations.RenameField(
            model_name='vehicle',
            old_name='car_model',
            new_name='vehicle_model',
        ),
        migrations.AlterField(
            model_name='dtp',
            name='data',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, help_text='extra data', null=True),
        ),
    ]