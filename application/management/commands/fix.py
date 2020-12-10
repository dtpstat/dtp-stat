from django.core.management.base import BaseCommand
from application import utils
from data import models
from data import serializers
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
        data = models.DTP.objects.filter(region__parent_region__slug='moskva')
        serializer = serializers.DTPSerializer(data, many=True)
        with open('test.json', 'w') as data_file:
            json.dump(serializer.data, data_file, ensure_ascii=False)
