from django.core.management.base import BaseCommand

from data.gibdd import download


class Command(BaseCommand):
    help = 'Download dtp'

    def handle(self, *args, **kwargs):
        download.run()