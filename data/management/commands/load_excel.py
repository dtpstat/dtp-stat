from django.core.management.base import BaseCommand
from data import utils
from application import utils as appUtils
import json
from data import models

class Command(BaseCommand):
    help = 'Load dtps from excel file'

    def handle(self, *args, **kwargs):
        i = 0
        a = 0
        with open('./excel/2021-09-25.gibdd.json') as json_file:
            data = json.load(json_file)
        for item in data:
            if models.DTP.objects.filter(gibdd_slug=item['KartId']).exists():
                print(i, "skip")
            else:
                utils.add_dtp_record(item)
                print(i, "add")  
                a += 1          
            i += 1
        print("done")
        print(a, "added")