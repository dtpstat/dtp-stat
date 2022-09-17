import json
import logging
import os
import re

import requests
from django.conf import settings
from lxml import html

from data.gibdd import conf as gibdd
from .tools.geocode import geocoder_yandex
from . import models

log = logging.getLogger(__name__)

def extra_filters_data():
    # severity
    severity_levels = {
        0: {'name': 'Без пострадавших (нет данных)', 'keywords': ['не пострадал']},
        1: {'name': 'Легкий', 'keywords': ['разовой', 'амбулатор']},
        3: {'name': 'Тяжёлый', 'keywords': ['стационар']},
        4: {'name': 'С погибшими', 'keywords': ['скончался']}
    }

    for item in severity_levels.items():
        severity_item, created = models.Severity.objects.get_or_create(
            level=item[0]
        )
        severity_item.name = item[1]['name']
        severity_item.keywords = item[1]['keywords']
        severity_item.save()

    # participant types
    participant_types = {
        'all': "Все участники",
        'pedestrians': "Пешеходы",
        'velo': "Велосипедисты",
        'moto': "Мотоциклисты",
        'public_transport': "Общ. транспорт",
        'kids': "Дети"
    }

    for participant_type in participant_types.items():
        participant_type_item, created = models.ParticipantCategory.objects.get_or_create(
            slug=participant_type[0]
        )
        participant_type_item.name = participant_type[1]
        participant_type_item.save()

    # get_tags
    tags = get_tags()
    for key, tag in tags.items():
        tag_item, created = models.Tag.objects.get_or_create(
            code=key
        )
        tag_item.name = tag
        if key in ['1']:
        #if key in ['1', '96', '98', '100', '98', '101', '102', '104', '105', '107', '109', '110', '111', '113', '114', '116', '118', '119', '120']:
            tag_item.is_filter = True
        tag_item.save()


def get_region(region_code, region_name, parent_region_code, parent_region_name):
    parent_region, parent_region_created = models.Region.objects.get_or_create(
        level=1,
        gibdd_code=parent_region_code
    )
    if parent_region_created:
        parent_region.name = parent_region_name
    parent_region.save()

    region, region_created = models.Region.objects.get_or_create(
        level=2,
        gibdd_code=region_code,
        parent_region=parent_region
    )
    if region_created:
        region.name = region_name
    region.save()

    if not region.ya_name or not parent_region.ya_name:
        ya_data = geocoder_yandex(parent_region_name + ", " + region_name)
        if not parent_region.ya_name and ya_data.get('parent_region'):
            parent_region.ya_name = ya_data['parent_region']

        if not region.ya_name and ya_data.get('region') and ya_data.get('region') != ya_data.get('parent_region'):
            region.ya_name = ya_data['region']

    parent_region.save()
    region.save()

    return region


def get_tags_data(data, parent_name=None):
    export_data = {}
    for item in data:
        item_text = item['text'] if not parent_name else parent_name + ", " + item['text']
        export_data[item['value']] = item_text
        if item.get('nodes'):
            export_data = {**export_data, **get_tags_data(item.get('nodes'), parent_name=item_text)}
    return export_data


def get_tags():
    tags = {}

    if settings.PROXY_LIST:
        proxies = {'http': 'http://' + settings.PROXY_LIST[0]}
    else:
        proxies = None

    r = requests.get(gibdd.STAT_URL, proxies=proxies)
    r = html.fromstring(r.content.decode('UTF-8'))
    scripts = r.xpath('//script')

    for script in scripts:
        if script.text and "pokComboData" in script.text:
            string = script.text
            p = re.compile(r"pokComboData = (.*?);", re.MULTILINE)
            data = json.loads(p.search(string).groups()[0])
            tags = get_tags_data(data)

    return tags

def load_fixtures():
    first_dir = os.getcwd()
    os.chdir("./")
    os.system('./manage.py loaddata data/fixtures/regions.json')
    os.system('./manage.py loaddata data/fixtures/pages.json')
    os.chdir(first_dir)