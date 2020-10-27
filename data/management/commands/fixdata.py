from django.core.management.base import BaseCommand
from data import utils
from data import models
from application import models as app_models
from tqdm import tqdm


class Command(BaseCommand):
    help = 'Fixes'

    def handle(self, *args, **kwargs):
        for DTP in tqdm(models.DTP.objects.filter().iterator()):
            if DTP.data['source']['infoDtp']['dor_k']:
                print(DTP.data['source']['infoDtp']['dor_k'], DTP.region.name, DTP.region.parent_region.name, DTP.datetime)