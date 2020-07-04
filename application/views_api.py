from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.pagination import LimitOffsetPagination
import django_filters.rest_framework
from rest_framework.decorators import action

from django.db.models import Sum, Q
from django.shortcuts import get_object_or_404, render

from data import models as data_models
from data import serializers as data_serializers

from application import utils, filters as data_filters
from application import models
from django.utils import timezone
from django.templatetags.static import static


import calendar
import datetime


# API ДТП на карте
class DTPApiView(generics.ListAPIView):
    queryset = data_models.DTP.objects.all()
    serializer_class = data_serializers.DTPSerializer
    filterset_class = data_filters.DTPFilterSet


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
            else:
                queryset = queryset.filter(region=region)
                data['parent_region_name'] = region.parent_region.name

            data['region_name'] = region.name
            data['region_slug'] = region.slug

            data = {**data, **{
                "count": queryset.count(),
                "injured": queryset.aggregate(Sum("injured")).get('injured__sum'),
                "dead": queryset.aggregate(Sum("dead")).get('dead__sum')
            }}

        return Response(data)


# API конструктора фильтров
class FiltersApiView(APIView):
    def get(self, request):
        filters = []

        # определяем регион
        region_slug = request.query_params.get('region_slug')
        if region_slug:
            region = get_object_or_404(data_models.Region, slug=region_slug)
            if region.parent_region:
                region = region.parent_region
            region_downloads = data_models.Download.objects.filter(region=region).order_by('date')

            if region_downloads:

                # фильтр по дате
                filters.append({
                    "name": "date",
                    "label": "Период данных",
                    "values": [
                        region_downloads.first().date,
                        region_downloads.last().date.replace(day=calendar.monthrange(region_downloads.last().date.year, region_downloads.last().date.month)[1])
                    ],
                    "default_value": {
                        "start_date": region_downloads.last().date,
                        "end_date": region_downloads.last().date.replace(day=calendar.monthrange(region_downloads.last().date.year, region_downloads.last().date.month)[1])
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
                            "value": x.slug,
                            "icon": static('media/icon-all.svg'),
                            "default": True if x.slug == 'all' else False
                        } for x in data_models.ParticipantCategory.objects.all()]
                })

                # фильтр по тяжести
                severity_colors = {
                    0: 'rgba(24, 51, 74, 0.5)',
                    1: '#FFFFB2',
                    2: '#F9C52E',
                    3: '#FD8D3C',
                    4: '#E31A1C'
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

        return Response(filters)



        """
        region = utils.get_region_by_request(request)

        if not region:
            data = {
                "error_message": "Вы находитесь за пределами России"
            }
        else:
            try:
                last_base_data = data_models.Download.objects.filter(region=region, base_data=True).latest("date").date
            except:
                last_base_data = None

            if not last_base_data:
                data = {
                    "error_message": "Данных по вашему региону пока нет"
                }
            else:
                data = {
                    "error_message": None,
                    "filters": {
                        "date": {
                            "range_values:": [
                                "2015-01-01",
                                last_base_data.replace(
                                    day=calendar.monthrange(last_base_data.year, last_base_data.month)[1]
                                ).strftime("%Y-%m-%d")
                            ],
                            "range_params": [
                                "start_date",
                                "end_date"
                            ]
                        },
                        "participants": {
                            "values": [(x.name, x.slug) for x in data_models.ParticipantCategory.objects.filter(
                                ~Q(slug__in=['kids', 'public_transport'])
                            )],
                            "parameter": "participant_categories"
                        },
                        "categories": {
                            "values": [(x.name, x.name) for x in data_models.Category.objects.all().order_by("name")],
                            "parameter": "category"
                        },
                        "severity": {
                            "values": [(x.name, x.level) for x in data_models.Severity.objects.all().order_by("level")],
                            "parameter": "severity"
                        },
                        "violations": {
                            "values": [(x.name, x.name) for x in data_models.Violation.objects.all().order_by("name")],
                            "parameter": "violations"
                        },
                        "extra": [
                            {
                                "name": "Погода",
                                "values": [(x.name, x.name) for x in data_models.Weather.objects.all().order_by("name")],
                                "parameter": "weather"
                            }, {
                                "name": "Состояние дороги",
                                "values": [(x.name, x.name) for x in
                                           data_models.RoadCondition.objects.all().order_by("name")],
                                "parameter": "conditions"
                            }, {
                                "name": "Освещение",
                                "values": [(x.name, x.name) for x in data_models.Light.objects.all().order_by("name")],
                                "parameter": "light"
                            }, {
                                "name": "Поблизости",
                                "values": [(x.name, x.name) for x in data_models.Nearby.objects.all().order_by("name")],
                                "parameter": "nearby"
                            }, {
                                "name": "Улицы",
                                "values": [(x.name, x.name) for x in data_models.Street.objects.filter(
                                    Q(dtp__region=region) | Q(dtp__region__in=region.region_set.all())
                                ).distinct().order_by("name")],
                                "parameter": "street"
                            }, {
                                "name": "Теги",
                                "values": [(x.name, x.name) for x in data_models.Tag.objects.all().order_by("name")],
                                "parameter": "tags"
                            }
                        ]
                    }
                }
        return Response(data)
        """
