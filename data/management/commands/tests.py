from django.core.management.base import BaseCommand
from data import utils


class Command(BaseCommand):
    help = 'Test'

    def handle(self, *args, **kwargs):
        utils.generate_datasets()