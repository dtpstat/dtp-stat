from django.core.management.base import BaseCommand
from data import utils
from data import models


class Command(BaseCommand):
    help = 'Tests'

    def handle(self, *args, **kwargs):
        models.DTP.objects.all().delete()
        models.Participant.objects.all().delete()
        models.Vehicle.objects.all().delete()
        models.Nearby.objects.all().delete()
        models.Weather.objects.all().delete()
        models.RoadCondition.objects.all().delete()
        models.Download.objects.all().delete()