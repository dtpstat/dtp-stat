from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from django.contrib.postgres.fields import JSONField
from django.utils.crypto import get_random_string

from slugify import slugify


def get_slug(instance, string=None, length=5):
    if string:
        slug = slugify(string)
    else:
        slug = get_random_string(length=length)

    Klass = instance.__class__

    qs_exists = Klass.objects.filter(slug=slug).exists()
    if qs_exists:
        return get_slug(instance)
    return slug

# Create your models here.
class Region(models.Model):
    name = models.CharField(max_length=1000, help_text="name", null=True, blank=True, default=None, db_index=True)
    slug = models.CharField(max_length=1000, help_text="slug", null=True, blank=True, default=None, db_index=True)
    gibdd_code = models.CharField(max_length=20, help_text="gibdd code", null=True, blank=True, default=None, db_index=True)
    level = models.IntegerField(help_text="level", null=True, blank=True, default=None, db_index=True)
    parent_region = models.ForeignKey('self', help_text="Parent region", null=True, blank=True, default=None, on_delete=models.SET_NULL, db_index=True)
    point = models.PointField(help_text="coordinates", null=True, default=None)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = get_slug(self, string=self.name)

        super(Region, self).save(*args, **kwargs)


class Street(models.Model):
    name = models.CharField(max_length=1000, help_text="name", null=True, blank=True, default=None, db_index=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=1000, help_text="name", null=True, blank=True, default=None, db_index=True)

    def __str__(self):
        return self.name


class Light(models.Model):
    name = models.CharField(max_length=1000, help_text="name", null=True, blank=True, default=None, db_index=True)

    def __str__(self):
        return self.name


class Nearby(models.Model):
    name = models.CharField(max_length=1000, help_text="name", null=True, blank=True, default=None, db_index=True)

    def __str__(self):
        return self.name


class Weather(models.Model):
    name = models.CharField(max_length=1000, help_text="name", null=True, blank=True, default=None, db_index=True)

    def __str__(self):
        return self.name


class RoadCondition(models.Model):
    name = models.CharField(max_length=1000, help_text="name", null=True, blank=True, default=None, db_index=True)

    def __str__(self):
        return self.name


class DTP(models.Model):
    region = models.ForeignKey(Region, help_text="region", null=True, blank=True, default=None, on_delete=models.SET_NULL, db_index=True)
    slug = models.CharField(max_length=1000, help_text="slug", null=True, blank=True, default=None, db_index=True)
    datetime = models.DateTimeField(help_text="datetime", null=True, blank=True, default=None, db_index=True)

    #gibdd_address = models.CharField(max_length=10000, help_text="address", null=True, blank=True, default=None, db_index=True)
    #gibdd_point = models.PointField(help_text="coordinates from police", null=True, default=None)
    #geocoder_address = models.CharField(max_length=10000, help_text="address", null=True, blank=True, default=None, db_index=True)
    #geocoder_point = models.PointField(help_text="coordinates from geocoder", null=True, default=None)
    #ugc_address = models.CharField(max_length=10000, help_text="address", null=True, blank=True, default=None, db_index=True)
    #ugc_point = models.PointField(help_text="coordinates from users", null=True, default=None)

    address = models.CharField(max_length=10000, help_text="address", null=True, blank=True, default=None, db_index=True)
    point = models.PointField(help_text="coordinates", null=True, default=None)

    data = JSONField(help_text="extra data", null=True, blank=True, default=dict())

    participants = models.IntegerField(help_text="participants count", null=True, blank=True, default=None,
                                       db_index=True)
    injured = models.IntegerField(help_text="injured count", null=True, blank=True, default=None, db_index=True)
    dead = models.IntegerField(help_text="dead count", null=True, blank=True, default=None, db_index=True)

    scheme = models.CharField(max_length=100, help_text="scheme number", null=True, blank=True, default=None,
                              db_index=True)

    street = models.ForeignKey(Street, help_text="Street", null=True, blank=True, default=None, on_delete=models.SET_NULL, db_index=True)
    category = models.ForeignKey(Category, help_text="category", null=True, blank=True, default=None, on_delete=models.SET_NULL, db_index=True)
    light = models.ForeignKey(Light, help_text="light", null=True, blank=True, default=None,
                                 on_delete=models.SET_NULL, db_index=True)
    nearby = models.ManyToManyField(Nearby, help_text="nearby objects", db_index=True)
    weather = models.ManyToManyField(Weather, help_text="weather", db_index=True)
    road_conditions = models.ManyToManyField(RoadCondition, help_text="Road conditions", db_index=True)
    #participant_type = models.ForeignKey(MVCParticipantType, help_text="MVC Participant Type", null=True, blank=True, default=None, on_delete=models.SET_NULL, db_index=True)

    source = models.CharField(max_length=100, help_text="data source", null=True, blank=True, default=None, choices=[
        ("police", "ГИБДД"),
        ("police_deleted", "ГИБДД (удалено)"),
        ("ugc", "Пользователи")
    ])

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.category.name + " " + self.region.name + " " + str(self.datetime)

    def get_absolute_url(self):
        return '/dtp/' + self.slug + '/'

    def save(self, *args, **kwargs):
        if self.data.get('ugc_point') and self.data.get('ugc_point').get('lat') and self.data.get('ugc_point').get('long'):
            self.point = Point(self.data.get('ugc_point').get('lat'), self.data.get('ugc_point').get('long'))
        elif self.data.get('geocoder_point') and self.data.get('geocoder_point').get('lat') and self.data.get('geocoder_point').get('long'):
            self.point = Point(self.data.get('geocoder_point').get('lat'), self.data.get('geocoder_point').get('long'))
        elif self.data.get('gibdd_point') and self.data.get('gibdd_point').get('lat') and self.data.get('gibdd_point').get('long'):
            self.point = Point(self.data.get('gibdd_point').get('lat'), self.data.get('gibdd_point').get('long'))

        super(DTP, self).save(*args, **kwargs)


class Violation(models.Model):
    name = models.CharField(max_length=1000, help_text="name", null=True, blank=True, default=None, db_index=True)

    def __str__(self):
        return self.name


class VehicleCategory(models.Model):
    name = models.CharField(max_length=1000, help_text="name", null=True, blank=True, default=None, db_index=True)

    def __str__(self):
        return self.name


class Vehicle(models.Model):
    brand = models.CharField(max_length=1000, help_text="brand", null=True, blank=True, default=None, db_index=True)
    car_model = models.CharField(max_length=1000, help_text="model", null=True, blank=True, default=None, db_index=True)
    color = models.CharField(max_length=1000, help_text="color", null=True, blank=True, default=None, db_index=True)
    year = models.IntegerField(help_text="year", null=True, blank=True, default=None, db_index=True)
    category = models.ForeignKey(VehicleCategory, help_text="category", null=True, blank=True, default=None, on_delete=models.CASCADE)

    def __str__(self):
        return self.brand + " " + self.car_model


class Participant(models.Model):
    role = models.CharField(max_length=1000, help_text="role", null=True, blank=True, default=None, db_index=True)
    driving_experience = models.IntegerField(help_text="Participant driving experience (years)", null=True, blank=True)
    health_status = models.CharField(max_length=1000, help_text="Participant status", null=True, blank=True, default=None)
    gender = models.CharField(max_length=1000, help_text="Participant gender", null=True, blank=True, default=None)

    mvc = models.ForeignKey(DTP, help_text="DTP", null=True, blank=True, default=None, on_delete=models.CASCADE)
    violations = models.ManyToManyField(Violation, help_text="violations", db_index=True)
    vehicle = models.ForeignKey(Vehicle, help_text="vehicle", null=True, blank=True, default=None, on_delete=models.CASCADE)


class Download(models.Model):
    datetime = models.DateTimeField(help_text="datetime", null=True, blank=True, default=None, db_index=True)
    phase = models.CharField(max_length=100, help_text="phase", null=True, blank=True, default=None, choices=[
        ("downloading", "Выгрузка данных"),
        ("recording", "Запись в базу"),
        ("done", "Готово")
    ])
