# Generated by Django 3.0.4 on 2020-09-13 21:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0016_auto_20200913_1232'),
    ]

    operations = [
        migrations.AddField(
            model_name='dtp',
            name='road_category',
            field=models.CharField(blank=True, db_index=True, default=None, help_text='road category', max_length=1000, null=True),
        ),
    ]
