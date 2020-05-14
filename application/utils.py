from django.contrib.gis.geos import Point, GEOSGeometry
from django.contrib.gis.db.models.functions import Distance
from data import models as data_models
from application import models

import json
import calendar
import os


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
    for region in data_models.Region.objects.filter(level=1):
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