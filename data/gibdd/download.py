import datetime
import json
import os
import re
from datetime import datetime

import requests
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils import timezone
from lxml import html

from application import utils as app_utils
from data import models
from data.gibdd import conf
from data.gibdd.conf import log


def run():
    _sync_dates()
    _run_downloads()
    app_utils.mapdata()
    app_utils.opendata()


def _sync_dates():
    log.info('Обновляем отчетные даты с %s' % conf.STAT_URL)
    source_dates = []
    parsed_dates = []
    new_downloads = []

    if settings.PROXY_LIST:
        proxies = {'http': 'http://' + settings.PROXY_LIST[0]}
    else:
        proxies = None
    r = requests.get(conf.STAT_URL, proxies=proxies)
    r = html.fromstring(r.content.decode('UTF-8'))
    scripts = r.xpath('//script')

    for script in scripts:
        if script.text and "dateComboData" in script.text:
            string = script.text
            p = re.compile(r"dateComboData = (.*?);", re.MULTILINE)
            m = p.search(string)
            data = m.groups()[0]
            source_dates = json.loads(data)
            if source_dates:
                break
    if not source_dates:
        raise Warning('Не могу найти список дат на %s' % conf.STAT_URL)

    for year in source_dates:
        for month in year['nodes']:
            parsed_dates.append(datetime.strptime(month['value'].replace("MONTHS:", ""), '%m.%Y').date())
    if not parsed_dates:
        raise Warning('Не могу разобрать список дат на %s' % conf.STAT_URL)

    for region in models.Region.objects.filter(level=1):
        for date in parsed_dates:
            download_item, created = models.Download.objects.get_or_create(region=region, date=date)
            if created:
                new_downloads += [download_item]
    log.info('Добавлено %d новых загрузок' % len(new_downloads))


def _run_downloads():
    downloads = models.Download.objects.all()

    # первым делом проверяем наличие вообще не скаченных регионов за конкретные даты
    downloads_no_update = downloads.filter(last_update=None)
    if downloads_no_update.count() > 0:
        _regions_crawl(downloads_no_update, tags=False)

    # потом смотрим на архивные данные
    downloads_old_update = downloads.filter(last_update__lte=timezone.now() - datetime.timedelta(days=40))
    if downloads_old_update.count() > 0:
        _regions_crawl(downloads_old_update, tags=False)
    """
    # потом смотрим на теги
    downloads_no_tags = downloads.filter(last_tags_update=None)
    elif downloads_no_tags.count() > 0:
        region_crawl(downloads_no_tags, tags=True)
    """
    for download in downloads.filter(last_update__isnull=False):
        _check_deleted_dtp(download)


def _regions_crawl(downloads, tags=False):
    for region in models.Region.objects.filter(level=1):
        region_downloads = downloads.filter(region=region)

        if region_downloads:
            dates = map(lambda d: d.strftime('%m.%Y'),sorted(list(set([x['date'] for x in region_downloads.values("date")]))))
            _crawl("dtp", params={
                "tags": str(tags),
                "dates": ",".join(dates),
                "region_code": str(region.gibdd_code),
                "area_codes": ",".join([x.gibdd_code for x in region.region_set.all()])
            })


def _crawl(spider_name, params=None):
    first_dir = os.getcwd()
    os.chdir("data/parser")
    command = 'scrapy crawl ' + spider_name + ' --nolog'
    if params:
        for key, value in params.items():
            command += ' -a ' + key + "=" + value
    os.system(command)
    os.chdir(first_dir)


def _check_deleted_dtp(download):
    download_item_dtps = models.DTP.objects.filter(
        datetime__month=download.date.month,
        datetime__year=download.date.year,
        region__parent_region=download.region
    )

    download_item_dtps.filter(
        gibdd_latest_check__gt=download.last_update - datetime.timedelta(hours=1),
        status=False
    ).update(
        status=True
    )

    # download_item_dtps.filter(
    #     gibdd_latest_check__lt=download.last_update - datetime.timedelta(hours=1),
    #     status=True
    # ).update(status=False)


def mark_successful_downloads(dates, region_code, tags=False):
    region = get_object_or_404(models.Region, gibdd_code=region_code, level=1)

    for date in [datetime.datetime.strptime(x, '%m.%Y') for x in dates.split(",")]:
        download_item, created = models.Download.objects.get_or_create(
            region=region,
            date=date
        )
        download_item.last_update = timezone.now()
        if tags:
            download_item.last_tags_update = timezone.now()
        download_item.save()
