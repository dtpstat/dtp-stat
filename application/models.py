from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.crypto import get_random_string
from . import middlewares
from django.contrib.postgres.fields import JSONField
from django.conf import settings
from django.contrib.gis.geos import Point

from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField

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


class BlogTag(models.Model):
    name = models.CharField(help_text="Текст тега", max_length=200)

    def __str__(self):
        return self.name


class BlogPost(models.Model):
    created_at = models.DateTimeField(help_text="Дата и время, с которого пост станет виден в блоге (по гринвичу, +3 Москве)", default=timezone.now, null=True, blank=True)
    title = models.CharField(help_text="Заголовок", max_length=200, null=True, blank=True, default=None)
    author_name = models.CharField(help_text="Имена авторов строчкой через запятую (можно не указывтаь никого)",
                                   max_length=1000, null=True, blank=True, default=None, db_index=True)
    tags = models.ManyToManyField("BlogTag", db_index=True, blank=True)
    cover = models.ImageField(upload_to='blog_covers',help_text='Заглавная картинка (желательно в соотношении 16:9 - 960×540, 1280×720)', null=True, blank=True, default=None)
    abstract = models.TextField(help_text='Краткая аннотация', null=True, blank=True, default=None)
    text = RichTextUploadingField(help_text="Текст", null=True, blank=True, default=None)
    slug = models.CharField(help_text="Ссылка на пост (если оставить пустым, заполнится автоматически из названия)", max_length=200, null=True, blank=True, default=None, db_index=True)
    created_by = models.ForeignKey(User, help_text="Кто добавил пост (заполнится автоматически)", default=middlewares.get_current_user, on_delete=models.SET_NULL, null=True)


    def save(self, *args, **kwargs):
        if not self.slug and self.title:
            self.slug = get_slug(self, slug_string=self.title[:30])
        super(BlogPost, self).save(*args, **kwargs)


class Page(models.Model):
    title = models.CharField(help_text="Post title", max_length=200, null=True, blank=True, default=None)
    text = RichTextUploadingField(help_text="text", null=True, blank=True, default=None)
    slug = models.CharField(help_text="slug", max_length=200, null=True, blank=True, default=None, db_index=True)

    def save(self, *args, **kwargs):
        if not self.slug and self.title:
            self.slug = get_slug(self, slug_string=self.title[:30])
        super(Page, self).save(*args, **kwargs)


class OpenData(models.Model):
    region = models.ForeignKey("data.Region", null=True, blank=True, default=None, on_delete=models.SET_NULL)
    date = models.DateField(help_text="date", null=True, blank=True, default=None, db_index=True)
    file_size = models.IntegerField(null=True, blank=True, default=None)

    def mb_file_size(self):
        return self.file_size/(1024*1024)


class Ticket(models.Model):
    dtp = models.ForeignKey("data.DTP",  null=True, blank=True, default=None, on_delete=models.SET_NULL)
    category = models.CharField(max_length=200, null=True, blank=True, default=None, choices=[
        ("fix_point", "Корректировка координат"),
    ])
    comment = models.TextField(null=True, blank=True, default=None)
    data = JSONField(default=dict, null=True, blank=True)
    moderated_by = models.ForeignKey(User, default=middlewares.get_current_user, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    status = models.CharField(max_length=200, null=True, blank=True, default="new", choices=[
        ("new", "новое"),
        ("done", "готово"),
        ("no", "невозможно пофиксить")
    ])


class Moderator(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, db_index=True, default=None, null=True, blank=True)
    username = models.CharField(max_length=200, default=None, null=True, blank=True)
    regions = models.ManyToManyField("data.Region", db_index=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def regions_list(self):
        return ", ".join([x.name for x in self.regions.all()])


class BriefData(models.Model):
    date = models.DateField()
    dtp_count = models.PositiveIntegerField(null=True)
    death_count = models.PositiveIntegerField(null=True)
    injured_count = models.PositiveIntegerField(null=True)
    child_death_count = models.PositiveIntegerField(null=True)
    child_injured_count = models.PositiveIntegerField(null=True)
