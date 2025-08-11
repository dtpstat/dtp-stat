from django.db import models


class CurrencyPriceHistoryManager(models.Manager):
    def get_latest_price(self, currency):
        return self.get_queryset().filter(currency=currency).order_by('-datetime').first()