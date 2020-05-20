from django.core.management.base import BaseCommand
from data import utils


class Command(BaseCommand):
    help = 'Download dtp'

    def add_arguments(self, parser):
        parser.add_argument('-t', '--tags', type=bool)

    def handle(self, *args, **kwargs):
        utils.check_dtp(tags=kwargs.get('tags'))