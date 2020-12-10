from rest_framework import serializers
from drf_extra_fields.geo_fields import PointField
from data import models
from drf_serializer_cache import SerializerCacheMixin


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Tag
        fields = ('name',)


class ParticipantCategorySerializer(serializers.RelatedField):
    def to_representation(self, value):
        return value.id

    class Meta:
        model = models.ParticipantCategory


class ViolationSerializer(serializers.RelatedField):
    def to_representation(self, value):
        return value.id

    class Meta:
        model = models.Violation


class TestSerializer(serializers.RelatedField):
    def to_representation(self, value):
        return value.violations.id

    class Meta:
        model = models.Participant


class DTPSerializer(SerializerCacheMixin, serializers.Serializer):
    id = serializers.CharField(source='gibdd_slug')
    datetime = serializers.DateTimeField()
    participants = serializers.IntegerField()
    injured = serializers.IntegerField()
    dead = serializers.IntegerField()
    point = PointField()
    address = serializers.CharField()
    street = serializers.CharField()
    severity = serializers.IntegerField(source='severity.level')
    region_slug = serializers.CharField(source='region.slug')
    category = serializers.IntegerField(source='category.id')
    category_name = serializers.CharField(source='category.name')
    weather = serializers.PrimaryKeyRelatedField(read_only=True, many=True)
    nearby = serializers.PrimaryKeyRelatedField(read_only=True, many=True)
    conditions = serializers.PrimaryKeyRelatedField(source='road_conditions',read_only=True, many=True)
    participant_categories = serializers.PrimaryKeyRelatedField(read_only=True, many=True)
    tags = serializers.PrimaryKeyRelatedField(read_only=True, many=True)
    violations = serializers.SerializerMethodField('get_violations')

    @staticmethod
    def get_violations(self):
        participants = models.Participant.objects.filter(dtp=self)
        return [x for x in participants.values_list('violations', flat=True) if x]


class RegionSerializer(serializers.Serializer):
    slug = serializers.CharField()
    name = serializers.CharField()
    parent_region = serializers.CharField()
    level = serializers.IntegerField()
    point = PointField()

