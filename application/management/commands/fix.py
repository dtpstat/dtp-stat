from django.core.management.base import BaseCommand
from application import utils


class Command(BaseCommand):
    help = 'fix'

    def handle(self, *args, **kwargs):
        utils.soc_risk()

