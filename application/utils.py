import calendar
import json
import logging
import os
import shutil
import requests
import datetime

import pandas as pd
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import GEOSGeometry, Point
from django.contrib.gis.measure import D
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404, render
from tqdm import tqdm

from application import models
from data import models as data_models
from data import utils as data_utils

from django.conf import settings

log = logging.getLogger(__name__)


def get_region_by_center_point(center_point):
    """
    принимает координаты в виде строки в формате 'долгота широта'
    например: '37.64 55.76'
    """
    region = None

    if center_point:
        if "," not in center_point:
            # проверяем координаты через Яндекс
            ya_data = data_utils.geocoder_yandex(center_point)
            if ya_data and ya_data.get('region') == ya_data.get('parent_region'):
                ya_data_district = data_utils.geocoder_yandex(center_point, kind='district')
                if ya_data_district:
                    ya_data = ya_data_district
            log.debug('ya_data: %s', ya_data)
            parent_region = None
            if ya_data and ya_data.get("address"):
                parent_region = data_models.Region.objects.filter(Q(name=ya_data.get('parent_region')) | Q(ya_name=ya_data.get('parent_region'))).first()
                log.debug('parent_region: %s', parent_region)

                if parent_region:
                    region = data_models.Region.objects.filter(Q(parent_region=parent_region) & (Q(name=ya_data.get('region')) | (Q(ya_name__isnull=False) & Q(ya_name=ya_data.get('region'))))).first()
                    log.debug('region_by_region_name: %s %s', region, ya_data.get('region'))

                    if not region:
                        region_name_from_address = ya_data.get('address').split(',')[-1]
                        region = data_models.Region.objects.filter(parent_region=parent_region, name=region_name_from_address).first()
                        log.debug('region_by_address: %s %s', region, region_name_from_address)

                        if not region:
                            for component in ya_data.get('components', []):
                                region = data_models.Region.objects.filter(Q(parent_region=parent_region) & ((Q(name=component) | Q(ya_name=component)))).first()
                                log.debug('region_by_component: %s %s', region, component)
                                if region:
                                    break
                if not region:
                    log.error('Region not found in ya_data; parent_region: %s ya_data.region: %s component: %s' % (parent_region, ya_data.get('region'), ','.join(ya_data.get('components'))))

            # смотреть внутри полигонов osm


            # проверяем координаты через ближайшие ДТП
            if not region:
                point = GEOSGeometry('POINT(' + center_point + ')')
                nearest_dtps = data_models.DTP.objects.all()

                for dist in [0.1, 0.5, 1, 5, 10, 25, 50, 75]:
                    nearest_dtps = nearest_dtps.filter(
                        point__dwithin=(point, dist)
                    )

                    if nearest_dtps.count() > 4:
                        nearest_dtps = nearest_dtps.annotate(
                            distance=Distance('point', point)
                        )
                        dtps = [x.region.id for x in nearest_dtps.order_by('distance')[0:5]]
                        region_id = max(set(dtps), key=dtps.count)
                        region = get_object_or_404(data_models.Region, id=region_id)
                        break

    return region


def opendata(region=None, force=False):
    if region:
        active_region_ids = [region.id]
    else:
        active_region_ids = data_models.Download.objects.filter(last_update__isnull=False).values('region').distinct()

    for region_id in tqdm(active_region_ids):
        region = get_object_or_404(data_models.Region, id=region_id['region'])
        latest_download = region.download_set.filter(last_update__isnull=False).latest('date')
        latest_opendata, created = models.OpenData.objects.get_or_create(
            region=region
        )

        if latest_opendata.date == latest_download.date and not force:
            continue

        data = []

        for obj in data_models.DTP.objects.filter(
                region__in=region.region_set.all(),
                datetime__date__lte=latest_download.date.replace(
                    day=calendar.monthrange(latest_download.date.year, latest_download.date.month)[1]
                )
        ):
            if not obj.data.get('export'):
                obj.data['export'] = obj.as_dict()
            data.append(obj.data['export'])

        export_opendata(data, region.slug, latest_download, latest_opendata)

    """
    latest_download = data_models.Download.objects.all().latest('date')
   
    if models.OpenData.objects.filter(date=latest_download.date, region__isnull=False).count() == data_models.Region.objects.filter(level=1, is_active=True).count():
        latest_opendata, created = models.OpenData.objects.get_or_create(
            region=None
        )

        if latest_opendata.date == latest_download.date and not force:
            return
        else:
            data = [obj.data['export'] for obj in data_models.DTP.objects.filter(
                datetime__date__lte=latest_download.date.replace(
                    day=calendar.monthrange(latest_download.date.year, latest_download.date.month)[1]
                )
            )]

            export_opendata(data, "russia", latest_download, latest_opendata)
    """

def export_opendata(data, region_slug, latest_download, latest_opendata):

    geo_data = {"type": "FeatureCollection", "features": [
        {"type": "Feature",
         "geometry": {"type": "Point", "coordinates": [item['point']['long'], item['point']['lat']]},
         "properties": item
         } for item in tqdm(data)
    ]}

    path = 'media/opendata/' + region_slug + '.geojson'
    with open(path, 'w') as data_file:
        json.dump(geo_data, data_file, ensure_ascii=False)

    print(settings.BASE_DIR)
    if region_slug == "russia":
        shutil.make_archive(region_slug + '.geojson', 'zip', settings.BASE_DIR + '/media/opendata/')

    latest_opendata.date = latest_download.date
    latest_opendata.file_size = os.stat(path).st_size
    latest_opendata.save()



def generate_datasets_geojson():
    data = [obj.as_dict() for obj in data_models.DTP.objects.all()]
    geo_data = { "type": "FeatureCollection", "features": [
        {"type": "Feature",
         "geometry": {"type": "Point", "coordinates": [item['point']['long'], item['point']['lat']]},
         "properties": item
         } for item in data
    ]}

    with open('static/data/' + 'test.geojson', 'w') as data_file:
        json.dump(geo_data, data_file, ensure_ascii=False)


def load_data():
    data = data_models.Region.objects.all()

    data = data.values('name', 'parent_region__name','gibdd_code', "ya_name", "slug")

    df = pd.DataFrame(data)
    df.to_csv('static/regions.csv', index=False)


def get_moderator_tickets(request):
    user = request.user
    if user.is_superuser:
        tickets = models.Ticket.objects.all()
    else:
        moderator = get_object_or_404(models.Moderator, user=request.user)
        tickets = models.Ticket.objects.filter(dtp__region__parent_region__moderator=moderator)

    return tickets


def is_moderator(user):
    try:
        get_object_or_404(models.Moderator, user=user)
        return True
    except:
        if user.is_superuser:
            return True

    return False



