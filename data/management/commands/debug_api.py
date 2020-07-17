import json
import pprint
from ast import literal_eval

import requests
from django.core.management.base import BaseCommand

from data import utils


class Command(BaseCommand):
    help = 'Download dtp'

    def add_arguments(self, parser):
        parser.add_argument('date')
        parser.add_argument('region_code')
        parser.add_argument('area_code')
        parser.add_argument('tag_code')
        parser.add_argument(
            '--full',
            action='store_true',
            help='Show full api result',
        )

    def handle(self, *args, **options):
        payload = dict()
        payload_data = '{"date": ["MONTHS:%s"], "ParReg": %s, "order": { "type":"1", "fieldName":"dat" }, "reg": %s, "ind": %s, "st": 1, "en": "10000",}' % (options['date'], options['region_code'], options['area_code'], options['tag_code'])
        payload["data"] = payload_data
        print(payload)
        r = requests.post("http://stat.gibdd.ru/map/getDTPCardData", json=payload)

        result = r.json()
        data = literal_eval(result['data'])

        print("RegName: %s countCard: %s dateName: %s pokName: %s" % (data['RegName'], data['countCard'], data['dateName'], data['pokName']))

        if options['full']:
            pprint.pprint(data)
