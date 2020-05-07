import scrapy
from scrapy.http.request import Request
from scrapy import signals
from scrapy.exceptions import CloseSpider
from scrapy.spidermiddlewares.httperror import HttpError

import json
from ast import literal_eval
import datetime
import re
from tqdm import tqdm


def dates_generator(year=None):
    if year:
        start = datetime.datetime(year, 1, 1)
        end = datetime.datetime(year, 12, 31)
    else:
        start = datetime.datetime(2015, 1, 1)
        end = datetime.datetime.now()

    dates_set = set()

    while start <= end:
        start += datetime.timedelta(days=1)
        dates_set.add(datetime.datetime(start.year, start.month, 1).strftime('%m.%Y'))

    return list(dates_set)


def get_regions(scripts):
    regions = []

    for script in scripts:
        if script.extract() and "downloadRegListData" in script.extract():
            string = script.extract()
            p = re.compile(r"downloadRegListData = (.*?);", re.MULTILINE)
            data = json.loads(p.search(string).groups()[0])
            for federal_district in data[0]["Nodes"]:
                for region in federal_district["Nodes"]:
                    regions.append(region)

    return regions


class DtpSpider(scrapy.Spider):
    name = "dtp"

    custom_settings = {
        'ITEM_PIPELINES': {
            'data.parser.dtp_parser.pipelines.DtpParserPipeline': 300
        },
    }

    def start_requests(self):
        for date in self.dates:
            #for tag_code, tag_name in list(self.tags.items()):
            for tag_code, tag_name in [("1","Тест")]:
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
    def parse(self, response):
        scripts = response.xpath('//script')

        tags = get_tags(scripts)
        regions = get_regions(scripts)

        for date in ['2.2020']:
            for tag, tag_name in list(tags.items()):
                for region in regions[0:1]:
                    region_name = region['Text'].replace("г.", "").replace("гор.", "").strip()

                    meta = {
                        "code": region['Value'],
                        "name": region_name,
                        "date": date,
                        "tag_name": tag_name,
                        "tag": tag
                    }

                    payload = {
                        "maptype": "1",
                        "region": region['Value'],
                        "pok": tag
                    }

                    yield Request(
                        url='http://stat.gibdd.ru/map/getMainMapData',
                        method="POST",
                        callback=self.parse_region,
                        meta=meta,
                        body=json.dumps(payload),
                        headers={'Content-Type': 'application/json; charset=UTF-8'}
                    )

                    print("lol")
    
    def parse_region(self, response):
        export = json.loads(response.body_as_unicode())['metabase']
        export = json.loads(literal_eval(export)[0]['maps'])

        for area in export:
            payload = dict()
            payload["data"] = '{"date":["MONTHS:' + '02.2020' + '"],"ParReg":"' + response.meta['code'] + '","order":{"type":"1","fieldName":"dat"},"reg":"' + area['id'] + '","ind":"' + response.meta['tag'] + '","st":"1","en":"10000"}'

            yield Request(
                url="http://stat.gibdd.ru/map/getDTPCardData",
                method="POST",
                meta={
                    "area_name": area['name'],
                    "area_code": area["id"],
                    "region_name": response.meta['name'],
                    "region_code": response.meta['code'],
                    "tag_name": response.meta['tag_name']
                },
                body=json.dumps(payload),
                headers={'Content-Type': 'application/json; charset=UTF-8'},
                callback=self.parse_area)
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
            self.area.actual_date = max(self.dates)
            print("УРА")
            #self.area.save()


