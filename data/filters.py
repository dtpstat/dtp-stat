from data import models
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D
from django.db.models import Q

import django_filters
from rest_framework import filters as drf_filters


class SearchRegionFilterSet(django_filters.FilterSet):
    search = django_filters.CharFilter(field_name='name', lookup_expr='icontains')


class DTPFilterSet(django_filters.FilterSet):
    start_date = django_filters.DateFilter(field_name='datetime__date', lookup_expr='gte')
    end_date = django_filters.DateFilter(field_name='datetime__date', lookup_expr='lte')
    category = django_filters.BaseInFilter(field_name='category__name', lookup_expr='in')
    tags = django_filters.BaseInFilter(field_name='tags__name', lookup_expr='in')
    participant_categories = django_filters.BaseInFilter(field_name='participant_categories__slug', lookup_expr='in')
    severity = django_filters.BaseInFilter(field_name='severity__level', lookup_expr='in')
    light = django_filters.BaseInFilter(field_name='light__name', lookup_expr='in')
    weather = django_filters.BaseInFilter(field_name='weather__name', lookup_expr='in')
    nearby = django_filters.BaseInFilter(field_name='nearby__name', lookup_expr='in')
    conditions = django_filters.BaseInFilter(field_name='road_conditions__name', lookup_expr='in')
    violations = django_filters.BaseInFilter(field_name='participant__violations__name', lookup_expr='in')
    id = django_filters.CharFilter(field_name='slug', lookup_expr="exact")
    street = django_filters.BaseInFilter(field_name='street__name', lookup_expr='in')

    class Meta:
        model = models.DTP
        fields = {
            'dead': ['gte', 'lte', 'exact', 'gt', 'lt'],
        }


class GeoFilterBackend(drf_filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        geo = request.query_params.get('geo')
        if "," in geo:
            geo = GEOSGeometry('POLYGON((' + geo + '))')
            queryset = queryset.filter(point__within=geo)
        else:
            geo = GEOSGeometry('POINT(' + geo + ')')
        """
        lat = request.query_params.get('lat')
        long = request.query_params.get('long')
        if lat and long:
            pnt = GEOSGeometry('POINT(%(lat)s %(long)s)' % {"lat": lat, "long": long}, srid=4326)
            queryset = queryset.filter(point__distance_lte=(pnt, D(km=100)))
        
        """
        return queryset