import django
django.setup()

from data import utils

import scrapy
from scrapy.http.request import Request
from scrapy import signals
from scrapy.exceptions import CloseSpider
from scrapy.spidermiddlewares.httperror import HttpError

import json
from ast import literal_eval


class DtpSpider(scrapy.Spider):
    name = "dtp"

    custom_settings = {
        'ITEM_PIPELINES': {'data.parser.dtp_parser.pipelines.DtpParserPipeline': 300},
        'CLOSESPIDER_TIMEOUT': 84000,
        'RETRY_HTTP_CODES': [502, 503, 504, 522, 524, 408, 429],
        'RETRY_TIMES': 10,
        "LOG_LEVEL": 'INFO',
        "DOWNLOAD_TIMEOUT": 40
    }

    def start_requests(self):
        tags = {"1":"Дорожно-транспортные происшествия"}

        for area_code in self.area_codes.split(','):
            for date in self.dates.split(","):
                for tag_code, tag_name in tags.items():
                    payload = dict()
                    payload["data"] = '{"date":["MONTHS:' + date + '"],"ParReg":"' + self.region_code + '","order":{"type":"1","fieldName":"dat"},"reg":"' + area_code + '","ind":"' + tag_code + '","st":"1","en":"10000"}'
                    yield Request(
                        'http://stat.gibdd.ru/map/getDTPCardData',
                        method="POST",
                        meta={
                            "tag_name": tag_name,
                            "area_code": area_code
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
    def parse_area(self, response):
        export = json.loads(response.body_as_unicode())
        if export['data']:
            export = literal_eval(export['data'])

            for dtp in export['tab']:
                export_dtp = dict(dtp)
                export_dtp['area_code'] = response.meta['area_code']
                export_dtp['tag'] = response.meta['tag_name']
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
            utils.download_success(self.dates, self.region_code)

