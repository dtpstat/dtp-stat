# Generated by Django 3.0.4 on 2021-08-10 19:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0018_auto_20200914_1640'),
    ]

    operations = [
        migrations.AddField(
            model_name='severity',
            name='description',
            field=models.CharField(blank=True, default=None, help_text='description', max_length=1000, null=True),
        ),
    ]