from django.utils import timezone
from . import models
from django.shortcuts import get_object_or_404
from django.contrib.gis.geos import Point, GEOSGeometry
from django.contrib.gis.db.models.functions import Distance
from django.db import transaction

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
from multiprocessing import Process
from twisted.internet import reactor, defer


import environ
env = environ.Env()


def open_json(path):
    with open(path) as data_file:
        data = json.load(data_file)
    return data


def extra_filters_data():
    # severity
    severity_levels = {
        0: {'name': 'Без пострадавших', 'keywords': ['не пострадал']},
        1: {'name': 'Легкая', 'keywords': ['разовой']},
        2: {'name': 'Средняя', 'keywords': ['амбулатор']},
        3: {'name': 'Тяжкая', 'keywords': ['стационар']},
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
        'pedestrians': "С пешеходами",
        'velo': "C велосипедистами",
        'moto': "C мотоциклистами",
        'public_transport': "C общественным транспортом",
        'kids': "C детьми"
    }

    for participant_type in participant_types.items():
        participant_type_item, created = models.ParticipantCategory.objects.get_or_create(
            slug=participant_type[0]
        )
        participant_type_item.name = participant_type[1]
        participant_type_item.save()



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
    # тяжесть
    participant_severity = None
    for severity in models.Severity.objects.all():
        if participant['S_T'] and severity.keywords[0] in participant['S_T'].lower():
            participant_severity = severity
            break

    participant_item = models.Participant(
        role=participant['K_UCH'] or None,
        driving_experience=participant['V_ST'] if participant['V_ST'] and int(participant['V_ST']) and int(participant['V_ST']) < 90 else None,
        health_status=participant['S_T'] or None,
        gender=participant['POL'] if participant['POL'] and participant['POL'] != "Не определен" else None,
        dtp=dtp,
        vehicle=vehicle,
        severity=participant_severity
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


def add_extra_filters(item, dtp):
    # severity
    severity_levels = [x.severity.level for x in dtp.participant_set.all() if x.severity]

    if severity_levels:
        dtp.severity = get_object_or_404(models.Severity, level=max(severity_levels))
    else:
        dtp.severity = get_object_or_404(models.Severity, level=1)

    # participatn categories
    dtp.participant_categories.clear()
    participant_categories = {x.slug: x.id for x in models.ParticipantCategory.objects.all()}

    dtp_participants = dtp.participant_set.all()
    dtp_participants_roles_string = ",".join([x.role.lower() for x in dtp_participants if x.role])
    dtp_vehicles_categories_string = ",".join([x.category.name for x in models.Vehicle.objects.filter(participant__in=dtp_participants) if x.category]).lower()
    all_tags_string = ";".join([x.name for x in dtp.tags.all()]).lower()

    if any("пешеход" in x.role.lower() for x in dtp_participants if x.role):
        dtp.participant_categories.add(participant_categories.get("pedestrians"))

    if any(x.lower() in dtp_participants_roles_string + dtp_vehicles_categories_string for x in ['велосипед']):
        dtp.participant_categories.add(participant_categories.get("velo"))

    if any(x.lower() in dtp_vehicles_categories_string for x in ['мотоцикл', 'мототранспорт', 'мопед', 'моторол']):
        dtp.participant_categories.add(participant_categories.get("moto"))

    if "до 16 лет" in all_tags_string:
        dtp.participant_categories.add(participant_categories.get("kids"))

    if any(x.lower() in dtp_vehicles_categories_string + all_tags_string for x in ['автобус', 'троллейбус', 'трамвай']):
        dtp.participant_categories.add(participant_categories.get("public_transport"))


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
    add_extra_filters(item, dtp)

    dtp.save()


def check_dates_from_gibdd():
    r = requests.get('http://stat.gibdd.ru/')
    r = html.fromstring(r.content.decode('UTF-8'))
    scripts = r.xpath('//script')

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

    with transaction.atomic():
        if date_data:
            for region in tqdm(models.Region.objects.all()):
                for date in date_data:
                    download_item, created = models.Download.objects.get_or_create(
                        region=region,
                        date=date
                    )


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


def crawl(spider_name, params=None):
    first_dir = os.getcwd()
    os.chdir("data/parser")
    command = 'scrapy crawl ' + spider_name
    if params:
        for key, value in params.items():
            command += ' -a ' + key + "=" + value
    print(command)
    os.system(command)
    os.chdir(first_dir)


def dates_generator(start, end):
    dates_set = set()

    while start <= end:
        start += datetime.timedelta(days=1)
        dates_set.add(datetime.datetime(start.year, start.month, 1).strftime('%m.%Y'))

    return list(dates_set)


def download_success(dates, region_code, tags=False):
    region = get_object_or_404(models.Region, gibdd_code=region_code)

    if region.level == 1:
        region_ids = [x.id for x in region.region_set.all()] + [region.id]
    else:
        region_ids = [region.id]

    for region_id in region_ids:
        for date in [datetime.datetime.strptime(x, '%m.%Y') for x in dates.split(",")]:
            download_item, created = models.Download.objects.get_or_create(
                region_id=region_id,
                date=date
            )
            download_item.base_data = True
            download_item.tags = tags
            download_item.save()


def check_dtp(tags=False):
    models.DTP.objects.all().delete()
    models.Participant.objects.all().delete()
    models.Vehicle.objects.all().delete()
    models.Nearby.objects.all().delete()
    models.Weather.objects.all().delete()
    models.RoadCondition.objects.all().delete()
    #models.Download.objects.all().delete()

    # проверяем обновления на сайте ГИБДД
    #check_dates_from_gibdd()

    # сверяем с нашей базой и, если расходится, то загружаем данные
    for region in tqdm(models.Region.objects.filter(level=1)[0:1]):
        dates = sorted([x['date'] for x in models.Download.objects.filter(region=region, base_data=False).values("date")])
        dates = dates[0:10]
        export_dates = dates_generator(start=min(dates), end=max(dates))

        crawl("dtp", params={
            "dates": ",".join(export_dates),
            "region_code": str(region.gibdd_code),
            "area_codes": ",".join([x.gibdd_code for x in region.region_set.all()])
        })


def get_region_by_request(request):
    geo = request.query_params.get('geo')

    if geo:
        pnt = GEOSGeometry('POINT(' + geo + ')')

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