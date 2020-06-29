from django.contrib.gis.geos import Point, GEOSGeometry
from django.contrib.gis.db.models.functions import Distance
from data import models as data_models
from application import models
from django.shortcuts import get_object_or_404, render
from django.db.models import Sum

import json
import calendar
import os
import shutil
from tqdm import tqdm
import pandas as pd


def get_region_by_request(request):
    geo = request.query_params.get('geo')

    if geo:
        pnt = GEOSGeometry('POINT(' + geo + ')')

        region = data_models.DTP.objects.filter(
            point__dwithin=(pnt, 1)
        ).annotate(
            distance=Distance('point', pnt)
        ).order_by('distance')[0].region

        return region


def opendata():
    # get russia dataset
    latest_download = data_models.Download.objects.filter(base_data=True).latest('date')
    latest_opendata = models.OpenData.objects.filter(region=None).last()

    if latest_opendata and latest_opendata.date == latest_download.date:
        pass
    else:
        data = []
        for obj in tqdm(data_models.DTP.objects.select_related(
                'region', 'category', 'light', 'severity'
        ).prefetch_related(
            'nearby', 'weather', 'tags', 'participant_categories', 'road_conditions'
        ).filter(
            datetime__date__lte=latest_download.date.replace(day=calendar.monthrange(latest_download.date.year, latest_download.date.month)[1]),
            #tags__code='96',
            datetime__year=2019
        ).iterator()):
            data.append(obj.as_dict())

        geo_data = {"type": "FeatureCollection", "features": [
            {"type": "Feature",
             "geometry": {"type": "Point", "coordinates": [item['point']['long'], item['point']['lat']]},
             "properties": item
             } for item in data
        ]}

        file_name = 'russia.geojson'
        path = 'media/opendata/'
        with open(path + file_name, 'w') as data_file:
            json.dump(geo_data, data_file, ensure_ascii=False)

        shutil.make_archive(path + file_name, 'zip', path, file_name)

        latest_opendata, created = models.OpenData.objects.get_or_create(
            region=None
        )
        latest_opendata.date = latest_download.date
        latest_opendata.file_size = os.stat(path + file_name + ".zip").st_size
        latest_opendata.save()

    """
    for region in data_models.Region.objects.filter(level=1, gibdd_code='45'):
        downloads = region.download_set.filter(base_data=True)
        if downloads:
            latest_download = downloads.latest('date')

            latest_opendata = region.opendata_set.last()

            if latest_opendata and latest_opendata.date == latest_download.date:
                continue

            data = [obj.as_dict() for obj in data_models.DTP.objects.filter(
                region__in=region.region_set.all(),
                datetime__date__lte=latest_download.date.replace(
                                day=calendar.monthrange(latest_download.date.year, latest_download.date.month)[1]
                            )
            )]

            geo_data = {"type": "FeatureCollection", "features": [
                {"type": "Feature",
                 "geometry": {"type": "Point", "coordinates": [item['point']['long'], item['point']['lat']]},
                 "properties": item
                 } for item in data
            ]}

            path = 'media/opendata/' + region.slug + '.geojson'
            with open(path, 'w') as data_file:
                json.dump(geo_data, data_file, ensure_ascii=False)

            latest_opendata, created = models.OpenData.objects.get_or_create(
                region=region
            )
            latest_opendata.date = latest_download.date
            latest_opendata.file_size = os.stat(path).st_size
            latest_opendata.save()
    """


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


def soc_risk():
    data = data_models.DTP.objects.filter(datetime__year__in=[2018,2019])

    data = data.values('region__parent_region__name', "datetime__year").annotate(dead_count=Sum('dead'))

    df = pd.DataFrame(data)
    df.to_csv('static/soc_risk.csv')


def get_moderator_feedback(request):
    user = request.user
    if user.is_superuser:
        feedback = models.Feedback.objects.all()
    else:
        moderator = get_object_or_404(models.Moderator, user=request.user)
        feedback = models.Feedback.objects.filter(dtp__region__parent_region__moderator=moderator)

    return feedback


def is_moderator(user):
    try:
        get_object_or_404(models.Moderator, user=user)
        return True
    except:
        return False