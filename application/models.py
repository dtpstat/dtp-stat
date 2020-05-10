from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.crypto import get_random_string
from . import middlewares

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


class BlogPost(models.Model):
    created_at = models.DateTimeField(help_text="datetime publish", default=timezone.now, null=True, blank=True)
    title = models.CharField(help_text="Post title", max_length=200, null=True, blank=True, default=None)
    text = RichTextUploadingField(help_text="text", null=True, blank=True, default=None)
    slug = models.CharField(help_text="slug", max_length=200, null=True, blank=True, default=None, db_index=True)
    created_by = models.ForeignKey(User, default=middlewares.get_current_user, on_delete=models.SET_NULL, null=True)

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