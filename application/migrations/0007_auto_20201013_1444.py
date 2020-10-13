# Generated by Django 3.0.4 on 2020-10-13 14:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0006_briefdata'),
    ]

    operations = [
        migrations.AlterField(
            model_name='briefdata',
            name='child_death_count',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='briefdata',
            name='child_injured_count',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='briefdata',
            name='death_count',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='briefdata',
            name='dtp_count',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='briefdata',
            name='injured_count',
            field=models.PositiveIntegerField(null=True),
        ),
    ]
