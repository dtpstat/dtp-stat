from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.pagination import LimitOffsetPagination
import django_filters.rest_framework
from rest_framework.decorators import action, api_view

from django.db.models import Sum, Q
from django.shortcuts import get_object_or_404, render, redirect, reverse, HttpResponseRedirect

from data import models as data_models
from data import serializers as data_serializers

from application import utils, filters as data_filters
from application import models
from django.utils import timezone
from django.templatetags.static import static
from django.conf import settings

from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

import calendar
import datetime
import os
import json


class CacheMixin(object):
    cache_timeout = 60

    def get_cache_timeout(self):
        return self.cache_timeout

    def dispatch(self, *args, **kwargs):
        return cache_page(self.get_cache_timeout())(super(CacheMixin, self).dispatch)(*args, **kwargs)


# API ДТП на карте
class DTPApiView(generics.ListAPIView):
    queryset = data_models.DTP.objects.filter(region__is_active=True).prefetch_related(
        'severity',
        'region',
        'category',
        'weather',
        'nearby',
        'road_conditions',
        'participant_categories',
        'tags',
        'participant_set__violations'
    )
    serializer_class = data_serializers.DTPSerializer
    filterset_class = data_filters.DTPFilterSet


class DTPApiViewLoad(generics.ListAPIView):
    queryset = data_models.DTP.objects.filter(region__is_active=True).prefetch_related(
        'severity',
        'region',
        'category',
        'weather',
        'nearby',
        'road_conditions',
        'participant_categories',
        'tags',
        'participant_set__violations'
    )
    serializer_class = data_serializers.DTPSerializer
    filterset_class = data_filters.DTPLoadFilterSet


def mapdata(request):
    if not os.path.exists(settings.MEDIA_ROOT + "/mapdata/"):
        os.makedirs(settings.MEDIA_ROOT + "/mapdata/")

    if request.GET.get('year') and request.GET.get('region_slug'):
        # files = os.listdir(settings.STATIC_ROOT)
        files = os.listdir(settings.MEDIA_ROOT + "/mapdata/")
        for file in files:
            file_region_slug = file.split('_')[0]
            if request.GET.get('year') in file and request.GET.get('region_slug') == file_region_slug:
                with open(settings.MEDIA_ROOT + "/mapdata/" + file) as data_file:
                    data = json.load(data_file)

                return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False})

        utils.mapdata(request.GET.get('region_slug'), request.GET.get('year'))
        return HttpResponseRedirect('?year=' + request.GET.get('year') + '&region_slug=' + request.GET.get('region_slug').format(reverse('mapdata')))


#@cache_page(24 * 60 * 60)
@api_view(['GET'])
def mvcs(request):
    mvcs = data_models.DTP.objects.all().values(
        'id', 'datetime', 'participants', 'injured', 'dead'
    )
    print(len(mvcs))
    return Response(mvcs)


# API статистики
class StatApiView(viewsets.ModelViewSet):
    queryset = data_models.DTP.objects.all()
    serializer_class = data_serializers.DTPSerializer
    filterset_class = data_filters.DTPStatFilterSet

    @action(detail=False, methods=['get'])
    def stat(self, request):
        data = {}

        queryset = self.filter_queryset(self.queryset)

        # определяем регион и масштаб, выводим их и считаем краткую статистику
        region = utils.get_region_by_center_point(request.query_params.get('center_point'))
        if region:
            scale = request.query_params.get('scale')
            if not scale or int(scale) <= 12:
                region = region.parent_region
                queryset = queryset.filter(region__parent_region=region)
                data['parent_region_slug'] = region.slug
            else:
                queryset = queryset.filter(region=region)
                data['parent_region_name'] = region.parent_region.name
                data['parent_region_slug'] = region.parent_region.slug

            data['region_name'] = region.name
            data['region_slug'] = region.slug

        if request.query_params.get('start_date') and request.query_params.get('end_date'):
            data = {**data, **{
                "count": queryset.count(),
                "injured": queryset.aggregate(Sum("injured")).get('injured__sum') or 0,
                "dead": queryset.aggregate(Sum("dead")).get('dead__sum') or 0
            }}

        return Response(data)


# API конструктора фильтров
class FiltersApiView(APIView):
    @method_decorator(cache_page(60 * 60 * 24))
    def get(self, request):
        filters = []

        # определяем регион
        region_slug = request.query_params.get('region_slug')
        if region_slug:
            region = get_object_or_404(data_models.Region, slug=region_slug)
            region = region.parent_region
            downloads = data_models.Download.objects.filter(region=region).order_by('date')
        else:
            downloads = data_models.Download.objects.filter(last_update__isnull=False).order_by('date')


        # фильтр по дате
        filters.append({
            "name": "date",
            "label": "Период данных",
            "values": [
                downloads.first().date,
                downloads.last().date.replace(day=calendar.monthrange(downloads.last().date.year, downloads.last().date.month)[1])
            ],
            "default_value": {
                "start_date": downloads.last().date,
                "end_date": downloads.last().date.replace(day=calendar.monthrange(downloads.last().date.year, downloads.last().date.month)[1])
            }
        })



        # фильтр по участникам
        filters.append({
            "name": "participant_categories",
            "label": "Участники ДТП",
            "multiple": False,
            "values": [
                {
                    "preview": x.name,
                    "value": x.id,
                    "icon": static('media/' + x.slug + '.svg'),
                    "default": True if x.slug == 'all' else False
                } for x in data_models.ParticipantCategory.objects.all()]
        })

        # фильтр по тяжести
        severity_colors = {
            0: 'rgba(24, 51, 74, 0.5)',
            1: '#FFB81F',
            3: '#FF7F24',
            4: '#FF001A'
        }
        filters.append(
            {
                "name": "severity",
                "label": "Вред здоровью",
                "multiple": True,
                "values": [
                    {
                        'preview': x.name,
                        'value': x.level,
                        'color': severity_colors.get(x.level),
                        'disabled': True if x.level == 0 else False,
                        "default": True if x.level in [1,2,3,4] else False
                    } for x in data_models.Severity.objects.all().order_by("level")
                ]
            },
        )

        filters.append(
            {
                "name": "category",
                "key": "category",
                "label": "Типы ДТП",
                "values": [
                    {
                    "preview": x.name,
                    "value": x.id
                    } for x in data_models.Category.objects.all().order_by("name")],
            }
        )

        filters.append(
            {
                "name": "category",
                "key": "violations",
                "label": "Нарушения ПДД",
                "values": [
                    {
                        "preview": x.name,
                        "value": x.id
                    } for x in data_models.Violation.objects.all().order_by("name")],
            }
        )

        filters.append(
            {
                "name": "category",
                "key": "nearby",
                "label": "Объекты поблизости",
                "values": [
                    {
                        "preview": x.name,
                        "value": x.id
                    } for x in data_models.Nearby.objects.all().order_by("name")],
            }
        )

        filters.append(
            {
                "name": "category",
                "key": "conditions",
                "label": "Дорожные условия",
                "values": [
                    {
                        "preview": x.name,
                        "value": x.id
                    } for x in data_models.RoadCondition.objects.all().order_by("name")],
            }
        )

        filters.append(
            {
                "name": "category",
                "key": "street",
                "label": "Улицы",
                "values": [],
            }
        )

        filters.append(
            {
                "name": "category",
                "key": "weather",
                "label": "Погода",
                "values": [
                    {
                        "preview": x.name,
                        "value": x.id
                    } for x in data_models.Weather.objects.all().order_by("name")
                ],
            }
        )

        return Response(filters)
