
from django.core.management.base import BaseCommand
from data import utils
from data import models
from application import models as app_models
from application import utils as app_utils
from tqdm import tqdm


class Command(BaseCommand):
    help = 'Fixes'

    def handle(self, *args, **kwargs):
        #for download in tqdm(models.Download.objects.filter(last_update__isnull=False)):
        #    utils.check_deleted_dtp(download)
        app_utils.mapdata(region_slug="saratovskaia-oblast")

