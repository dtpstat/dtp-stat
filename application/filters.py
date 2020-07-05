from data import models
from django.contrib.gis.geos import GEOSGeometry

import django_filters


def geo_filter(queryset, name, value):
    if value:
        if "," in value:
            geo = GEOSGeometry('POLYGON((' + value + '))')
            queryset = queryset.filter(point__within=geo)
    return queryset


class DTPFilterSet(django_filters.FilterSet):
    start_date = django_filters.DateFilter(field_name='datetime__date', lookup_expr='gte', required=True)
    end_date = django_filters.DateFilter(field_name='datetime__date', lookup_expr='lte', required=True)
    geo_frame = django_filters.CharFilter(method=geo_filter, required=True)


class DTPStatFilterSet(django_filters.FilterSet):
    start_date = django_filters.DateFilter(field_name='datetime__date', lookup_expr='gte')
    end_date = django_filters.DateFilter(field_name='datetime__date', lookup_expr='lte')
    severity = django_filters.BaseInFilter(field_name='severity__level', lookup_expr='in')
    participant_categories = django_filters.BaseInFilter(field_name='participant_categories__slug', lookup_expr='in')
    geo_frame = django_filters.CharFilter(method=geo_filter)

    """
    category = django_filters.BaseInFilter(field_name='category__name', lookup_expr='in')
    tags = django_filters.BaseInFilter(field_name='tags__name', lookup_expr='in')
    light = django_filters.BaseInFilter(field_name='light__name', lookup_expr='in')
    weather = django_filters.BaseInFilter(field_name='weather__name', lookup_expr='in')
    nearby = django_filters.BaseInFilter(field_name='nearby__name', lookup_expr='in')
    conditions = django_filters.BaseInFilter(field_name='road_conditions__name', lookup_expr='in')
    violations = django_filters.BaseInFilter(field_name='participant__violations__name', lookup_expr='in')
    id = django_filters.CharFilter(field_name='slug', lookup_expr="exact")
    street = django_filters.BaseInFilter(field_name='street', lookup_expr='in')
        """