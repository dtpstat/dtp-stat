from rest_framework import serializers
from drf_extra_fields.geo_fields import PointField
from data import models


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Tag
        fields = ('name',)


class ParticipantCategorySerializer(serializers.RelatedField):

    def to_representation(self, value):
        return value.id

    class Meta:
        model = models.ParticipantCategory

class DTPSerializer(serializers.Serializer):
    id = serializers.CharField(source='gibdd_slug')
    datetime = serializers.DateTimeField()
    severity = serializers.IntegerField(source='severity.level')
    participants = serializers.IntegerField()
    injured = serializers.IntegerField()
    dead = serializers.IntegerField()
    point = PointField()
    region_slug = serializers.CharField(source='region.slug')
    category = serializers.IntegerField(source='category.id')
    address = serializers.CharField()
    category_name = serializers.CharField(source='category.name')
    participant_categories = serializers.PrimaryKeyRelatedField(read_only=True, many=True)
    tags = serializers.PrimaryKeyRelatedField(read_only=True, many=True)


class RegionSerializer(serializers.Serializer):
    slug = serializers.CharField()
    name = serializers.CharField()
    parent_region = serializers.CharField()
    level = serializers.IntegerField()
    point = PointField()

