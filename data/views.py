

from rest_framework import generics, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets
import django_filters.rest_framework
from rest_framework.decorators import action
from django.db.models import Sum

from data import filters as data_filters
from data import models
from data import serializers
from data import utils


class DTPApiView(generics.ListAPIView):
    queryset = models.DTP.objects.all()
    serializer_class = serializers.DTPSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, data_filters.GeoFilterBackend,)
    filterset_class = data_filters.DTPFilterSet


class StatApiView(viewsets.ModelViewSet):
    queryset = models.DTP.objects.all()
    serializer_class = serializers.DTPSerializer
    filterset_class = data_filters.DTPFilterSet

    @action(detail=False, methods=['get'])
    def stat(self, request):
        region = utils.get_region_by_request(request)

        if region:
            queryset = self.filter_queryset(self.queryset).filter(region=region)
            region_name = region.name
        else:
            region_name = "Россия"
            queryset = self.filter_queryset(self.queryset)

        data = {
            "region_name": region_name,
            "count": queryset.count(),
            "dead": queryset.aggregate(Sum("dead")).get('dead__sum'),
            "injured": queryset.aggregate(Sum("injured")).get('injured__sum')
        }
        return Response(data)


class FilterApiView(APIView):
    def get(self, request):
        data = {x: [] for x in ['street']}

        region = utils.get_region_by_request(request)

        if region:
            data['street'] = [x.name for x in models.Street.objects.filter(dtp__region=region).distinct().order_by("name")]

        data["category"] = [x.name for x in models.Category.objects.all().order_by("name")]
        data["light"] = [x.name for x in models.Light.objects.all().order_by("name")]
        return Response(data)

