import datetime
import json
import logging
from ast import literal_eval

import scrapy
from datadog import statsd
from scrapy import signals
from scrapy.exceptions import CloseSpider
from scrapy.http.request import Request
from scrapy.spidermiddlewares.httperror import HttpError

from data import models, utils

log = logging.getLogger(__name__)


class DtpSpider(scrapy.Spider):
    name = "dtp"

    custom_settings = {
        'ITEM_PIPELINES': {'data.parser.dtp_parser.pipelines.DtpParserPipeline': 300},
        'CLOSESPIDER_TIMEOUT': 84000,
        'RETRY_HTTP_CODES': [502, 503, 504, 522, 524, 408, 429],
        'RETRY_TIMES': 10,
        "LOG_LEVEL": 'INFO',
        "CONCURRENT_ITEMS": 8,
        "CONCURRENT_REQUESTS": 8,
        "DOWNLOAD_TIMEOUT": 40
    }

    def start_requests(self):
        if self.tags == "True":
            tags = models.Tag.objects.filter(is_filter=False)
        else:
            tags = models.Tag.objects.filter(is_filter=True)

        for area_code in self.area_codes.split(','):
            for date in self.dates.split(","):
                for tag_code in [x.code for x in tags]:
                    payload = dict()
                    payload_data = '{"date": ["MONTHS:%s"], "ParReg": %s, "order": { "type":"1", "fieldName":"dat" }, "reg": %s, "ind": %s, "st": 1, "en": "10000",}' % (date, self.region_code, area_code, tag_code)
                    payload["data"] = payload_data
                    yield Request(
                        'http://stat.gibdd.ru/map/getDTPCardData',
                        method="POST",
                        meta={
                            "tag_code": tag_code,
                            "area_code": area_code,
                            "parent_code": self.region_code,
                            "date": date
                        },
                        body=json.dumps(payload),
                        headers={'Content-Type': 'application/json; charset=UTF-8'},
                        callback=self.parse_area,
                        errback=self.handle_error
                    )
        """
        for date in self.dates:
            for tag_code, tag_name in list(self.tags.items()):
                payload = dict()
                payload["data"] = '{"date":["MONTHS:' + date.strftime('%m.%Y') + '"],"ParReg":"' + self.area.parent_region.gibdd_code + '","order":{"type":"1","fieldName":"dat"},"reg":"' + self.area.gibdd_code + '","ind":"' + tag_code + '","st":"1","en":"10000"}'
                yield Request(
                    'http://stat.gibdd.ru/map/getDTPCardData',
                    method="POST",
                    meta={
                      "tag_name": tag_name,
                      "area_code": self.area.gibdd_code
                    },
                    body=json.dumps(payload),
                    headers={'Content-Type': 'application/json; charset=UTF-8'},
                    callback=self.parse_area,
                    errback=self.handle_error
                )
        """
    @statsd.timed('dtpstat.spider.parse_area')
    def parse_area(self, response):
        export = json.loads(response.body_as_unicode())
        if export['data']:
            export = literal_eval(export['data'])

            for dtp in export['tab']:
                export_dtp = dict(dtp)

                export_dtp['area_code'] = response.meta['area_code']
                export_dtp['parent_code'] = response.meta['parent_code']

                export_dtp['tag_code'] = response.meta['tag_code']
                yield export_dtp

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(DtpSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def handle_error(self, failure):
        if failure.check(HttpError):
            if failure.value.response.status in [500, 200]:
                return

        raise CloseSpider("failed")

    def spider_closed(self, reason):
        if reason == "finished":
            utils.download_success(self.dates, self.region_code, tags=True if self.tags == "True" else False)

