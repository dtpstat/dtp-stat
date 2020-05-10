# Generated by Django 3.0.4 on 2020-05-10 11:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0011_auto_20200510_1110'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dtp',
            name='severity',
        ),
        migrations.AddField(
            model_name='dtp',
            name='severity',
            field=models.ForeignKey(blank=True, default=None, help_text='severity lvl', null=True, on_delete=django.db.models.deletion.SET_NULL, to='data.Severity'),
        ),
        migrations.RemoveField(
            model_name='participant',
            name='severity',
        ),
        migrations.AddField(
            model_name='participant',
            name='severity',
            field=models.ForeignKey(blank=True, default=None, help_text='severity lvl', null=True, on_delete=django.db.models.deletion.SET_NULL, to='data.Severity'),
        ),
    ]