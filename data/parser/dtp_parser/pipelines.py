import logging

import django

django.setup()

from data import utils
import data.gibdd.process as p


class DtpParserPipeline(object):
    name = "dtp parser pipeline"

    def process_item(self, item, spider):
        try:
            p.add_dtp_record(item)
        except Exception as e:
            spider.log(e, logging.ERROR)


class RegionParserPipeline(object):
    def process_item(self, item, spider):
        utils.get_region(
            item['area_gibdd_code'],
            item['area_name'],
            item['region_gibdd_code'],
            item['region_name'],
        )