from django.core.management.base import BaseCommand
from data import utils
from data import models
from application import models as app_models
from tqdm import tqdm


class Command(BaseCommand):
    help = 'Fixes'

    def handle(self, *args, **kwargs):
        for DTP in tqdm(models.DTP.objects.filter().iterator()):
            DTP.delete()

        for Vehicle in tqdm(models.Vehicle.objects.filter(participant__isnull=True)):
            Vehicle.delete()

        models.Download.objects.all().delete()
        app_models.OpenData.objects.all().delete()

        """
        models.Download.objects.all().delete()
        models.Participant.objects.all().delete()
        models.Vehicle.objects.all().delete()
        models.Nearby.objects.all().delete()
        models.Weather.objects.all().delete()
        models.RoadCondition.objects.all().delete()
        #models.Region.objects.all().delete()
        """