# Generated by Django 3.0.4 on 2020-05-10 19:50

import application.middlewares
import ckeditor.fields
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BlogPost',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(blank=True, default=django.utils.timezone.now, help_text='datetime publish', null=True)),
                ('title', models.CharField(blank=True, default=None, help_text='Post title', max_length=200, null=True)),
                ('slug', models.CharField(blank=True, db_index=True, default=None, help_text='slug', max_length=200, null=True)),
                ('text', ckeditor.fields.RichTextField(blank=True, default=None, help_text='text', null=True)),
                ('created_by', models.ForeignKey(default=application.middlewares.get_current_user, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]