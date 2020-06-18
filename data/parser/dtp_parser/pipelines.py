import django
django.setup()

from data import utils

import traceback


class DtpParserPipeline(object):
    name = "dtp parser pipeline"

    def process_item(self, item, spider):
        try:
            utils.add_dtp_record(item)
        except:
            traceback.print_exc()
            spider.crawler.engine.close_spider(self, reason='failed')


class RegionParserPipeline(object):
    def process_item(self, item, spider):
        utils.get_region(
            item['area_gibdd_code'],
            item['area_name'],
            item['region_gibdd_code'],
            item['region_name'],
        )
        pass

