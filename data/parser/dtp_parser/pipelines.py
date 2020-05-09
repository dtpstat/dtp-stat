import django
django.setup()

from data import utils


class DtpParserPipeline(object):
    def process_item(self, item, spider):
        utils.add_dtp_record(item)
        pass


class RegionParserPipeline(object):
    def process_item(self, item, spider):
        utils.get_region(
            item['area_gibdd_code'],
            item['area_name'],
            item['region_gibdd_code'],
            item['region_name'],
        )
        pass

