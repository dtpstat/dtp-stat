from datetime import date, timedelta
from decimal import Decimal
from typing import List

from django.db import models
from django.db.models import Q

from donations.constants import SUBSCRIPTION_THRESHOLD_DAYS


class DonationManager(models.Manager):
    def confirmed(self):
        """Returns a queryset of all confirmed donations."""
        return self.get_queryset().filter(is_confirmed=True)

    def total_donated_in_range(self, start_date: date, end_date: date) -> Decimal:
        """Calculates the total confirmed donations within a given date range."""
        total = self.confirmed().filter(
            donation_datetime__date__gte=start_date,
            donation_datetime__date__lte=end_date
        ).aggregate(total=models.Sum('amount_in_base_currency'))['total']
        return Decimal(total) if total else Decimal('0.00')

    def find_donations_by_contact_amount_currency_and_dates(
            self, *,
            contact: 'Contact',
            amount: 'Decimal',
            currency: 'Currency',
            dates: List[date],
            threshold: int = None,
    ) -> 'QuerySet':
        """Returns a queryset of donations with the given amount, currency, and dates."""
        if threshold is None:
            threshold = SUBSCRIPTION_THRESHOLD_DAYS
        query = Q()
        for _date in dates:
            query |= Q(donation_datetime__date__range=(_date, _date + timedelta(days=threshold)))
        return self.confirmed().filter(
            contact=contact,
            amount=amount,
            currency=currency,
        ).filter(
            query
        )