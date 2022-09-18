from django.core.management.base import BaseCommand
from django.db import connection
from data.models import DTP


class Command(BaseCommand):
    help = 'Remove duplicated dtps'

    def add_arguments(self, parser):
        parser.add_argument(
            '--delete',
            action='store_true',
            help='Delete found duplicates',
        )

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            cursor.execute("select dtp.id FROM data_dtp dtp join data_dtp d2 ON  dtp.gibdd_slug = d2.gibdd_slug and dtp.id > d2.id")
            ids = cursor.fetchall()
        pks = [id[0] for id in ids]
        print('Найдено %d дубликатов' % len(pks))
        if options['delete']:
            cnt = DTP.objects.filter(pk__in=pks).delete()
            if cnt[0] > 0 :
                print('Удалено %d повторных ДТП' % cnt[1]['data.DTP'])
