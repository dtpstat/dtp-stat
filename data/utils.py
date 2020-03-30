from django.utils import timezone
from . import models
from django.shortcuts import get_object_or_404
from django.contrib.gis.geos import Point

import json
import ijson
from tqdm import tqdm
import datetime
import requests

import environ
env = environ.Env()


def open_json(path):
    with open(path) as data_file:
        data = json.load(data_file)
    return data


def download(download_item):
    download_item.phase = "downloading"
    download_item.save()

    pass


def get_geo_data(item, dtp):
    try:
        gibdd_lat, gibdd_long = float(item['infoDtp']['COORD_W']), float(item['infoDtp']['COORD_L'])
    except:
        gibdd_lat, gibdd_long = None, None

    address_components = [
        item['infoDtp']['n_p'],
        item['infoDtp']['street'],
        item['infoDtp']['house']
    ]

    road_components = [
        item['infoDtp']['n_p'],
        item['infoDtp']['dor']
    ]

    if address_components[1]:
        street, created = models.Street.objects.get_or_create(name=address_components[1])
        gibdd_address = ", ".join([x for x in address_components if x]).strip()
    elif road_components[1]:
        street, created = models.Street.objects.get_or_create(name=road_components[1])
        gibdd_address = ", ".join([x for x in address_components if x]).strip()
    else:
        street = None
        gibdd_address = None

    return gibdd_lat, gibdd_long, gibdd_address, street


def geocode(address):
    url = "https://geocode.search.hereapi.com/v1/geocode"
    headers = {
        "Authorization": "Bearer " + env('HERE_TOKEN')
    }
    payload = {
        "q": address
    }
    response = requests.get(url, params=payload, headers=headers)
    try:
        return response.json().get('items')[0]['access'][0]['lat'], response.json().get('items')[0]['access'][0]['long']
    except:
        pass


def get_region(region_code, region_name, parent_region_code, parent_region_name):
    parent_region, created = models.Region.objects.get_or_create(
        level=1,
        gibdd_code=parent_region_code
    )
    if created:
        parent_region.name = parent_region_name
        parent_region.point = Point(geocode(parent_region.name))
        parent_region.save()

    region, created = models.Region.objects.get_or_create(
        level=2,
        gibdd_code=region_code,
        parent_region=parent_region
    )
    if created:
        region.name = region_name
        region.point = Point(geocode(region.name + " " + parent_region.name))
        region.save()

    return region


def add_dtp_record(item):
    dtp, created = models.DTP.objects.get_or_create(
        slug=item['KartId']
    )
    dtp.datetime = datetime.datetime.strptime(item['date'] + " " + item['Time'], '%d.%m.%Y %H:%M')
    dtp.region = get_region(item["oktmo_code"], item["area_name"], item["parent_region_code"], item["parent_region_name"])
    dtp.category, created = models.Category.objects.get_or_create(name=item['DTP_V'])
    dtp.participants = item['K_UCH']
    dtp.injured = item['RAN']
    dtp.dead = item['POG']
    dtp.scheme = item['infoDtp']['s_dtp'] if item['infoDtp']['s_dtp'] not in ["290", "390", "490", "590", "690", "790", "890", "990"] else None
    dtp.data['gibdd'] = {}
    dtp.data['gibdd']['lat'], dtp.data['gibdd']['long'], dtp.data['gibdd']['address'], dtp.street = get_geo_data(item, dtp)
    print(dtp.data['gibdd'])
    dtp.data['source'] = item
    dtp.save()




    #mvc_item.participant_set.clear()

    #return mvc_item


def recording(download_item):
    download_item.phase = "recording"
    download_item.save()

    with open("data/data/dtp.json", 'r') as f:
        for item in tqdm(ijson.items(f, 'item')):
            add_dtp_record(item)
            break


def check_download():
    download_item, created = models.Download.objects.filter(
        datetime__month=timezone.now().month,
        datetime__year=timezone.now().year,
    ).get_or_create()

    if created or download_item.phase == "downloading":
        download_item.datetime = timezone.now()
        download_item.save()

        download(download_item)
        recording(download_item)

    elif download_item.phase == "recording":
        recording(download_item)

    elif download_item.phase == "done":
        return

    #download_item.phase = "done"
    download_item.save()

