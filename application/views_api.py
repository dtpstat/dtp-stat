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

import calendar
import datetime


class DTPApiView(generics.ListAPIView):
    queryset = data_models.DTP.objects.all()
    serializer_class = data_serializers.DTPSerializer
    filterset_class = data_filters.DTPFilterSet
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, data_filters.GeoFilterBackend,)
    pagination_class = LimitOffsetPagination

    def post(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class StatApiView(viewsets.ModelViewSet):
    queryset = data_models.DTP.objects.all()
    serializer_class = data_serializers.DTPSerializer
    filterset_class = data_filters.DTPFilterSet
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, data_filters.GeoFilterBackend,)

    @action(detail=False, methods=['get'])
    def stat(self, request):
        geo = request.query_params.get('geo')
        scale = request.query_params.get('scale')

        queryset = self.filter_queryset(self.queryset)

        if "," in geo:
            name = "Полигон"
        else:
            region = utils.get_region_by_request(request)
            if region:
                if not scale or int(scale) < 7:
                    name = region.name
                    queryset = queryset.filter(Q(region=region))
                else:
                    name = region.parent_region.name
                    queryset = queryset.filter(Q(region__parent_region=region.parent_region))
            else:
                name = "Россия"

        data = {
            "name": name,
            "count": queryset.count(),
            "dead": queryset.aggregate(Sum("dead")).get('dead__sum'),
            "injured": queryset.aggregate(Sum("injured")).get('injured__sum')
        }
        return Response(data)


class FiltersApiView(APIView):
    def get(self, request):
        data = {}
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

            try:
                last_tags_data = data_models.Download.objects.filter(region=region, base_data=True).latest("date").date
            except:
                last_tags_data = None

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