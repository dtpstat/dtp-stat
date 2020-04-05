import django
django.setup()

from data import utils


class DtpParserPipeline(object):
    def process_item(self, item, spider):
        utils.add_dtp_record(item)
        pass
