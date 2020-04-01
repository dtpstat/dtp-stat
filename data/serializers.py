from rest_framework import serializers
from drf_extra_fields.geo_fields import PointField
from data import models


class DTPSerializer(serializers.Serializer):
    id = serializers.CharField(source='slug')
    datetime = serializers.DateTimeField()
    category = serializers.CharField()
    participants = serializers.IntegerField()
    injured = serializers.IntegerField()
    dead = serializers.IntegerField()
    point = PointField()


class RegionSerializer(serializers.Serializer):
    slug = serializers.CharField()
    name = serializers.CharField()
    parent_region = serializers.CharField()
    level = serializers.IntegerField()
    point = PointField()

