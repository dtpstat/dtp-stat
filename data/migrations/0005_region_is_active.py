# Generated by Django 3.0.4 on 2020-07-03 16:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0004_auto_20200703_1047'),
    ]

    operations = [
        migrations.AddField(
            model_name='region',
            name='is_active',
            field=models.BooleanField(default=True, help_text='last_tags_update'),
        ),
    ]