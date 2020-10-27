from django.core.management.base import BaseCommand
from application import utils
from data import models
from data import utils as data_utils
import pandas as pd
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404

from tqdm import tqdm
import json
import glob
import shutil



class Command(BaseCommand):
    help = 'fix'

    def handle(self, *args, **kwargs):
        import telegram
        import environ
        env = environ.Env()

        bot = telegram.Bot(token=env('TELEGRAM_TOKEN'))
        bot.send_message(48994754, text='test')
