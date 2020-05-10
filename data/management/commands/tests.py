from django.core.management.base import BaseCommand
from data import utils
from data import models


class Command(BaseCommand):
    help = 'Test'

    def handle(self, *args, **kwargs):
        print([x['health_status'] for x in models.Participant.objects.all().values('health_status').distinct() if x['health_status']])