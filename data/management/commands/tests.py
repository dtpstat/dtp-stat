from django.core.management.base import BaseCommand
from data import utils
from data import models
from tqdm import tqdm


class Command(BaseCommand):
    help = 'Tests'

    def handle(self, *args, **kwargs):
        for DTP in tqdm(models.DTP.objects.all().iterator()):
            DTP.delete()
        models.Participant.objects.all().delete()
        models.Vehicle.objects.all().delete()
        models.Nearby.objects.all().delete()
        models.Weather.objects.all().delete()
        models.RoadCondition.objects.all().delete()
        models.Download.objects.all().delete()