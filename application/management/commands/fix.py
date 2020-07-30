from django.core.management.base import BaseCommand
from application import utils
from data import models
import pandas as pd

class Command(BaseCommand):
    help = 'fix'

    def handle(self, *args, **kwargs):
        data = models.DTP.objects.all()

        data = data.values('scheme').distinct()

        df = pd.DataFrame(data)
        df.to_csv('static/schemes.csv', index=False)

