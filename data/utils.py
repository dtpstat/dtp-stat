import datetime
import json
import logging
import os
import re

import environ
import herepy
import pytz
import requests
from datadog import statsd
from django.contrib.gis.geos import Point
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from lxml import html
from tqdm import tqdm

from . import models
from application import utils as app_utils
from django.core.cache import cache

env = environ.Env(
    PROXY_LIST=(list, [])
)
environ.Env.read_env()
log = logging.getLogger(__name__)

def open_json(path):
    with open(path) as data_file:
        data = json.load(data_file)
    return data


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
        if key in ['1', '96', '70', '81', '83']:
        #if key in ['1', '96', '98', '100', '98', '101', '102', '104', '105', '107', '109', '110', '111', '113', '114', '116', '118', '119', '120']:
            tag_item.is_filter = True
        tag_item.save()


#@statsd.timed('dtpstat.get_geo_data')
def get_geo_data(item, dtp):
    try:
        lat, long = float(item['infoDtp']['COORD_L']), float(item['infoDtp']['COORD_W'])
    except:
        lat, long = None, None

    address_components = [
        item['infoDtp']['n_p'],
        item['infoDtp']['street'],
        item['infoDtp']['house']
    ]

    road_components = [
        item['infoDtp']['n_p'],
        item['infoDtp']['dor']
    ]
    if item['infoDtp']['km']:
        road_components.append(item['infoDtp']['km'] + " " + "км")

    if address_components[1]:
        street = address_components[1]
        address = ", ".join([x for x in address_components if x]).strip()
    elif road_components[1]:
        street = road_components[1]
        address = ", ".join([x for x in road_components if x]).strip()
    else:
        street = None
        address = None

    if address:
        dtp.address = address

    if street:
        dtp.street = street

    if item['infoDtp']['k_ul']:
        dtp.street_category = item['infoDtp']['k_ul']

    if item['infoDtp']['dor_z'] and item['infoDtp']['dor_z']!= "Не указано":
        dtp.road_category = item['infoDtp']['dor_z']

    if lat and long:
        if not dtp.point_is_verified:
            dtp.point = Point(lat, long)


def geocoder_yandex(address, kind=None):
    params = {
        "geocode": address,
        "apikey": env('YANDEX_TOKEN'),
        "format": "json"
    }
    if kind is not None:
        params['kind'] = kind

    url = "https://geocode-maps.yandex.ru/1.x"
    r = requests.get(url, params=params)

    data = {}

    try:
        json = r.json()
        if not json['response']['GeoObjectCollection']['featureMember']:
            log.error('geocoder_yandex result is empty')
            return None
        geo = json['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']

        data['lat'] = float(geo['Point']['pos'].split(" ")[1])
        data['long'] = float(geo['Point']['pos'].split(" ")[0])

        data['address'] = geo['metaDataProperty']['GeocoderMetaData']['text']

        address_components_street = [x for x in geo['metaDataProperty']['GeocoderMetaData']['Address']['Components'] if
                                     x['kind'] == "street"]
        if address_components_street:
            data['street'] = address_components_street[0]['name']


        parent_region_data = [x for x in geo['metaDataProperty']['GeocoderMetaData']['Address']['Components'] if
                              x['kind'] == "province"]
        if len(parent_region_data) > 1:
            data['parent_region'] = parent_region_data[1]['name']

        data['components'] = [x['name'] for x in geo['metaDataProperty']['GeocoderMetaData']['Address']['Components'] if
                           x['kind'] in ["locality", "area"]]

        if "Россия" in data['address']:
            region_data = [x for x in geo['metaDataProperty']['GeocoderMetaData']['Address']['Components'] if
                           (x['kind'] in ["locality"] and x['name'] != data['parent_region'])]
            if region_data:
                data['region'] = region_data[0]['name']
            else:
                region_data = [x for x in geo['metaDataProperty']['GeocoderMetaData']['Address']['Components'] if
                               (x['kind'] in ["area"] and x['name'] != data['parent_region'])]
                if region_data:
                    data['region'] = region_data[0]['name']

    except Exception as e:
        log.error('geocoder_yandex error: %s', e)

    return data if data != {} else None


def geocoder_here(address=None, coords=None):
    api_key = env('HERE_TOKEN')
    response = None

    if address:
        geocoderApi = herepy.GeocoderApi(api_key)
        response = geocoderApi.free_form(address).as_dict()
    elif coords:
        geocoderReverseApi = herepy.GeocoderReverseApi(api_key)
        response = geocoderReverseApi.retrieve_addresses(coords).as_dict()

    if response:
        return {
            'lat': response['Response']['View'][0]['Result'][0]['Location']['NavigationPosition'][0]['Latitude'],
            "long": response['Response']['View'][0]['Result'][0]['Location']['NavigationPosition'][0]['Longitude']
        }
    else:
        return None


def geocode(dtp):
    data = geocoder_yandex(dtp.full_address())
    if data:
        here_data = geocoder_here(coords=[data['lat'], data['long']])
        if here_data:
            data['lat'] = here_data['lat']
            data['long'] = here_data['long']
    return data


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


def add_participant_record(participant, dtp, vehicle=None):
    # тяжесть
    participant_severity = None
    for severity in models.Severity.objects.all():
        if participant['S_T'] and any(x in participant['S_T'].lower() for x in severity.keywords):
            participant_severity = severity
            break

    try:
        alco = int(participant['ALCO'])
        if not alco:
            alco = None
    except:
        alco = None

    participant_item = models.Participant(
        role=participant['K_UCH'] or None,
        driving_experience=participant['V_ST'] if participant['V_ST'] and int(participant['V_ST']) and int(participant['V_ST']) < 90 else None,
        health_status=participant['S_T'] or None,
        gender=participant['POL'] if participant['POL'] and participant['POL'] != "Не определен" else None,
        dtp=dtp,
        vehicle=vehicle,
        severity=participant_severity,
        gibdd_slug=participant['N_UCH'],
        alco=alco,
        absconded=participant['S_SM']
    )
    participant_item.save()

    for violation_item in participant['NPDD']:
        if violation_item != "Нет нарушений":
            violation, created = models.Violation.objects.get_or_create(
                name=violation_item
            )
            if not violation.gibdd_category:
                violation.gibdd_category = 'Основные нарушения'
                violation.save()
            participant_item.violations.add(violation)

    for violation_item in participant['SOP_NPDD']:
        if violation_item != "Нет нарушений":
            violation, created = models.Violation.objects.get_or_create(
                name=violation_item
            )
            if not violation.gibdd_category:
                violation.gibdd_category = 'Сопутствующие нарушения'
                violation.save()
            participant_item.violations.add(violation)

#@statsd.timed('dtpstat.add_participants_records')
def add_participants_records(item, dtp):
    models.Vehicle.objects.filter(participant__dtp=dtp).delete()
    dtp.participant_set.all().delete()

    for vehicle_item in item['infoDtp']['ts_info']:
        if vehicle_item.get('t_ts'):
            category, created = models.VehicleCategory.objects.get_or_create(
                name=vehicle_item['t_ts']
            )

            vehicle = models.Vehicle(
                gibdd_slug=vehicle_item['n_ts'],
                year=vehicle_item['g_v'] or None,
                brand=vehicle_item['marka_ts'] or None,
                vehicle_model=vehicle_item['m_ts'] or None,
                color=vehicle_item['color'] or None,
                category=category,
                drive=vehicle_item['r_rul'] or None,
                absconded=vehicle_item['ts_s'] or None,
                ownership_category=vehicle_item['f_sob'] or None,
                ownership=vehicle_item['o_pf'] or None,
            )
            vehicle.save()

            for damage in vehicle_item['m_pov'].split("|"):
                if damage:
                    damage_item, created = models.VehicleDamage.objects.get_or_create(
                        name=damage.strip()
                    )
                    vehicle.damages.add(damage_item)

            for malfunction in vehicle_item['t_n'].split("|"):
                if malfunction and malfunction != "Технические неисправности отсутствуют":
                    damage_item, created = models.VehicleMalfunction.objects.get_or_create(
                        name=malfunction.strip()
                    )
                    vehicle.malfunctions.add(damage_item)

            for participant in vehicle_item['ts_uch']:
                add_participant_record(participant, dtp, vehicle=vehicle)

    for participant in item['infoDtp']['uchInfo']:
        add_participant_record(participant, dtp)


#@statsd.timed('dtpstat.add_related_data')
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
        data_list = []

        for data_object in data_item['data']:
            if not any(re.search(x, data_object, re.IGNORECASE) for x in data_item['exclude']):
                new_item, created = data_item['model'].objects.get_or_create(
                    name=data_object
                )
                data_list.append(new_item)

        data_item['dtp_model'].add(*data_list)


#@statsd.timed('dtpstat.add_extra_filters')
def add_extra_filters(item, dtp):
    # severity

    if dtp.dead:
        dtp.severity = get_object_or_404(models.Severity, level=4)
    else:
        severity_levels = [x.severity.level for x in dtp.participant_set.all() if x.severity and x.severity.level]
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

    dtp.participant_categories.add(participant_categories.get("all"))

    if any("пешеход" in x.role.lower() for x in dtp_participants if x.role):
        dtp.participant_categories.add(participant_categories.get("pedestrians"))

    if any(x.lower() in dtp_participants_roles_string + dtp_vehicles_categories_string for x in ['велосипед']):
        dtp.participant_categories.add(participant_categories.get("velo"))

    if any(x.lower() in dtp_vehicles_categories_string for x in ['мотоцикл', 'мототранспорт', 'мопед', 'моторол']):
        dtp.participant_categories.add(participant_categories.get("moto"))

    if "до 16 лет" in all_tags_string:
        dtp.participant_categories.add(participant_categories.get("kids"))

    if any(x.lower() in dtp_vehicles_categories_string + all_tags_string for x in ['автобус', 'троллейбус', 'трамва']):
        dtp.participant_categories.add(participant_categories.get("public_transport"))


def update_dtp_data(dtp):
    item = dtp.data['source']
    dtp_datetime = pytz.timezone('UTC').localize(
        datetime.datetime.strptime(item['date'] + " " + item['Time'], '%d.%m.%Y %H:%M'))

    get_geo_data(item, dtp)

    dtp.datetime = dtp_datetime

    dtp.category, created = models.Category.objects.get_or_create(name=item['DTP_V']) if item['DTP_V'] else None
    dtp.light, created = models.Light.objects.get_or_create(name=item['infoDtp']['osv']) if item['infoDtp']['osv'] else None

    dtp.participants = item['K_UCH']
    dtp.injured = item['RAN']
    dtp.dead = item['POG']
    dtp.scheme = item['infoDtp']['s_dtp'] if item['infoDtp']['s_dtp'] not in ["290", "390", "490", "590", "690", "790", "890", "990"] else None
    dtp.save()

    add_participants_records(item, dtp)
    add_related_data(item, dtp)
    add_extra_filters(item, dtp)

    dtp.save()


#@statsd.timed('dtpstat.add_dtp_record')
def add_dtp_record(item):
    tag_code = item.get("tag_code")
    area_code = item.get("area_code")
    parent_code = item.get("parent_code")
    item = {key: item[key] for key in item if key not in ['tag_code', 'area_code', 'parent_code']}

    dtp_datetime = pytz.timezone('UTC').localize(datetime.datetime.strptime(item['date'] + " " + item['Time'], '%d.%m.%Y %H:%M'))

    dtp, created = models.DTP.objects.filter(
        datetime__year=dtp_datetime.year,
        datetime__month=dtp_datetime.month
    ).get_or_create(
        gibdd_slug=item['KartId'],
    )

    if area_code and parent_code:
        dtp.region = get_object_or_404(models.Region, gibdd_code=area_code, parent_region__gibdd_code=parent_code)

    dtp.gibdd_latest_check = timezone.now()

    tag = get_object_or_404(models.Tag, code=tag_code)
    dtp.tags.add(tag)

    dtp.save()

    if dtp.only_manual_edit or (dtp.region and dtp.data and dtp.data.get('source') and dtp.data.get('source') == item):
        #statsd.increment('dtpstat.add_dtp_record.update_not_needed')
        return
    else:
        # statsd.increment('dtpstat.add_dtp_record.update_started')
        dtp.gibdd_latest_change = timezone.now()
        dtp.data['source'] = item
        dtp.save()

        update_dtp_data(dtp)






#@statsd.timed('dtpstat.check_dates_from_gibdd')
def check_dates_from_gibdd():
    if env('PROXY_LIST'):
        proxies = {'http': 'http://' + env('PROXY_LIST')[0]}
    else:
        proxies = None

    r = requests.get('http://stat.gibdd.ru/', proxies=proxies)

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
            for region in tqdm(models.Region.objects.filter(level=1)):
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


def get_tags():
    tags = {}

    if env('PROXY_LIST'):
        proxies = {'http': 'http://' + env('PROXY_LIST')[0]}
    else:
        proxies = None

    r = requests.get('http://stat.gibdd.ru/', proxies=proxies)
    r = html.fromstring(r.content.decode('UTF-8'))
    scripts = r.xpath('//script')

    for script in scripts:
        if script.text and "pokComboData" in script.text:
            string = script.text
            p = re.compile(r"pokComboData = (.*?);", re.MULTILINE)
            data = json.loads(p.search(string).groups()[0])
            tags = get_tags_data(data)

    return tags


def crawl(spider_name, params=None):
    print(spider_name)
    first_dir = os.getcwd()
    os.chdir("data/parser")
    command = 'scrapy crawl ' + spider_name + ' -L INFO'
    if params:
        for key, value in params.items():
            command += ' -a ' + key + "=" + value
    print(command)
    os.system(command)
    os.chdir(first_dir)


def dates_generator(start, end, gap=0):
    dates_set = set()

    start_with_gap = start - datetime.timedelta(days=gap)
    start_with_gap = start_with_gap if start_with_gap >= datetime.date(2015, 1, 1) else start

    while start_with_gap <= end:
        start_with_gap += datetime.timedelta(days=1)
        dates_set.add(datetime.datetime(start_with_gap.year, start_with_gap.month, 1).strftime('%m.%Y'))

    return list(dates_set)


def download_success(dates, region_code, tags=False):
    region = get_object_or_404(models.Region, gibdd_code=region_code, level=1)

    for date in [datetime.datetime.strptime(x, '%m.%Y') for x in dates.split(",")]:
        download_item, created = models.Download.objects.get_or_create(
            region=region,
            date=date
        )
        download_item.last_update = timezone.now()
        if tags:
            download_item.last_tags_update = timezone.now()
        download_item.save()


def regions_crawl(downloads, tags=False):
    for region in tqdm(models.Region.objects.filter(level=1)):
        region_downloads = downloads.filter(region=region)

        if region_downloads:
            dates = sorted([x['date'] for x in region_downloads.values("date")])
            export_dates = dates_generator(start=min(dates), end=max(dates), gap=70)

            for date in export_dates:
                crawl("dtp", params={
                    "tags": str(tags),
                    "dates": ",".join([date]),
                    "region_code": str(region.gibdd_code),
                    "area_codes": ",".join([x.gibdd_code for x in region.region_set.all()])
                })

        for dtp in tqdm(models.DTP.objects.filter(severity__isnull=True)):
            update_dtp_data(dtp)

        app_utils.opendata()


def update_export_meta_data():
    for dtp in tqdm(models.DTP.objects.all()):
        dtp.data['export'] = dtp.as_dict()
        dtp.save()

    app_utils.opendata(force=True)

#@statsd.timed('dtpstat.check_dtp')
def check_dtp():
    # проверяем обновления на сайте ГИБДД
    check_dates_from_gibdd()

    # сверяем с нашей базой и, если расходится, то загружаем данные
    downloads = models.Download.objects.all()
    downloads_no_update = downloads.filter(last_update=None)

    # первым делом проверяем наличие вообще не скаченных регионов за конкретные даты
    if downloads_no_update.count() > 0:
        regions_crawl(downloads_no_update, tags=False)
        cache.clear()

    """
    # потом смотрим на архивные данные
    downloads_old_update = downloads.filter(last_update__lte=timezone.now() - datetime.timedelta(days=40))
    if downloads_old_update.count() > 0:
        region_crawl(downloads_old_update, tags=False)

    # потом смотрим на теги
    downloads_no_tags = downloads.filter(last_tags_update=None)
    elif downloads_no_tags.count() > 0:
        region_crawl(downloads_no_tags, tags=True)
    """

    app_utils.opendata()

