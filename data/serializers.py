from rest_framework import serializers
from drf_extra_fields.geo_fields import PointField


class DTPSerializer(serializers.Serializer):
    slug = serializers.CharField()
    datetime = serializers.DateTimeField()
    category = serializers.CharField()
    participants = serializers.IntegerField()
    injured = serializers.IntegerField()
    dead = serializers.IntegerField()
    light = serializers.CharField()
    point = PointField()

