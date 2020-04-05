from django.core.management.base import BaseCommand
from data import utils


class Command(BaseCommand):
    help = 'Download dtp'

    def handle(self, *args, **kwargs):
        utils.download()