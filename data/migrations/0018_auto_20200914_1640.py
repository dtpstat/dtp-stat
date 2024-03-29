# Generated by Django 3.0.4 on 2020-09-14 16:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0017_dtp_road_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dtp',
            name='nearby',
            field=models.ManyToManyField(blank=True, db_index=True, help_text='nearby objects', to='data.Nearby'),
        ),
        migrations.AlterField(
            model_name='dtp',
            name='participant_categories',
            field=models.ManyToManyField(blank=True, db_index=True, help_text='ParticipantCategory', to='data.ParticipantCategory'),
        ),
        migrations.AlterField(
            model_name='dtp',
            name='road_conditions',
            field=models.ManyToManyField(blank=True, db_index=True, help_text='Road conditions', to='data.RoadCondition'),
        ),
        migrations.AlterField(
            model_name='dtp',
            name='tags',
            field=models.ManyToManyField(blank=True, db_index=True, help_text='Tags', to='data.Tag'),
        ),
        migrations.AlterField(
            model_name='dtp',
            name='weather',
            field=models.ManyToManyField(blank=True, db_index=True, help_text='weather', to='data.Weather'),
        ),
        migrations.AlterField(
            model_name='participant',
            name='violations',
            field=models.ManyToManyField(blank=True, db_index=True, help_text='violations', to='data.Violation'),
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='damages',
            field=models.ManyToManyField(blank=True, help_text='damages', to='data.VehicleDamage'),
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='malfunctions',
            field=models.ManyToManyField(blank=True, help_text='malfunctions', to='data.VehicleMalfunction'),
        ),
    ]
