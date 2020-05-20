from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from django.contrib.postgres.fields import JSONField
from django.utils.crypto import get_random_string

from slugify import slugify


def get_slug(instance, slug_string=None, length=5):
    if slug_string:
        slug = slugify(slug_string)
    else:
        slug = get_random_string(length=length)

    Klass = instance.__class__

    qs_exists = Klass.objects.filter(slug=slug).exists()
    if qs_exists:
        if slug_string:
            return get_slug(instance, slug_string=slug_string + "-" + get_random_string(length=3))
        else:
            return get_slug(instance)
    return slug


class Region(models.Model):
    name = models.CharField(max_length=1000, help_text="name", null=True, blank=True, default=None, db_index=True)
    slug = models.CharField(max_length=1000, help_text="slug", null=True, blank=True, default=None, db_index=True)
    gibdd_code = models.CharField(max_length=20, help_text="gibdd code", null=True, blank=True, default=None, db_index=True)
    level = models.IntegerField(help_text="level", null=True, blank=True, default=None, db_index=True)
    parent_region = models.ForeignKey('self', help_text="Parent region", null=True, blank=True, default=None, on_delete=models.SET_NULL, db_index=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug and self.name:
            self.slug = get_slug(self, slug_string=self.name)
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


class Tag(models.Model):
    name = models.CharField(max_length=1000, help_text="name", null=True, blank=True, default=None, db_index=True)
    is_filter = models.BooleanField(default=False, db_index=True)
    code = models.CharField(max_length=100, help_text="code", null=True, blank=True, default=None)

    def __str__(self):
        return self.name


class Severity(models.Model):
    level = models.IntegerField(help_text="level", null=True, blank=True)
    name = models.CharField(max_length=1000, help_text="name", null=True, blank=True, default=None)
    keywords = JSONField(null=True, blank=True, default=list)

    def __str__(self):
        return self.name


class ParticipantCategory(models.Model):
    name = models.CharField(max_length=1000, help_text="name", null=True, blank=True, default=None)
    slug = models.CharField(max_length=1000, help_text="slug", null=True, blank=True, default=None)

    def __str__(self):
        return self.name


class DTP(models.Model):
    region = models.ForeignKey(Region, help_text="region", null=True, blank=True, default=None, on_delete=models.SET_NULL, db_index=True)
    slug = models.CharField(max_length=1000, help_text="slug", null=True, blank=True, default=None, db_index=True)
    datetime = models.DateTimeField(help_text="datetime", null=True, blank=True, default=None, db_index=True)

    address = models.CharField(max_length=1000, help_text="address", null=True, blank=True, default=None, db_index=True)
    street = models.CharField(max_length=1000, help_text="street", null=True, blank=True, default=None, db_index=True)
    point = models.PointField(help_text="coordinates", null=True, default=None, srid=4326)

    participants = models.IntegerField(help_text="participants count", null=True, blank=True, default=None,
                                       db_index=True)
    injured = models.IntegerField(help_text="injured count", null=True, blank=True, default=None, db_index=True)
    dead = models.IntegerField(help_text="dead count", null=True, blank=True, default=None, db_index=True)

    scheme = models.CharField(max_length=100, help_text="scheme number", null=True, blank=True, default=None)

    category = models.ForeignKey(Category, help_text="category", null=True, blank=True, default=None, on_delete=models.SET_NULL, db_index=True)
    light = models.ForeignKey(Light, help_text="light", null=True, blank=True, default=None,
                                 on_delete=models.SET_NULL, db_index=True)
    severity = models.ForeignKey(Severity, help_text="severity lvl", db_index=True, on_delete=models.SET_NULL,
                                 null=True, blank=True, default=None)

    nearby = models.ManyToManyField(Nearby, help_text="nearby objects", db_index=True)
    weather = models.ManyToManyField(Weather, help_text="weather", db_index=True)
    road_conditions = models.ManyToManyField(RoadCondition, help_text="Road conditions", db_index=True)
    tags = models.ManyToManyField(Tag, help_text="Tags", db_index=True)
    participant_categories = models.ManyToManyField(ParticipantCategory, help_text="ParticipantCategory", db_index=True)

    data = JSONField(help_text="extra data", null=True, blank=True, default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.category.name + " " + self.region.name + " " + str(self.datetime)

    def full_address(self):
        return ", ".join([x for x in [self.region.parent_region.name, self.region.name, self.address] if x])

    def get_absolute_url(self):
        return '/dtp/' + self.slug + '/'

    def as_dict(self):
        return {
            "id": self.id,
            "point": {
                "lat": self.point.coords[1] if self.point else None,
                "long": self.point.coords[0] if self.point else None,
            },
            "region": self.region.name,
            "parent_region": self.region.parent_region.name,
            "datetime": self.datetime.strftime("%Y-%m-%d %H:%M:%S"),
            "address": self.address,
            "participants_count": self.participants,
            "injured_count": self.injured,
            "dead_count": self.dead,
            "category": self.category.name,
            "light": self.light.name,
            "nearby": [x.name for x in self.nearby.all()],
            "weather": [x.name for x in self.weather.all()],
            "road_conditions": [x.name for x in self.road_conditions.all()],
            "vehicles": [{
                'brand':x.brand,
                'model':x.vehicle_model,
                'color': x.color,
                'year': x.year,
                'category': x.category.name,
                'participants': [{
                    "health_status": y.health_status,
                    "role": y.role,
                    "gender": y.gender,
                    "years_of_driving_experience": y.driving_experience,
                    "violations": [k.name for k in y.violations.all()]
                } for y in x.participant_set.all()]
            } for x in Vehicle.objects.filter(participant__dtp=self).distinct()],
            "participants": [{
                "health_status": x.health_status,
                "role": x.role,
                "gender": x.gender,
                "violations": [y.name for y in x.violations.all()]
            } for x in self.participant_set.filter(vehicle__isnull=True)],
            "tags": [x.name for x in self.tags.all()]
        }

    def save(self, *args, **kwargs):
        if not self.point:
            geo = self.geo_set.filter(source="gibdd").last()
            if geo:
                self.point = geo.point
                self.address = geo.address
                self.street = geo.street


        super(DTP, self).save(*args, **kwargs)


class Geo(models.Model):
    dtp = models.ForeignKey(DTP, help_text="DTP", null=True, blank=True, default=None, on_delete=models.CASCADE)
    source = models.CharField(max_length=100, help_text="data source", null=True, blank=True, default=None, choices=[
        ("gibdd", "ГИБДД"),
        ("user", "Пользователи"),
        ("geocode", "Геокодер")
    ])
    street = models.CharField(max_length=1000, help_text="street", null=True, blank=True, default=None,db_index=True)
    address = models.CharField(max_length=1000, help_text="address", null=True, blank=True, default=None, db_index=True)
    point = models.PointField(help_text="coordinates", null=True, default=None, srid=4326)


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
    vehicle_model = models.CharField(max_length=1000, help_text="model", null=True, blank=True, default=None, db_index=True)
    color = models.CharField(max_length=1000, help_text="color", null=True, blank=True, default=None, db_index=True)
    year = models.IntegerField(help_text="year", null=True, blank=True, default=None, db_index=True)
    category = models.ForeignKey(VehicleCategory, help_text="category", null=True, blank=True, default=None, on_delete=models.CASCADE)

    def __str__(self):
        return self.brand + " " + self.vehicle_model


class Participant(models.Model):
    role = models.CharField(max_length=1000, help_text="role", null=True, blank=True, default=None, db_index=True)
    driving_experience = models.IntegerField(help_text="Participant driving experience (years)", null=True, blank=True)
    health_status = models.CharField(max_length=1000, help_text="Participant status", null=True, blank=True, default=None)
    gender = models.CharField(max_length=1000, help_text="Participant gender", null=True, blank=True, default=None)

    dtp = models.ForeignKey(DTP, help_text="DTP", null=True, blank=True, default=None, on_delete=models.CASCADE)
    violations = models.ManyToManyField(Violation, help_text="violations", db_index=True)
    vehicle = models.ForeignKey(Vehicle, help_text="vehicle", null=True, blank=True, default=None, on_delete=models.CASCADE)
    severity = models.ForeignKey(Severity, help_text="severity lvl", db_index=True, null=True, blank=True, default=None, on_delete=models.SET_NULL)


class Download(models.Model):
    date = models.DateField(help_text="date", null=True, blank=True, default=None, db_index=True)
    region = models.ForeignKey(Region, help_text="region", null=True, blank=True, default=None, on_delete=models.SET_NULL, db_index=True)
    base_data = models.BooleanField(help_text="tags", null=True, blank=True, default=False)
    tags = models.BooleanField(help_text="tags", null=True, blank=True, default=False)