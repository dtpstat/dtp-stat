from rest_framework import serializers
from drf_extra_fields.geo_fields import PointField
from data import models


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Tag
        fields = ('name',)


class DTPSerializer(serializers.Serializer):
    id = serializers.CharField(source='slug')
    datetime = serializers.DateTimeField()
    severity = serializers.IntegerField(source="severity.level")
    participants = serializers.IntegerField()
    injured = serializers.IntegerField()
    dead = serializers.IntegerField()
    point = PointField()
    #tags = TagSerializer(many=True)


class RegionSerializer(serializers.Serializer):
    slug = serializers.CharField()
    name = serializers.CharField()
    parent_region = serializers.CharField()
    level = serializers.IntegerField()
    point = PointField()

