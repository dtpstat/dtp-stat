# Generated by Django 3.0.4 on 2020-04-05 14:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0005_auto_20200401_1202'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, db_index=True, default=None, help_text='name', max_length=1000, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='dtp',
            name='tags',
            field=models.ManyToManyField(db_index=True, help_text='Tags', to='data.Tag'),
        ),
    ]