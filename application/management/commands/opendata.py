from django.core.management.base import BaseCommand
from application import utils


class Command(BaseCommand):
    help = 'Open data'

    def handle(self, *args, **kwargs):
        utils.opendata()

