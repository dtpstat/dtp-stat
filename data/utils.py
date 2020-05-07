from django.utils import timezone
from . import models
from django.shortcuts import get_object_or_404
from django.contrib.gis.geos import Point, GEOSGeometry
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D
from django.contrib.postgres.aggregates.general import StringAgg
from django.forms.models import model_to_dict

import scrapy
from scrapy.crawler import CrawlerProcess
from data.parser.dtp_parser.spiders.dtp_spider import DtpSpider

import json
import ijson
from tqdm import tqdm
import datetime
import requests
import pytz
import re
import os
from lxml import html
import pandas as pd
from scrapy.crawler import CrawlerProcess
from data.parser.dtp_parser.spiders.dtp_spider import DtpSpider

import environ
env = environ.Env()


def open_json(path):
    with open(path) as data_file:
        data = json.load(data_file)
    return data


def get_geo_data(item, dtp):
    try:
        gibdd_lat, gibdd_long = float(item['infoDtp']['COORD_L']), float(item['infoDtp']['COORD_W'])
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
        #parent_region.point = Point(geocode(parent_region.name))
        parent_region.save()

    region, created = models.Region.objects.get_or_create(
        level=2,
        gibdd_code=region_code,
        parent_region=parent_region
    )
    if created:
        region.name = region_name
        #region.point = Point(geocode(region.name + " " + parent_region.name))
        region.save()

    return region


def add_participant_record(participant, dtp, vehicle=None):
    participant_item = models.Participant(
        role=participant['K_UCH'] or None,
        driving_experience=participant['V_ST'] if participant['V_ST'] and int(participant['V_ST']) and int(participant['V_ST']) < 90 else None,
        health_status=participant['S_T'] or None,
        gender=participant['POL'] or None,
        dtp=dtp,
        vehicle=vehicle
    )
    participant_item.save()

    for violation_item in (participant['NPDD'] + participant['NPDD']):
        if violation_item != "Нет нарушений":
            violation, created = models.Violation.objects.get_or_create(
                name=violation_item
            )
            participant_item.violations.add(violation)


def add_participants_records(item, dtp):
    models.Vehicle.objects.filter(participant__dtp=dtp).delete()
    dtp.participant_set.clear()

    for vehicle_item in item['infoDtp']['ts_info']:
        if vehicle_item.get('t_ts'):
            category, created = models.VehicleCategory.objects.get_or_create(
                name=vehicle_item['t_ts']
            )

            vehicle = models.Vehicle(
                year=vehicle_item['g_v'] or None,
                brand=vehicle_item['marka_ts'] or None,
                vehicle_model=vehicle_item['m_ts'] or None,
                color=vehicle_item['color'] or None,
                category=category
            )
            vehicle.save()

            for participant in vehicle_item['ts_uch']:
                add_participant_record(participant, dtp, vehicle=vehicle)

    for participant in item['infoDtp']['uchInfo']:
        add_participant_record(participant, dtp)


def add_related_data(item, dtp):
    related_data = [
        {
            "model": models.Nearby,
            "dtp_model": dtp.nearby,
            "data": item['infoDtp']['OBJ_DTP'] + item['infoDtp']['sdor'],
            "exclude": [
                'нет объектов',
                "отсутствие",
                'иное место'
            ]
        },
        {
            "model": models.Weather,
            "dtp_model": dtp.weather,
            "data": item['infoDtp']['s_pog'],
            "exclude": []
        },
        {
            "model": models.RoadCondition,
            "dtp_model": dtp.road_conditions,
            "data": item['infoDtp']['ndu'] + [item['infoDtp']['s_pch']],
            "exclude": [
                "не установлены",
            ]
        }
    ]

    for data_item in related_data:
        data_item['dtp_model'].clear()
        for data_object in data_item['data']:
            if not any(re.search(x, data_object, re.IGNORECASE) for x in data_item['exclude']):
                new_item, created = data_item['model'].objects.get_or_create(
                    name=data_object
                )
                data_item['dtp_model'].add(new_item)


def add_dtp_record(item):
    dtp, created = models.DTP.objects.get_or_create(
        slug=item['KartId']
    )

    tag, created = models.Tag.objects.get_or_create(name=item['tag']) if item['tag'] else None
    dtp.tags.add(tag)
    dtp.datetime = pytz.timezone('UTC').localize(datetime.datetime.strptime(item['date'] + " " + item['Time'], '%d.%m.%Y %H:%M'))
    #dtp.region = get_region(item["area_code"], item["area_name"], item["region_code"], item["region_name"])
    dtp.region = get_object_or_404(models.Region, gibdd_code=item["area_code"])
    dtp.category, created = models.Category.objects.get_or_create(name=item['DTP_V']) if item['DTP_V'] else None
    dtp.light, created = models.Light.objects.get_or_create(name=item['infoDtp']['osv']) if item['infoDtp']['osv'] else None
    dtp.participants = item['K_UCH']
    dtp.injured = item['RAN']
    dtp.dead = item['POG']
    dtp.scheme = item['infoDtp']['s_dtp'] if item['infoDtp']['s_dtp'] not in ["290", "390", "490", "590", "690", "790", "890", "990"] else None
    dtp.data['gibdd_point'] = {}
    dtp.data['gibdd_point']['lat'], dtp.data['gibdd_point']['long'], dtp.data['gibdd_point']['address'], dtp.street = get_geo_data(item, dtp)
    dtp.source = "police"
    dtp.data['source'] = item
    dtp.save()

    add_participants_records(item, dtp)
    add_related_data(item, dtp)


def recording(download_item):
    models.DTP.objects.all().delete()
    models.Participant.objects.all().delete()
    models.Vehicle.objects.all().delete()
    models.Nearby.objects.all().delete()
    models.Weather.objects.all().delete()
    models.RoadCondition.objects.all().delete()
    download_item.phase = "recording"
    download_item.save()

    with open("data/data/dtp.json", 'r') as f:
        n = 0
        for item in tqdm(ijson.items(f, 'item')):
            add_dtp_record(item)
            n = n + 1
            if n == 10:
                break


def download():
    #models.DTP.objects.all().delete()
    first_dir = os.getcwd()
    os.chdir("data/parser")
    os.system('scrapy crawl dtp')
    os.chdir(first_dir)


def check_dates_from_gibdd(scripts):
    source_date_data = None
    date_data = []

    for script in scripts:
        if script.text and "dateComboData" in script.text:
            string = script.text
            p = re.compile(r"dateComboData = (.*?);", re.MULTILINE)
            m = p.search(string)
            data = m.groups()[0]
            source_date_data = json.loads(data)
            if source_date_data:
                break

    if source_date_data:
        for year in source_date_data:
            for month in year['nodes']:
                date_data.append(datetime.datetime.strptime(month['Value'].replace("MONTHS:", ""), '%m.%Y').date())

    return date_data or None


def get_tags_data(data, parent_name=None):
    export_data = {}
    for item in data:
        item_text = item['Text'] if not parent_name else parent_name + ", " + item['Text']
        export_data[item['Value']] = item_text
        if item.get('nodes'):
            export_data = {**export_data, **get_tags_data(item.get('nodes'), parent_name=item_text)}
    return export_data


def get_tags(scripts):
    tags = {}

    for script in scripts:
        if script.text and "pokComboData" in script.text:
            string = script.text
            p = re.compile(r"pokComboData = (.*?);", re.MULTILINE)
            data = json.loads(p.search(string).groups()[0])
            tags = get_tags_data(data)
            for k in ['1']:
                tags.pop(k, None)

    return tags


def check_download():
    models.DTP.objects.all().delete()

    # проверяем обновления на сайте ГИБДД
    r = requests.get('http://stat.gibdd.ru/')
    r = html.fromstring(r.content)
    scripts = r.xpath('//script')

    gibdd_actual_dates = sorted(check_dates_from_gibdd(scripts))
    tags = get_tags(scripts)

    # сверяем с нашей базой и, если расходится, то загружаем данные
    for region in tqdm(models.Region.objects.filter(level=1)[0:1]):
        print(region)
        for area in tqdm(region.region_set.all()[0:1]):
            print(area)
            if not area.actual_date or any(area.actual_date < date for date in gibdd_actual_dates):
                if area.actual_date:
                    start_date_index = min([index for index, date in enumerate(gibdd_actual_dates) if date > area.actual_date])
                    start_date_index = start_date_index - 2 if start_date_index >= 2 else 0
                    dates = gibdd_actual_dates[start_date_index:]
                else:
                    dates = gibdd_actual_dates

                process = CrawlerProcess()
                process.crawl(DtpSpider,
                              dates=dates,
                              tags=tags,
                              area=area)
                process.start()
    #
    """
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
    """

def get_region_by_request(request):
    lat = request.query_params.get('lat')
    long = request.query_params.get('long')
    region = request.query_params.get('region')

    if region:
        region = get_object_or_404(models.Region, slug=region)
        return region

    if lat and long:
        pnt = Point(float(lat), float(long))

        region = models.DTP.objects.filter(
            point__dwithin=(pnt, 1)
        ).annotate(
            distance=Distance('point', pnt)
        ).order_by('distance')[0].region

        return region


def generate_datasets():
    data = [obj.as_dict() for obj in models.DTP.objects.all()]
    with open('static/data/' + 'test.json', 'w') as data_file:
        json.dump(data, data_file, ensure_ascii=False)


def generate_datasets_geojson():
    data = [obj.as_dict() for obj in models.DTP.objects.all()]
    geo_data = { "type": "FeatureCollection", "features": [
        {"type": "Feature",
         "geometry": {"type": "Point", "coordinates": [item['point']['long'], item['point']['lat']]},
         "properties": item
         } for item in data
    ]}
    with open('static/data/' + 'test.geojson', 'w') as data_file:
        json.dump(geo_data, data_file, ensure_ascii=False)

    """
    data = list(models.DTP.objects.all().annotate(
        election_regions=StringAgg('election_item__regions__name', ordering="election_item__regions__level",
                                   delimiter=", ")
    ).values(
        'id',
        'datetime',
        'slug',
        'region__name',
        'region__parent_region__name',
        'address',
        #'point',
        'participants',
        'injured',
        'dead',
        'category__name',
        'light__name',
        'candidate__data__birthplace',
        'electoral_district',
        'election_item__election__name',
        'election_item__name',
        'election_regions',
        'election_item__date',
        'election_item__level__name',
        'election_item__stage__name',
        'election_item__type__name',
        'election_item__scheme__name',
        'gas_url',

    ))

    df = pd.DataFrame(data)
    df.to_csv('static/data/nominations.csv')
    """