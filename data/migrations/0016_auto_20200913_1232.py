# Generated by Django 3.0.4 on 2020-09-13 12:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0015_auto_20200913_1151'),
    ]

    operations = [
        migrations.AddField(
            model_name='dtp',
            name='gibdd_latest_change',
            field=models.DateTimeField(blank=True, default=None, help_text='gibdd_latest_change', null=True),
        ),
        migrations.AddField(
            model_name='dtp',
            name='gibdd_latest_check',
            field=models.DateTimeField(blank=True, default=None, help_text='gibdd_latest_check', null=True),
        ),
    ]