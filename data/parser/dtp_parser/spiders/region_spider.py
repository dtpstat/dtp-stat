import scrapy
from scrapy.http.request import Request

import json
from ast import literal_eval
import re

import logging
logging.disable(10)

class RegionSpider(scrapy.Spider):
    name = "regions"

    start_urls = ['http://stat.gibdd.ru/']

    custom_settings = {
        'ITEM_PIPELINES': {'data.parser.dtp_parser.pipelines.RegionParserPipeline': 300},
        'CLOSESPIDER_TIMEOUT': 1000,
        'RETRY_HTTP_CODES': [502, 503, 504, 522, 524, 408, 429],
        "LOG_LEVEL": 'INFO',
    }

    def parse(self, response):
        # ищем скрипт с кодами регионов и выкачиваем их
        scripts = response.xpath('//script')

        for script in scripts:
            if script.extract() is not None and "downloadRegListData" in script.extract():
                string = script.extract()
                p = re.compile(r"downloadRegListData = (.*?);", re.MULTILINE)
                m = p.search(string)
                data = m.groups()[0]
                jdata = json.loads(data)
                for federal_district in jdata[0]["Nodes"]:
                    for region in federal_district["Nodes"]:
                        region_name = region['Text'].replace("г.", "").replace("гор.", "").strip()
                        region_data = {
                            "code": region['Value'],
                            "name": region_name
                        }
                        payload = {
                            "maptype": "1",
                            "region": region['Value'],
                            "pok": "1"
                        }
                        body = json.dumps(payload)
                        yield Request("http://stat.gibdd.ru/map/getMainMapData", method="POST",
                                      callback=self.parse_region, meta=region_data, body=body,
                                      headers={'Content-Type': 'application/json; charset=UTF-8'})

    def parse_region(self, response):
        export = json.loads(response.text)['metabase']
        export = json.loads(literal_eval(export)[0]['maps'])
        for area in export:
            Item = dict()
            Item['area_name'] = area["name"].replace("г.", "").replace("гор.", "").replace("ГО", "").strip()
            Item['area_gibdd_code'] = area["id"]
            Item['region_name'] = response.meta['name']
            Item['region_gibdd_code'] = response.meta['code']

            yield Item


