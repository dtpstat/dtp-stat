from django.core.management.base import BaseCommand
from data import utils


class Command(BaseCommand):
    help = 'Download regions'

    def handle(self, *args, **kwargs):
        utils.extra_filters_data()
        utils.load_regions()
        #TODO: use direct fixture loading instead of ./manage.py call
        #utils.crawl('regions')
        #utils.get_region_ya_names()