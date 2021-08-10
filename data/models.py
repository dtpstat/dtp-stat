from django.contrib.gis.db import models
from django.contrib.gis.geos import Point, MultiPolygon
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
    ya_name = models.CharField(max_length=1000, help_text="yandex name", null=True, blank=True, default=None, db_index=True)
    slug = models.CharField(max_length=1000, help_text="slug", null=True, blank=True, default=None, db_index=True)
    gibdd_code = models.CharField(max_length=20, help_text="gibdd code", null=True, blank=True, default=None, db_index=True)
    official_code = models.CharField(max_length=20, help_text="official code", null=True, blank=True, default=None, db_index=True)
    oktmo = models.CharField(max_length=1000, help_text="oktmo", null=True, blank=True, default=None, db_index=True)
    okato = models.CharField(max_length=1000, help_text="okato", null=True, blank=True, default=None, db_index=True)
    geo = models.MultiPolygonField(srid=4326, null=True, blank=True, default=None, db_index=True)
    osm_index = models.CharField(max_length=1000, help_text="geo osm id", null=True, blank=True, default=None, db_index=True)

    level = models.IntegerField(help_text="level", null=True, blank=True, default=None, db_index=True)
    parent_region = models.ForeignKey('self', help_text="Parent region", null=True, blank=True, default=None, on_delete=models.SET_NULL, db_index=True)
    is_active = models.BooleanField(help_text="last_tags_update", default=True)


    def __str__(self):
        return self.name or ''

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
    description = models.CharField(max_length=1000, help_text="description", null=True, blank=True, default=None)
    keywords = JSONField(null=True, blank=True, default=list)

    def __str__(self):
        return self.name


class ParticipantCategory(models.Model):
    name = models.CharField(max_length=1000, help_text="name", null=True, blank=True, default=None)
    slug = models.CharField(max_length=1000, help_text="slug", null=True, blank=True, default=None)

    def __str__(self):
        return self.name


class DTP(models.Model):
    gibdd_slug = models.CharField(max_length=1000, help_text="slug", null=True, blank=True, default=None, db_index=True)
    status = models.BooleanField(help_text="show or hide dtp", default=True)
    only_manual_edit = models.BooleanField(help_text="only manul adit and update", default=False)

    region = models.ForeignKey(Region, help_text="region", null=True, blank=True, default=None,
                               on_delete=models.SET_NULL, db_index=True)
    address = models.CharField(max_length=1000, help_text="address", null=True, blank=True, default=None, db_index=True)
    street = models.CharField(max_length=1000, help_text="street", null=True, blank=True, default=None, db_index=True)
    street_category = models.CharField(max_length=1000, help_text="street category", null=True, blank=True, default=None, db_index=True)
    road_category = models.CharField(max_length=1000, help_text="road category", null=True, blank=True, default=None, db_index=True)
    point = models.PointField(help_text="coordinates", null=True, default=None, srid=4326, spatial_index=True)
    point_is_verified = models.BooleanField(help_text="point is valid and verified", default=False)

    datetime = models.DateTimeField(help_text="datetime", null=True, blank=True, default=None, db_index=True)
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

    nearby = models.ManyToManyField(Nearby, help_text="nearby objects", db_index=True, blank=True)
    weather = models.ManyToManyField(Weather, help_text="weather", db_index=True, blank=True)
    road_conditions = models.ManyToManyField(RoadCondition, help_text="Road conditions", db_index=True, blank=True)
    tags = models.ManyToManyField(Tag, help_text="Tags", db_index=True, blank=True)
    participant_categories = models.ManyToManyField(ParticipantCategory, help_text="ParticipantCategory", db_index=True, blank=True)

    data = JSONField(help_text="extra data", null=True, blank=True, default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    gibdd_latest_check = models.DateTimeField(help_text="gibdd_latest_check", null=True, blank=True, default=None)
    gibdd_latest_change = models.DateTimeField(help_text="gibdd_latest_change", null=True, blank=True, default=None)

    def __str__(self):
        name = ""
        if self.category and self.datetime:
            name = self.category.name + " " + str(self.datetime)
        if self.region:
            name += " " + self.region.parent_region.name
        return name

    def full_address(self):
        return ", ".join([x for x in [self.region.parent_region.name, self.region.name, self.address] if x])

    def get_absolute_url(self):
        return '/dtp/' + self.gibdd_slug + '/'

    def save(self, *args, **kwargs):
        # генерация нового export json

        if self.severity and self.data:
            old_source = self.__class__._default_manager.filter(pk=self.pk).values('data').get()['data'].get('source')
            old_point = self.__class__._default_manager.filter(pk=self.pk).values('point')

            if old_source != self.data.get('source') or not self.data.get('export') or old_point != self.point:
                self.data['export'] = self.as_dict()

        super(DTP, self).save(*args, **kwargs)

    def as_dict(self):
        return {
            "id": self.id,
            "point": {
                "lat": self.point.coords[1] if self.point else None,
                "long": self.point.coords[0] if self.point else None,
            },
            "participant_categories": [x.name for x in self.participant_categories.all()],
            "severity": self.severity.name,
            "region": self.region.name if self.region else None,
            "parent_region": self.region.parent_region.name if self.region else None,
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
                'brand': x.brand,
                'model': x.vehicle_model,
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
            "tags": [x.name for x in self.tags.all()],
            "scheme": self.scheme
        }


class Violation(models.Model):
    name = models.CharField(max_length=1000, help_text="name", null=True, blank=True, default=None, db_index=True)
    gibdd_category = models.CharField(max_length=1000, help_text="category", null=True, blank=True, default=None, db_index=True)

    def __str__(self):
        return self.name


class VehicleCategory(models.Model):
    name = models.CharField(max_length=1000, help_text="name", null=True, blank=True, default=None, db_index=True)

    def __str__(self):
        return self.name


class VehicleDamage(models.Model):
    name = models.CharField(max_length=1000, help_text="damage name", null=True, blank=True, default=None, db_index=True)


class VehicleMalfunction(models.Model):
    name = models.CharField(max_length=1000, help_text="malfunction name", null=True, blank=True, default=None, db_index=True)


class Vehicle(models.Model):
    gibdd_slug = models.CharField(max_length=1000, help_text="vehicle gibdd id", null=True, blank=True, default=None)

    brand = models.CharField(max_length=1000, help_text="brand", null=True, blank=True, default=None, db_index=True)
    vehicle_model = models.CharField(max_length=1000, help_text="model", null=True, blank=True, default=None, db_index=True)
    color = models.CharField(max_length=1000, help_text="color", null=True, blank=True, default=None, db_index=True)
    year = models.IntegerField(help_text="year", null=True, blank=True, default=None, db_index=True)
    category = models.ForeignKey(VehicleCategory, help_text="category", null=True, blank=True, default=None, on_delete=models.CASCADE)
    drive = models.CharField(max_length=1000, help_text="color", null=True, blank=True, default=None, db_index=True)
    ownership = models.CharField(max_length=1000, help_text="ownership", null=True, blank=True, default=None, db_index=True)
    ownership_category = models.CharField(max_length=1000, help_text="ownership_category", null=True, blank=True, default=None, db_index=True)
    malfunctions = models.ManyToManyField(VehicleMalfunction, help_text="malfunctions", blank=True)

    absconded = models.CharField(max_length=1000, help_text="absconded", null=True, blank=True, default=None)
    damages = models.ManyToManyField(VehicleDamage, help_text="damages", blank=True)

    def __str__(self):
        return self.brand + " " + self.vehicle_model


class Participant(models.Model):
    gibdd_slug = models.CharField(max_length=1000, help_text="participant id", null=True, blank=True, default=None)

    role = models.CharField(max_length=1000, help_text="role", null=True, blank=True, default=None, db_index=True)
    driving_experience = models.IntegerField(help_text="Participant driving experience (years)", null=True, blank=True)
    health_status = models.CharField(max_length=1000, help_text="Participant status", null=True, blank=True, default=None)
    gender = models.CharField(max_length=1000, help_text="Participant gender", null=True, blank=True, default=None)
    alco = models.IntegerField(help_text="Participant alco", null=True, blank=True, default=None)
    absconded = models.CharField(max_length=1000, help_text="Participant absconded", null=True, blank=True, default=None)

    dtp = models.ForeignKey(DTP, help_text="DTP", null=True, blank=True, default=None, on_delete=models.CASCADE)
    violations = models.ManyToManyField(Violation, help_text="violations", db_index=True, blank=True)
    vehicle = models.ForeignKey(Vehicle, help_text="vehicle", null=True, blank=True, default=None, on_delete=models.CASCADE)
    severity = models.ForeignKey(Severity, help_text="severity lvl", db_index=True, null=True, blank=True, default=None, on_delete=models.SET_NULL)


class Download(models.Model):
    date = models.DateField(help_text="date", null=True, blank=True, default=None, db_index=True)
    region = models.ForeignKey(Region, help_text="region", null=True, blank=True, default=None, on_delete=models.SET_NULL, db_index=True)
    last_update = models.DateTimeField(help_text="last_update", null=True, blank=True, default=None)
    last_tags_update = models.DateTimeField(help_text="last_tags_update", null=True, blank=True, default=None)