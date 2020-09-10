# Generated by Django 3.0.4 on 2020-08-21 16:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0010_delete_geo'),
    ]

    operations = [
        migrations.AddField(
            model_name='dtp',
            name='street_category',
            field=models.CharField(blank=True, db_index=True, default=None, help_text='street category', max_length=1000, null=True),
        ),
    ]
