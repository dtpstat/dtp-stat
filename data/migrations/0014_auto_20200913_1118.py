# Generated by Django 3.0.4 on 2020-09-13 11:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0013_auto_20200913_1052'),
    ]

    operations = [
        migrations.AddField(
            model_name='participant',
            name='absconded',
            field=models.CharField(blank=True, default=None, help_text='Participant absconded', max_length=1000, null=True),
        ),
        migrations.AddField(
            model_name='participant',
            name='alco',
            field=models.IntegerField(blank=True, default=None, help_text='Participant alco', null=True),
        ),
    ]