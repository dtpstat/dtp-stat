from django.core.management.base import BaseCommand
from application import utils
from data import models
from data import utils as data_utils
import pandas as pd
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404

from tqdm import tqdm
import json
import shutil


class Command(BaseCommand):
    help = 'fix'

    def handle(self, *args, **kwargs):

        """
        data = []
        for dtp in tqdm(models.DTP.objects.all()):
            data.append(dtp.data['source'])

        with open('test.json', 'w') as data_file:
            json.dump(data, data_file, ensure_ascii=False)
        """

        for dtp in tqdm(models.DTP.objects.filter(gibdd_slug="209684131")):
            if dtp.gibdd_slug == "209684131":
                data_utils.update_dtp_data(dtp)

        for dtp in models.DTP.objects.filter(status=False):
            pass

        #data_utils.update_export_meta_data()

