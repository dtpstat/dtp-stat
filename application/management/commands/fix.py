from django.core.management.base import BaseCommand
from application import utils
from data import models
from data import utils as data_utils
import pandas as pd
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404

from tqdm import tqdm

class Command(BaseCommand):
    help = 'fix'

    def handle(self, *args, **kwargs):

        for dtp in tqdm(models.DTP.objects.all()):
            if dtp.dead:
                dtp.severity = get_object_or_404(models.Severity, level=4)
            else:
                severity_levels = [x.severity.level for x in dtp.participant_set.all() if
                                   x.severity and x.severity.level]
                if severity_levels:
                    dtp.severity = get_object_or_404(models.Severity, level=max(severity_levels))
                else:
                    dtp.severity = get_object_or_404(models.Severity, level=1)
            dtp.save()
