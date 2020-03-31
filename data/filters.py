from data import models
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D

import django_filters
from rest_framework import filters as drf_filters


class SearchRegionFilterSet(django_filters.FilterSet):
    search = django_filters.CharFilter(field_name='name', lookup_expr='icontains')


class DTPFilterSet(django_filters.FilterSet):
    region = django_filters.CharFilter(field_name='region__slug')
    start_date = django_filters.DateFilter(field_name='datetime__date', lookup_expr='gte')
    end_date = django_filters.DateFilter(field_name='datetime__date', lookup_expr='lte')
    light = django_filters.BaseInFilter(field_name='light__name', lookup_expr='in')
    category = django_filters.BaseInFilter(field_name='category__name', lookup_expr='in')

    class Meta:
        model = models.DTP
        fields = {
            'slug': ['exact'],
            'dead': ['gte', 'lte', 'exact', 'gt', 'lt'],
        }


class GeoFilterBackend(drf_filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        lat = request.query_params.get('lat')
        long = request.query_params.get('long')
        if lat and long:
            pnt = GEOSGeometry('POINT(%(lat)s %(long)s)' % {"lat": lat, "long": long}, srid=4326)
            queryset = queryset.filter(point__distance_lte=(pnt, D(km=100)))
        return queryset
