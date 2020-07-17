from django.core.management.base import BaseCommand
from application import utils
from data import models


class Command(BaseCommand):
    help = 'fix'

    def handle(self, *args, **kwargs):
        models.Region.objects.all().update(ya_name=None)

