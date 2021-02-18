
from django.core.management.base import BaseCommand
from data import utils
from data import models
from application import models as app_models
from tqdm import tqdm


class Command(BaseCommand):
    help = 'Fixes'

    def handle(self, *args, **kwargs):
        import json
        with open("media/mapdata/tomskaia-oblast_2020.json") as data_file:
            data = json.load(data_file)

        print(len([x for x in data if (x['region_slug'] == "tomsk" and x['datetime'].startswith("2020-12"))]))
