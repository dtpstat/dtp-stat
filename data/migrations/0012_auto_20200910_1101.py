# Generated by Django 3.0.4 on 2020-09-10 11:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0011_dtp_street_category'),
    ]

    operations = [
        migrations.RenameField(
            model_name='dtp',
            old_name='slug',
            new_name='gibdd_slug',
        ),
    ]