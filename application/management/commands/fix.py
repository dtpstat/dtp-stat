from django.core.management.base import BaseCommand
from application import utils
from data import models
from data import utils as data_utils
import pandas as pd
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404

from tqdm import tqdm
import json
import glob
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

        data = list(models.DTP.objects.filter(region__slug='barnaul').extra(select={'export':"data->>'export'"}).values('export'))
        print(data[0:3])
        geo_data = {"type": "FeatureCollection", "features": [
            {"type": "Feature",
             "geometry": {"type": "Point", "coordinates": [item['point']['long'], item['point']['lat']]},
             "properties": item
             } for item in tqdm(data)
        ]}

        path = 'media/opendata/test.geojson'
        with open(path, 'w') as data_file:
            json.dump(geo_data, data_file, ensure_ascii=False)
        """
        result = [] 
        for f in glob.glob("*.geojson"):
            if "russia" not in f:
                with open(f, "rb") as infile:
                    result.append(json.load(infile))

        with open("merged_file.geojson", "wb") as outfile:
            json.dump(result, outfile)
        """
        #data_utils.update_export_meta_data()

