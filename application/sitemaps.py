from django.contrib.sitemaps import Sitemap

from data.models import DTP


class DTPSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5
    limit = 2000
    protocol = 'https'

    def items(self):
        return DTP.objects.filter(status=True)

    def lastmod(self, item):
        return item.modified_at
